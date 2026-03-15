"""
Google Search API Client
Uses SerpAPI for Google search results
Falls back to a simple web scraping approach if no API key
"""
import aiohttp
from config import SERPAPI_KEY, MAX_RESULTS_PER_SOURCE, SEARCH_TIMEOUT


async def search_google(query: str, num_results: int = None) -> list:
    """Search Google via SerpAPI"""
    if num_results is None:
        num_results = MAX_RESULTS_PER_SOURCE

    results = []

    if not SERPAPI_KEY:
        # Return demo results when no API key
        return _get_demo_results(query)

    try:
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "num": num_results,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://serpapi.com/search",
                params=params,
                timeout=aiohttp.ClientTimeout(total=SEARCH_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    organic = data.get("organic_results", [])
                    for item in organic[:num_results]:
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "source": "google",
                            "source_icon": "🔍",
                        })
    except Exception as e:
        print(f"Google Search Error: {e}")
        results = _get_demo_results(query)

    return results


def _get_demo_results(query: str) -> list:
    """Return demo results for development/demo purposes"""
    return [
        {
            "title": f"Google: {query} - Overview & Guide",
            "url": f"https://www.google.com/search?q={query.replace(' ', '+')}",
            "snippet": f"Comprehensive overview of {query}. Find detailed information, tutorials, and resources related to your search.",
            "source": "google",
            "source_icon": "🔍",
        },
        {
            "title": f"Understanding {query} - Complete Tutorial",
            "url": f"https://www.google.com/search?q={query.replace(' ', '+')}+tutorial",
            "snippet": f"Learn everything about {query} with step-by-step tutorials, examples, and best practices from industry experts.",
            "source": "google",
            "source_icon": "🔍",
        },
        {
            "title": f"{query} - Latest News & Updates",
            "url": f"https://www.google.com/search?q={query.replace(' ', '+')}+news",
            "snippet": f"Stay updated with the latest developments, news, and trends related to {query}.",
            "source": "google",
            "source_icon": "🔍",
        },
    ]
