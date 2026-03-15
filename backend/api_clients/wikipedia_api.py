"""
Wikipedia API Client
Uses the free MediaWiki API - no API key required
"""
import aiohttp
from config import MAX_RESULTS_PER_SOURCE, SEARCH_TIMEOUT


async def search_wikipedia(query: str, num_results: int = None) -> list:
    """Search Wikipedia for relevant articles"""
    if num_results is None:
        num_results = MAX_RESULTS_PER_SOURCE

    results = []

    try:
        # Use Wikipedia's opensearch API
        params = {
            "action": "opensearch",
            "search": query,
            "limit": num_results,
            "namespace": 0,
            "format": "json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://en.wikipedia.org/w/api.php",
                params=params,
                timeout=aiohttp.ClientTimeout(total=SEARCH_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # OpenSearch returns [query, [titles], [descriptions], [urls]]
                    if len(data) >= 4:
                        titles = data[1]
                        descriptions = data[2]
                        urls = data[3]
                        for i in range(min(len(titles), num_results)):
                            results.append({
                                "title": titles[i],
                                "url": urls[i],
                                "snippet": descriptions[i] if descriptions[i] else f"Wikipedia article about {titles[i]}",
                                "source": "wikipedia",
                                "source_icon": "📚",
                            })

        # If we got results, also fetch extracts for better snippets
        if results:
            await _enrich_with_extracts(results)

    except Exception as e:
        print(f"Wikipedia Search Error: {e}")

    return results


async def _enrich_with_extracts(results: list):
    """Enrich results with article extracts for better snippets"""
    try:
        titles = "|".join([r["title"] for r in results[:3]])
        params = {
            "action": "query",
            "titles": titles,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "exsentences": 3,
            "format": "json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://en.wikipedia.org/w/api.php",
                params=params,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    pages = data.get("query", {}).get("pages", {})
                    for page_id, page_data in pages.items():
                        extract = page_data.get("extract", "")
                        title = page_data.get("title", "")
                        if extract:
                            for r in results:
                                if r["title"] == title:
                                    r["snippet"] = extract[:300] + "..." if len(extract) > 300 else extract
    except Exception:
        pass
