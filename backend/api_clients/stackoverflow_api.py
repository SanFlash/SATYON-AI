"""
StackOverflow API Client
Uses the free StackExchange API - no API key required for basic usage
"""
import aiohttp
from config import MAX_RESULTS_PER_SOURCE, SEARCH_TIMEOUT


async def search_stackoverflow(query: str, num_results: int = None) -> list:
    """Search StackOverflow for relevant questions and answers"""
    if num_results is None:
        num_results = MAX_RESULTS_PER_SOURCE

    results = []

    try:
        params = {
            "order": "desc",
            "sort": "relevance",
            "intitle": query,
            "site": "stackoverflow",
            "pagesize": num_results,
            "filter": "default",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.stackexchange.com/2.3/search/advanced",
                params=params,
                timeout=aiohttp.ClientTimeout(total=SEARCH_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])
                    for item in items[:num_results]:
                        tags = item.get("tags", [])
                        tag_str = ", ".join(tags[:4]) if tags else ""
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": f"Score: {item.get('score', 0)} | Answers: {item.get('answer_count', 0)} | Tags: {tag_str}",
                            "source": "stackoverflow",
                            "source_icon": "💬",
                            "extra": {
                                "score": item.get("score", 0),
                                "answer_count": item.get("answer_count", 0),
                                "is_answered": item.get("is_answered", False),
                                "tags": tags,
                                "view_count": item.get("view_count", 0),
                            }
                        })
    except Exception as e:
        print(f"StackOverflow Search Error: {e}")

    return results
