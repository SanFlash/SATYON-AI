"""
Search Engine - Core Aggregator
Orchestrates parallel searches across all sources
and combines results into a unified response
"""
import asyncio
from query_classifier import classify_query, detect_intent
from api_clients.google_api import search_google
from api_clients.wikipedia_api import search_wikipedia
from api_clients.stackoverflow_api import search_stackoverflow
from api_clients.github_api import search_github
from api_clients.kaggle_api import search_kaggle
from api_clients.arxiv_api import search_arxiv
from api_clients.youtube_api import search_youtube


# Source function mapping
SOURCE_FUNCTIONS = {
    "google": search_google,
    "wikipedia": search_wikipedia,
    "stackoverflow": search_stackoverflow,
    "github": search_github,
    "kaggle": search_kaggle,
    "arxiv": search_arxiv,
    "youtube": search_youtube,
}


async def search_all_sources(query: str, sources: list = None) -> dict:
    """
    Search across all specified sources in parallel.
    
    Args:
        query: User's search query
        sources: Optional list of sources to search. If None, auto-detect.
    
    Returns:
        dict with classification info and results per source
    """
    # Classify the query
    classification = classify_query(query)
    intent = detect_intent(query)
    
    # Determine which sources to use
    if sources:
        active_sources = sources
    else:
        active_sources = classification["sources"]
    
    # Create search tasks for parallel execution
    tasks = {}
    for source in active_sources:
        if source in SOURCE_FUNCTIONS:
            tasks[source] = SOURCE_FUNCTIONS[source](query)
    
    # Execute all searches in parallel
    source_names = list(tasks.keys())
    results_list = await asyncio.gather(*tasks.values(), return_exceptions=True)
    
    # Organize results by source
    all_results = {}
    combined_results = []
    total_count = 0
    
    for i, source_name in enumerate(source_names):
        result = results_list[i]
        if isinstance(result, Exception):
            print(f"Error from {source_name}: {result}")
            all_results[source_name] = []
        else:
            all_results[source_name] = result
            combined_results.extend(result)
            total_count += len(result)
    
    # Sort combined results by relevance (simple scoring)
    combined_results = _score_and_sort(combined_results, query)
    
    return {
        "query": query,
        "classification": classification,
        "intent": intent,
        "sources_searched": source_names,
        "total_results": total_count,
        "results_by_source": all_results,
        "combined_results": combined_results,
    }


async def search_single_source(query: str, source: str) -> list:
    """Search a single specific source"""
    if source in SOURCE_FUNCTIONS:
        try:
            return await SOURCE_FUNCTIONS[source](query)
        except Exception as e:
            print(f"Error searching {source}: {e}")
            return []
    return []


def _score_and_sort(results: list, query: str) -> list:
    """Score and sort results by relevance to the query"""
    query_words = set(query.lower().split())
    
    for result in results:
        score = 0
        title_lower = result.get("title", "").lower()
        snippet_lower = result.get("snippet", "").lower()
        
        # Title match scoring
        for word in query_words:
            if word in title_lower:
                score += 3
            if word in snippet_lower:
                score += 1
        
        # Source priority scoring
        source_priority = {
            "google": 2,
            "stackoverflow": 3,
            "github": 2,
            "wikipedia": 2,
            "arxiv": 1,
            "kaggle": 1,
            "youtube": 1,
        }
        score += source_priority.get(result.get("source", ""), 0)
        
        # Extra data scoring (stars, votes, etc.)
        extra = result.get("extra", {})
        if extra.get("stars", 0) > 1000:
            score += 2
        if extra.get("score", 0) > 10:
            score += 2
        if extra.get("is_answered"):
            score += 1
        
        result["relevance_score"] = score
    
    results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return results


def get_available_sources() -> list:
    """Return list of available search sources with metadata"""
    return [
        {"id": "google", "name": "Google", "icon": "🔍", "description": "Web search results"},
        {"id": "wikipedia", "name": "Wikipedia", "icon": "📚", "description": "Encyclopedia articles"},
        {"id": "stackoverflow", "name": "Stack Overflow", "icon": "💬", "description": "Programming Q&A"},
        {"id": "github", "name": "GitHub", "icon": "🐙", "description": "Code repositories"},
        {"id": "kaggle", "name": "Kaggle", "icon": "📊", "description": "Datasets & notebooks"},
        {"id": "arxiv", "name": "ArXiv", "icon": "📄", "description": "Research papers"},
        {"id": "youtube", "name": "YouTube", "icon": "🎥", "description": "Video tutorials"},
    ]
