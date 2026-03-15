"""
GitHub API Client
Uses GitHub REST API - works without token but rate-limited
With token: 5000 requests/hour; Without: 60 requests/hour
"""
import aiohttp
from config import GITHUB_TOKEN, MAX_RESULTS_PER_SOURCE, SEARCH_TIMEOUT


async def search_github(query: str, num_results: int = None) -> list:
    """Search GitHub repositories"""
    if num_results is None:
        num_results = MAX_RESULTS_PER_SOURCE

    results = []

    try:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"

        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": num_results,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/search/repositories",
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=SEARCH_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])
                    for item in items[:num_results]:
                        lang = item.get("language", "Unknown")
                        stars = item.get("stargazers_count", 0)
                        desc = item.get("description", "") or "No description"
                        results.append({
                            "title": item.get("full_name", ""),
                            "url": item.get("html_url", ""),
                            "snippet": f"⭐ {stars:,} | 🔤 {lang} | {desc[:200]}",
                            "source": "github",
                            "source_icon": "🐙",
                            "extra": {
                                "stars": stars,
                                "language": lang,
                                "forks": item.get("forks_count", 0),
                                "description": desc,
                                "topics": item.get("topics", []),
                                "updated_at": item.get("updated_at", ""),
                            }
                        })
    except Exception as e:
        print(f"GitHub Search Error: {e}")

    return results


async def search_github_code(query: str, num_results: int = 3) -> list:
    """Search GitHub code (requires authentication)"""
    if not GITHUB_TOKEN:
        return []

    results = []

    try:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {GITHUB_TOKEN}",
        }
        params = {
            "q": query,
            "per_page": num_results,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/search/code",
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=SEARCH_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])
                    for item in items[:num_results]:
                        repo = item.get("repository", {})
                        results.append({
                            "title": f"{repo.get('full_name', '')} / {item.get('name', '')}",
                            "url": item.get("html_url", ""),
                            "snippet": f"Code file: {item.get('path', '')} in {repo.get('full_name', '')}",
                            "source": "github",
                            "source_icon": "🐙",
                        })
    except Exception as e:
        print(f"GitHub Code Search Error: {e}")

    return results
