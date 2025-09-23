# Configuration for different data sources
CRAWLER_CONFIGS = {
    "stackoverflow": {
        "endpoint": "https://api.stackexchange.com/2.3/questions",
        "rate_limit": 1,  # seconds
        "tags": ["python", "machine-learning", "fastapi", "ai", "deep-learning"],
    },
    "github": {
        "endpoint": "https://api.github.com/search/repositories",
        "rate_limit": 1,
        "languages": ["python", "javascript", "typescript"],
    },
    "rss_feeds": {
        "tech": [
            "https://feeds.feedburner.com/TechCrunch",
            "https://rss.cnn.com/rss/edition.rss",
        ],
        "finance": [
            "https://feeds.finance.yahoo.com/rss/2.0/headline",
            "https://www.reuters.com/markets/wealth/rss",
        ],
    },
}

# API Keys (set these as environment variables)
API_KEYS = {
    "news_api": os.getenv("NEWS_API_KEY"),  # Get free key from newsapi.org
    "alpha_vantage": os.getenv("ALPHA_VANTAGE_KEY"),  # For financial data
}

AVAILABLE_APIS = {
    "news_api": bool(API_KEYS["news_api"]),
    "alpha_vantage": bool(API_KEYS["alpha_vantage"]),
}
