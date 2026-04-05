"""
SATYON-AI Configuration
Environment variables and API keys management
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server Config
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 10000)) # Render uses 10000 or $PORT
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Redis Config (optional caching)
REDIS_URL = os.getenv("REDIS_URL", "")

# Rate Limiting
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", 30))

# AI Config
AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", 1500))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", 0.7))

# Search Config
MAX_RESULTS_PER_SOURCE = int(os.getenv("MAX_RESULTS_PER_SOURCE", 5))
SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", 10))
