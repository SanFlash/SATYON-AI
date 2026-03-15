"""
AI Summarizer
Sends aggregated search results to AI models for intelligent summarization
Supports OpenAI and DeepSeek APIs
"""
import aiohttp
import json
from config import OPENAI_API_KEY, DEEPSEEK_API_KEY, AI_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE


async def summarize_results(query: str, results: list, classification: dict = None, intent: dict = None) -> dict:
    """
    Summarize search results using AI.
    
    Args:
        query: Original user query
        results: List of search result dicts
        classification: Query classification info
        intent: Query intent info
    
    Returns:
        dict with 'summary', 'key_insights', 'recommendations'
    """
    # Build context from results
    context = _build_context(results)
    
    # Build the prompt
    prompt = _build_prompt(query, context, classification, intent)
    
    # Try OpenAI first, then DeepSeek, then fallback
    summary = None
    
    if OPENAI_API_KEY:
        summary = await _call_openai(prompt)
    
    if not summary and DEEPSEEK_API_KEY:
        summary = await _call_deepseek(prompt)
    
    if not summary:
        summary = _generate_fallback_summary(query, results, classification)
    
    return summary


def _build_context(results: list) -> str:
    """Build a context string from search results"""
    context_parts = []
    
    for i, result in enumerate(results[:15], 1):
        source = result.get("source", "unknown").upper()
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        url = result.get("url", "")
        
        context_parts.append(
            f"[{i}] [{source}] {title}\n"
            f"    {snippet}\n"
            f"    URL: {url}"
        )
    
    return "\n\n".join(context_parts)


def _build_prompt(query: str, context: str, classification: dict = None, intent: dict = None) -> str:
    """Build the AI prompt for summarization"""
    category = classification.get("category", "general") if classification else "general"
    user_intent = intent.get("intent", "explore") if intent else "explore"
    
    prompt = f"""You are SATYON-AI, an intelligent search aggregation assistant. 
A user searched for: "{query}"

Query Category: {category}
User Intent: {user_intent}

Here are the search results from multiple sources:

{context}

Please provide a comprehensive, well-structured response that:
1. **Summary**: A clear, concise summary answering the user's query (2-3 paragraphs)
2. **Key Insights**: 3-5 bullet points of the most important findings
3. **Recommendations**: 2-3 specific recommendations or next steps

Format your response as JSON with these keys:
- "summary": string (the main summary in markdown format)
- "key_insights": list of strings
- "recommendations": list of strings  
- "reasoning_steps": list of strings (3-5 steps showing the thought process)
- "confidence": float (0-1, how confident you are in the answer)

Important:
- Synthesize information from ALL sources, don't just repeat individual results
- If results are from code platforms, include relevant code concepts
- If results include datasets, mention dataset availability
- If results include research papers, summarize key findings
- Use markdown formatting in the summary for readability
- The reasoning_steps should explain how you verified info or connected sources
"""
    return prompt


async def _call_openai(prompt: str) -> dict:
    """Call OpenAI API for summarization"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": AI_MODEL,
            "messages": [
                {"role": "system", "content": "You are SATYON-AI, an intelligent search aggregation assistant. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": AI_MAX_TOKENS,
            "temperature": AI_TEMPERATURE,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    # Try to parse as JSON
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        # Clean up potential markdown code blocks
                        content = content.strip()
                        if content.startswith("```"):
                            content = content.split("\n", 1)[1]
                        if content.endswith("```"):
                            content = content[:-3]
                        try:
                            return json.loads(content.strip())
                        except:
                            return {
                                "summary": content,
                                "key_insights": [],
                                "recommendations": [],
                                "confidence": 0.5,
                            }
                else:
                    error_text = await response.text()
                    print(f"OpenAI API Error ({response.status}): {error_text}")
                    return None
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return None


async def _call_deepseek(prompt: str) -> dict:
    """Call DeepSeek API for summarization"""
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are SATYON-AI, an intelligent search aggregation assistant. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": AI_MAX_TOKENS,
            "temperature": AI_TEMPERATURE,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        content = content.strip()
                        if content.startswith("```"):
                            content = content.split("\n", 1)[1]
                        if content.endswith("```"):
                            content = content[:-3]
                        try:
                            return json.loads(content.strip())
                        except:
                            return {
                                "summary": content,
                                "key_insights": [],
                                "recommendations": [],
                                "confidence": 0.5,
                            }
                else:
                    return None
    except Exception as e:
        print(f"DeepSeek API Error: {e}")
        return None


def _generate_fallback_summary(query: str, results: list, classification: dict = None) -> dict:
    """Generate a summary without AI when no API keys are available"""
    category = classification.get("category", "general") if classification else "general"
    sources_found = set()
    titles = []
    
    for r in results[:10]:
        sources_found.add(r.get("source", "unknown"))
        titles.append(r.get("title", ""))
    
    sources_str = ", ".join(s.capitalize() for s in sources_found)
    
    # Build a structured summary from the results
    summary_parts = [f"## Search Results for: \"{query}\"\n"]
    summary_parts.append(f"Found **{len(results)} results** across **{len(sources_found)} sources** ({sources_str}).\n")
    
    # Group by source
    by_source = {}
    for r in results[:15]:
        src = r.get("source", "unknown")
        if src not in by_source:
            by_source[src] = []
        by_source[src].append(r)
    
    for src, items in by_source.items():
        summary_parts.append(f"\n### From {src.capitalize()}:")
        for item in items[:3]:
            summary_parts.append(f"- **{item.get('title', '')}**: {item.get('snippet', '')[:150]}")
    
    key_insights = [
        f"Query classified as '{category}' category",
        f"Found results from {len(sources_found)} different sources",
        f"Total of {len(results)} relevant results aggregated",
    ]
    
    reasoning_steps = [
        f"Step 1: Analyzed search query for '{category}' intent",
        f"Step 2: Scanned results from {sources_str}",
        f"Step 3: Aggregated key data points from top {min(len(results), 5)} results",
        "Step 4: Synthesized cross-platform information for comprehensive view"
    ]
    
    recommendations = [
        "Review the individual source tabs for detailed results",
        "Click on result links to access full content",
        f"Try refining your search for more specific {category} results",
    ]
    
    return {
        "summary": "\n".join(summary_parts),
        "key_insights": key_insights[:5],
        "reasoning_steps": reasoning_steps,
        "recommendations": recommendations,
        "confidence": 0.6,
        "ai_powered": False,
    }
