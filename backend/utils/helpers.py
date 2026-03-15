"""
Utility Helper Functions
"""
import re
import hashlib
import time


# Simple in-memory cache
_cache = {}
_cache_ttl = 300  # 5 minutes


def cache_get(key: str):
    """Get value from cache if not expired"""
    if key in _cache:
        item = _cache[key]
        if time.time() - item["timestamp"] < _cache_ttl:
            return item["value"]
        else:
            del _cache[key]
    return None


def cache_set(key: str, value, ttl: int = None):
    """Set value in cache"""
    _cache[key] = {
        "value": value,
        "timestamp": time.time(),
    }


def make_cache_key(query: str, sources: list = None) -> str:
    """Generate a cache key from query and sources"""
    key_str = query.lower().strip()
    if sources:
        key_str += "|" + ",".join(sorted(sources))
    return hashlib.md5(key_str.encode()).hexdigest()


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max length with ellipsis"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "..."
