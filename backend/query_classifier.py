"""
Query Classifier
Uses keyword-based NLP to classify queries into categories
and determine which sources to search
"""
import re


# Category keywords mapping
CATEGORY_KEYWORDS = {
    "dataset": [
        "dataset", "data set", "data", "csv", "training data", "test data",
        "kaggle", "database", "corpus", "benchmark", "labeled data",
        "data collection", "open data", "public data"
    ],
    "code": [
        "code", "implement", "function", "class", "algorithm", "library",
        "package", "module", "api", "sdk", "framework", "programming",
        "syntax", "error", "bug", "debug", "compile", "runtime",
        "python", "javascript", "java", "c++", "rust", "golang",
        "typescript", "react", "angular", "vue", "django", "flask",
        "nodejs", "npm", "pip", "how to code", "code example"
    ],
    "research": [
        "research", "paper", "study", "journal", "academic", "thesis",
        "arxiv", "ieee", "acm", "conference", "publication", "citation",
        "survey", "review paper", "state of the art", "sota",
        "methodology", "experiment", "hypothesis"
    ],
    "tutorial": [
        "tutorial", "how to", "guide", "learn", "beginner", "step by step",
        "introduction", "getting started", "basics", "course", "lesson",
        "explain", "what is", "understand", "overview"
    ],
    "general": []  # Fallback category
}

# Source mapping per category
CATEGORY_SOURCES = {
    "dataset": ["kaggle", "github", "google", "wikipedia", "tavily"],
    "code": ["stackoverflow", "github", "google", "youtube", "tavily"],
    "research": ["arxiv", "google", "wikipedia", "github", "tavily"],
    "tutorial": ["youtube", "google", "stackoverflow", "wikipedia", "tavily"],
    "general": ["google", "wikipedia", "stackoverflow", "github", "arxiv", "youtube", "kaggle", "tavily"],
}


def classify_query(query: str) -> dict:
    """
    Classify a query into a category and determine which sources to search.
    
    Returns:
        dict with 'category', 'sources', 'confidence', and 'keywords_matched'
    """
    query_lower = query.lower().strip()
    
    scores = {}
    matched_keywords = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "general":
            continue
        
        score = 0
        matches = []
        for keyword in keywords:
            if keyword in query_lower:
                # Longer keyword matches get higher scores
                weight = len(keyword.split())
                score += weight
                matches.append(keyword)
        
        if score > 0:
            scores[category] = score
            matched_keywords[category] = matches
    
    # Determine the best category
    if scores:
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]
        # Confidence based on score
        confidence = min(0.95, 0.5 + (max_score * 0.1))
    else:
        best_category = "general"
        confidence = 0.3
        matched_keywords["general"] = []
    
    sources = CATEGORY_SOURCES.get(best_category, CATEGORY_SOURCES["general"])
    
    return {
        "category": best_category,
        "sources": sources,
        "confidence": round(confidence, 2),
        "keywords_matched": matched_keywords.get(best_category, []),
        "all_scores": scores,
    }


def detect_intent(query: str) -> dict:
    """
    Detect the user's intent from the query.
    
    Returns:
        dict with 'intent', 'is_question', 'is_comparison', 'entities'
    """
    query_lower = query.lower().strip()
    
    # Question detection
    question_words = ["what", "how", "why", "when", "where", "which", "who", "can", "is", "are", "do", "does"]
    is_question = any(query_lower.startswith(w) for w in question_words) or query_lower.endswith("?")
    
    # Comparison detection
    comparison_words = ["vs", "versus", "compared to", "difference between", "better than", "or"]
    is_comparison = any(w in query_lower for w in comparison_words)
    
    # Intent classification
    if is_comparison:
        intent = "comparison"
    elif any(w in query_lower for w in ["find", "search", "list", "show me", "get"]):
        intent = "search"
    elif any(w in query_lower for w in ["how to", "tutorial", "guide", "learn"]):
        intent = "learn"
    elif any(w in query_lower for w in ["explain", "what is", "define", "meaning"]):
        intent = "explain"
    elif any(w in query_lower for w in ["build", "create", "make", "develop", "implement"]):
        intent = "build"
    elif is_question:
        intent = "question"
    else:
        intent = "explore"
    
    # Simple entity extraction (quoted terms or capitalized words)
    entities = re.findall(r'"([^"]*)"', query)
    if not entities:
        # Extract potential entities (multi-word capitalized phrases)
        entities = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', query)
    
    return {
        "intent": intent,
        "is_question": is_question,
        "is_comparison": is_comparison,
        "entities": entities,
    }
