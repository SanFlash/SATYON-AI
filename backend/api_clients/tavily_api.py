"""
Tavily Search API Client
Uses Tavily for web search results
Falls back to demo results if no API key is set
"""
import aiohttp
from config import TAVILY_API_KEY, MAX_RESULTS_PER_SOURCE, SEARCH_TIMEOUT


async def search_tavily(query: str, num_results: int = None) -> list:
    """Search the web via Tavily API"""
    if num_results is None:
        num_results = MAX_RESULTS_PER_SOURCE

    results = []

    if not TAVILY_API_KEY:
        # Return demo results when no API key
        return _get_demo_results(query)

    try:
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "max_results": num_results,
            "include_answer": False,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.tavily.com/search",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=SEARCH_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data.get("results", [])[:num_results]:
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "snippet": item.get("content", ""),
                            "source": "tavily",
                            "source_icon": "🔎",
                        })
    except Exception as e:
        print(f"Tavily Search Error: {e}")
        results = _get_demo_results(query)

    return results


def _get_demo_results(query: str) -> list:
    """Return demo results for development/demo purposes"""
    return [
        {
            "title": f"Tavily: {query} - Overview & Guide",
            "url": f"https://www.google.com/search?q={query.replace(' ', '+')}",
            "snippet": f"Comprehensive overview of {query}. Find detailed information, tutorials, and resources related to your search.",
            "source": "tavily",
            "source_icon": "🔎",
        },
        {
            "title": f"Understanding {query} - Complete Tutorial",
            "url": f"https://www.google.com/search?q={query.replace(' ', '+')}+tutorial",
            "snippet": f"Learn everything about {query} with step-by-step tutorials, examples, and best practices from industry experts.",
            "source": "tavily",
            "source_icon": "🔎",
        },
        {
            "title": f"{query} - Latest News & Updates",
            "url": f"https://www.google.com/search?q={query.replace(' ', '+')}+news",
            "snippet": f"Stay updated with the latest developments, news, and trends related to {query}.",
            "source": "tavily",
            "source_icon": "🔎",
        },
    ]
