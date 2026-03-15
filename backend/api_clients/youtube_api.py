"""
YouTube API Client
Uses YouTube Data API v3 for video search
Falls back to demo results if no API key
"""
import aiohttp
from config import YOUTUBE_API_KEY, MAX_RESULTS_PER_SOURCE, SEARCH_TIMEOUT


async def search_youtube(query: str, num_results: int = None) -> list:
    """Search YouTube for relevant videos"""
    if num_results is None:
        num_results = MAX_RESULTS_PER_SOURCE

    results = []

    if not YOUTUBE_API_KEY:
        return _get_demo_results(query)

    try:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": num_results,
            "key": YOUTUBE_API_KEY,
            "order": "relevance",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.googleapis.com/youtube/v3/search",
                params=params,
                timeout=aiohttp.ClientTimeout(total=SEARCH_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])
                    for item in items[:num_results]:
                        snippet = item.get("snippet", {})
                        video_id = item.get("id", {}).get("videoId", "")
                        results.append({
                            "title": snippet.get("title", ""),
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "snippet": snippet.get("description", "")[:200],
                            "source": "youtube",
                            "source_icon": "🎥",
                            "extra": {
                                "channel": snippet.get("channelTitle", ""),
                                "published": snippet.get("publishedAt", "")[:10],
                                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                            }
                        })
    except Exception as e:
        print(f"YouTube Search Error: {e}")
        results = _get_demo_results(query)

    return results


def _get_demo_results(query: str) -> list:
    """Return demo YouTube results"""
    return [
        {
            "title": f"{query} - Complete Tutorial & Guide",
            "url": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
            "snippet": f"Watch comprehensive video tutorials about {query}. Learn from top creators and experts.",
            "source": "youtube",
            "source_icon": "🎥",
        },
        {
            "title": f"Learn {query} in 2024 - Full Course",
            "url": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}+tutorial",
            "snippet": f"Full course video covering {query} from beginner to advanced levels.",
            "source": "youtube",
            "source_icon": "🎥",
        },
    ]
