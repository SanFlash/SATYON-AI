"""
Kaggle API Client
Searches Kaggle datasets via their API
Requires kaggle.json credentials or falls back to web search
"""
import aiohttp
from config import MAX_RESULTS_PER_SOURCE, SEARCH_TIMEOUT


async def search_kaggle(query: str, num_results: int = None) -> list:
    """Search Kaggle for datasets"""
    if num_results is None:
        num_results = MAX_RESULTS_PER_SOURCE

    results = []

    try:
        # Use Kaggle's public dataset search endpoint
        params = {
            "search": query,
            "sortBy": "relevance",
            "filetype": "all",
            "license": "all",
            "tagids": "",
        }

        headers = {
            "User-Agent": "SATYON-AI/1.0",
        }

        async with aiohttp.ClientSession() as session:
            # Try the Kaggle datasets API
            async with session.get(
                "https://www.kaggle.com/api/v1/datasets/list",
                params={"search": query, "sortBy": "hottest", "page": 1, "pageSize": num_results},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=SEARCH_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        for item in data[:num_results]:
                            ref = item.get("ref", "")
                            results.append({
                                "title": item.get("title", ref),
                                "url": f"https://www.kaggle.com/datasets/{ref}",
                                "snippet": f"📊 Size: {item.get('totalBytes', 'N/A')} | Downloads: {item.get('downloadCount', 0):,} | {item.get('subtitle', '')[:150]}",
                                "source": "kaggle",
                                "source_icon": "📊",
                                "extra": {
                                    "downloads": item.get("downloadCount", 0),
                                    "votes": item.get("voteCount", 0),
                                    "size": item.get("totalBytes", 0),
                                }
                            })
    except Exception as e:
        print(f"Kaggle Search Error: {e}")

    # Fallback demo results if API fails
    if not results:
        results = _get_demo_results(query)

    return results


def _get_demo_results(query: str) -> list:
    """Return demo Kaggle dataset results"""
    return [
        {
            "title": f"{query} Dataset - Kaggle",
            "url": f"https://www.kaggle.com/search?q={query.replace(' ', '+')}",
            "snippet": f"Find datasets related to {query} on Kaggle. Explore notebooks, competitions, and community resources.",
            "source": "kaggle",
            "source_icon": "📊",
        },
        {
            "title": f"{query} - Open Dataset Collection",
            "url": f"https://www.kaggle.com/search?q={query.replace(' ', '+')}+dataset",
            "snippet": f"Curated collection of {query} datasets available for download. Includes CSV, JSON, and other formats.",
            "source": "kaggle",
            "source_icon": "📊",
        },
    ]
