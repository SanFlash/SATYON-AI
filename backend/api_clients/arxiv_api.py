"""
ArXiv API Client
Uses the free ArXiv API - no API key required
Great for research papers and academic content
"""
import aiohttp
import xml.etree.ElementTree as ET
from config import MAX_RESULTS_PER_SOURCE, SEARCH_TIMEOUT


async def search_arxiv(query: str, num_results: int = None) -> list:
    """Search ArXiv for research papers"""
    if num_results is None:
        num_results = MAX_RESULTS_PER_SOURCE

    results = []

    try:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": num_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://export.arxiv.org/api/query",
                params=params,
                timeout=aiohttp.ClientTimeout(total=SEARCH_TIMEOUT)
            ) as response:
                if response.status == 200:
                    text = await response.text()
                    results = _parse_arxiv_xml(text, num_results)
    except Exception as e:
        print(f"ArXiv Search Error: {e}")

    return results


def _parse_arxiv_xml(xml_text: str, num_results: int) -> list:
    """Parse ArXiv Atom XML response"""
    results = []
    try:
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        entries = root.findall("atom:entry", ns)
        for entry in entries[:num_results]:
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            link = entry.find("atom:id", ns)
            published = entry.find("atom:published", ns)

            # Get authors
            authors = entry.findall("atom:author/atom:name", ns)
            author_names = [a.text for a in authors[:3]] if authors else []
            author_str = ", ".join(author_names)
            if len(authors) > 3:
                author_str += f" et al. ({len(authors)} authors)"

            title_text = title.text.strip().replace("\n", " ") if title is not None and title.text else "Untitled"
            summary_text = summary.text.strip().replace("\n", " ")[:250] + "..." if summary is not None and summary.text else ""
            link_text = link.text.strip() if link is not None and link.text else ""
            pub_date = published.text[:10] if published is not None and published.text else ""

            # Convert arxiv ID URL to abstract URL
            url = link_text.replace("http://arxiv.org/abs/", "https://arxiv.org/abs/")

            results.append({
                "title": title_text,
                "url": url,
                "snippet": f"📅 {pub_date} | 👤 {author_str} | {summary_text}",
                "source": "arxiv",
                "source_icon": "📄",
                "extra": {
                    "authors": author_names,
                    "published": pub_date,
                    "abstract": summary_text,
                }
            })
    except Exception as e:
        print(f"ArXiv XML Parse Error: {e}")

    return results
