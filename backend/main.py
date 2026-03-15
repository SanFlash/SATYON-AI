"""
SATYON-AI - Multi-Source AI Search Aggregator
FastAPI Backend Server

Main entry point for the application.
Serves the API endpoints and static frontend files.
"""
import os
import sys
import time
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from search_engine import search_all_sources, search_single_source, get_available_sources
from ai_summarizer import summarize_results
from query_classifier import classify_query, detect_intent
from utils.helpers import cache_get, cache_set, make_cache_key
from config import HOST, PORT, DEBUG

# ─────────────────────────────────────────────
# App Initialization
# ─────────────────────────────────────────────
app = FastAPI(
    title="SATYON-AI",
    description="Multi-Source AI Search Aggregator - One Search, One Answer, Multiple Sources",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")


# ─────────────────────────────────────────────
# Frontend Routes
# ─────────────────────────────────────────────
@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        {"message": "SATYON-AI API is running. Frontend not found."},
        status_code=200
    )


# ─────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────
@app.get("/api/search")
async def api_search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    sources: str = Query(None, description="Comma-separated source names (e.g., 'google,github,arxiv')"),
    summarize: bool = Query(True, description="Whether to generate AI summary"),
):
    """
    Main search endpoint.
    Searches across multiple sources and optionally generates an AI summary.
    """
    start_time = time.time()
    
    # Parse sources
    source_list = None
    if sources:
        source_list = [s.strip().lower() for s in sources.split(",") if s.strip()]
    
    # Check cache
    cache_key = make_cache_key(q, source_list)
    cached = cache_get(cache_key)
    if cached:
        cached["cached"] = True
        return JSONResponse(cached)
    
    try:
        # Perform search
        search_results = await search_all_sources(q, source_list)
        
        # Generate AI summary if requested
        ai_summary = None
        if summarize and search_results["combined_results"]:
            ai_summary = await summarize_results(
                q,
                search_results["combined_results"],
                search_results["classification"],
                search_results["intent"],
            )
        
        # Build response
        elapsed = round(time.time() - start_time, 2)
        response = {
            "success": True,
            "query": q,
            "elapsed_seconds": elapsed,
            "classification": search_results["classification"],
            "intent": search_results["intent"],
            "sources_searched": search_results["sources_searched"],
            "total_results": search_results["total_results"],
            "ai_summary": ai_summary,
            "results_by_source": search_results["results_by_source"],
            "combined_results": search_results["combined_results"],
            "cached": False,
        }
        
        # Cache the response
        cache_set(cache_key, response)
        
        return JSONResponse(response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.get("/api/search/{source}")
async def api_search_source(
    source: str,
    q: str = Query(..., min_length=1, max_length=500),
):
    """Search a specific source only"""
    start_time = time.time()
    
    try:
        results = await search_single_source(q, source)
        elapsed = round(time.time() - start_time, 2)
        
        return JSONResponse({
            "success": True,
            "query": q,
            "source": source,
            "elapsed_seconds": elapsed,
            "total_results": len(results),
            "results": results,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.get("/api/classify")
async def api_classify(
    q: str = Query(..., min_length=1, max_length=500),
):
    """Classify a query and return category, sources, and intent"""
    classification = classify_query(q)
    intent = detect_intent(q)
    
    return JSONResponse({
        "query": q,
        "classification": classification,
        "intent": intent,
    })


@app.get("/api/sources")
async def api_sources():
    """Get list of available search sources"""
    return JSONResponse({
        "sources": get_available_sources()
    })


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "service": "SATYON-AI",
        "version": "1.0.0",
    })


# ─────────────────────────────────────────────
# Run Server
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  SATYON-AI - Multi-Source AI Search Aggregator")
    print("=" * 50)
    print(f"  Server: http://localhost:{PORT}")
    print(f"  API Docs: http://localhost:{PORT}/docs")
    print("=" * 50 + "\n")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
    )
