# import requests
# import time
# import json
# from typing import List, Dict
# from datetime import datetime, timedelta
# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# from rag.ingestion.document_processor import DocumentProcessor

# class APICrawler:
#     def __init__(self, document_processor: DocumentProcessor = None):
#         self.document_processor = document_processor or DocumentProcessor()
#         self.session = requests.Session()

#     def crawl_stackoverflow_questions(self, tags: List[str] = ["python", "machine-learning"],
#                                     max_questions: int = 10) -> List[Dict]:
#         """Use StackOverflow API (no authentication needed for basic queries)"""
#         try:
#             # StackOverflow API endpoint
#             url = "https://api.stackexchange.com/2.3/questions"

#             results = []
#             for tag in tags:
#                 params = {
#                     'order': 'desc',
#                     'sort': 'votes',
#                     'tagged': tag,
#                     'site': 'stackoverflow',
#                     'pagesize': max_questions,
#                     'filter': 'withbody'  # Include question body
#                 }

#                 response = self.session.get(url, params=params)
#                 response.raise_for_status()

#                 data = response.json()

#                 for question in data.get('items', []):
#                     results.append({
#                         'title': question.get('title', ''),
#                         'content': question.get('body', ''),
#                         'url': question.get('link', ''),
#                         'tags': question.get('tags', []),
#                         'score': question.get('score', 0),
#                         'source': 'stackoverflow',
#                         'scraped_at': datetime.now().isoformat()
#                     })

#                 # Respect API rate limits
#                 time.sleep(1)

#             return results

#         except Exception as e:
#             print(f"Error crawling StackOverflow: {e}")
#             return []

#     def crawl_news_api(self, api_key: str, query: str = "artificial intelligence") -> List[Dict]:
#         """Use NewsAPI for finance/tech news (requires free API key)"""
#         try:
#             url = "https://newsapi.org/v2/everything"
#             params = {
#                 'q': query,
#                 'sortBy': 'publishedAt',
#                 'pageSize': 20,
#                 'language': 'en',
#                 'apiKey': api_key
#             }

#             response = self.session.get(url, params=params)
#             response.raise_for_status()

#             data = response.json()
#             results = []

#             for article in data.get('articles', []):
#                 results.append({
#                     'title': article.get('title', ''),
#                     'content': article.get('description', '') + ' ' + article.get('content', ''),
#                     'url': article.get('url', ''),
#                     'source': article.get('source', {}).get('name', 'news'),
#                     'published_at': article.get('publishedAt', ''),
#                     'scraped_at': datetime.now().isoformat()
#                 })

#             return results

#         except Exception as e:
#             print(f"Error crawling news: {e}")
#             return []

#     def crawl_github_trending(self, language: str = "python") -> List[Dict]:
#         """Use GitHub API for trending repositories"""
#         try:
#             url = "https://api.github.com/search/repositories"

#             # Search for trending repos (created in last month, sorted by stars)
#             date_filter = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

#             params = {
#                 'q': f'language:{language} created:>{date_filter}',
#                 'sort': 'stars',
#                 'order': 'desc',
#                 'per_page': 10
#             }

#             response = self.session.get(url, params=params)
#             response.raise_for_status()

#             data = response.json()
#             results = []

#             for repo in data.get('items', []):
#                 results.append({
#                     'title': repo.get('full_name', ''),
#                     'content': f"Description: {repo.get('description', '')}\nLanguage: {repo.get('language', '')}\nStars: {repo.get('stargazers_count', 0)}",
#                     'url': repo.get('html_url', ''),
#                     'source': 'github',
#                     'language': repo.get('language', ''),
#                     'stars': repo.get('stargazers_count', 0),
#                     'scraped_at': datetime.now().isoformat()
#                 })

#             return results

#         except Exception as e:
#             print(f"Error crawling GitHub: {e}")
#             return []

#     def crawl_rss_feeds(self, feeds: List[str]) -> List[Dict]:
#         """Crawl RSS feeds for finance/tech news"""
#         try:
#             import feedparser

#             results = []
#             for feed_url in feeds:
#                 feed = feedparser.parse(feed_url)

#                 for entry in feed.entries[:10]:  # Limit to 10 per feed
#                     results.append({
#                         'title': entry.get('title', ''),
#                         'content': entry.get('summary', '') or entry.get('description', ''),
#                         'url': entry.get('link', ''),
#                         'source': feed.feed.get('title', 'rss'),
#                         'published_at': entry.get('published', ''),
#                         'scraped_at': datetime.now().isoformat()
#                     })

#                 time.sleep(1)  # Rate limiting

#             return results

#         except ImportError:
#             print("feedparser not installed. Run: pip install feedparser")
#             return []
#         except Exception as e:
#             print(f"Error crawling RSS feeds: {e}")
#             return []

# def comprehensive_crawl(self, search_queries: List[str] = None) -> Dict:
#         """Run all crawlers and ingest data"""
#         if search_queries is None:
#             search_queries = ["artificial intelligence", "machine learning python", "fastapi tutorial"]

#         all_data = []

#         # DuckDuckGo searches
#         print("Running DuckDuckGo searches...")
#         for query in search_queries:
#             search_results = self.search_duckduckgo(query, max_results=3)
#             all_data.extend(search_results)
#             time.sleep(2)  # Rate limiting

#         # StackOverflow
#         print("Crawling StackOverflow...")
#         so_data = self.crawl_stackoverflow_questions(['python', 'ai'])
#         all_data.extend(so_data)

#         # GitHub trending
#         print("Crawling GitHub...")
#         gh_data = self.crawl_github_trending('python')
#         all_data.extend(gh_data)

#         # Ingest all data
#         if all_data:
#             print(f"Collected {len(all_data)} items, ingesting...")
#             return self.document_processor.ingest_crawled_data(all_data)
#         else:
#             return {"success": False, "message": "No data collected"}


# def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict]:
#         """Use DuckDuckGo search (more permissive than Google)"""
#         try:
#             from duckduckgo_search import DDGS

#             results = []
#             with DDGS() as ddgs:
#                 for result in ddgs.text(query, max_results=max_results):
#                     results.append({
#                         'title': result.get('title', ''),
#                         'content': result.get('body', ''),
#                         'url': result.get('href', ''),
#                         'source': 'duckduckgo_search',
#                         'scraped_at': datetime.now().isoformat()
#                     })

#             return results

#         except ImportError:
#             print("Install: pip install duckduckgo-search")
#             return []
#         except Exception as e:
#             print(f"Error searching DuckDuckGo: {e}")
#             return []

# def comprehensive_crawl(self, search_queries: List[str] = None) -> Dict:
#         """Run all crawlers and ingest data"""
#         if search_queries is None:
#             search_queries = ["artificial intelligence", "machine learning python", "fastapi tutorial"]

#         all_data = []

#         # DuckDuckGo searches
#         for query in search_queries:
#             search_results = self.search_duckduckgo(query, max_results=3)
#             all_data.extend(search_results)
#             time.sleep(2)  # Rate limiting

#         # StackOverflow
#         so_data = self.crawl_stackoverflow_questions(['python', 'ai'])
#         all_data.extend(so_data)

#         # GitHub trending
#         gh_data = self.crawl_github_trending('python')
#         all_data.extend(gh_data)

#         # Ingest all data
#         if all_data:
#             return self.document_processor.ingest_crawled_data(all_data)
#         else:
#             return {"success": False, "message": "No data collected"}

# if __name__ == "__main__":
#     crawler = APICrawler()

#     print("Testing comprehensive crawl...")

#     # Test DuckDuckGo search
#     search_queries = [
#         "python machine learning tutorial",
#         "fastapi rest api guide",
#         "artificial intelligence news"
#     ]

#     result = crawler.comprehensive_crawl(search_queries)
#     print(f"Comprehensive crawl result: {result}")

#     # Test individual DuckDuckGo search
#     print("\nTesting individual DuckDuckGo search...")
#     search_results = crawler.search_duckduckgo("python programming", max_results=3)
#     for i, result in enumerate(search_results):
#         print(f"{i+1}. {result['title']} - {result['url']}")


#     print("Crawling StackOverflow questions...")
#     so_data = crawler.crawl_stackoverflow_questions(['python', 'fastapi'])

#     print("Crawling GitHub trending...")
#     gh_data = crawler.crawl_github_trending('python')

#     print("Crawling RSS feeds...")
#     finance_feeds = [
#         'https://feeds.finance.yahoo.com/rss/2.0/headline',
#         'https://www.reuters.com/markets/wealth/rss'
#     ]
#     rss_data = crawler.crawl_rss_feeds(finance_feeds)

#     all_data = so_data + gh_data + rss_data

#     if all_data:
#         result = crawler.document_processor.ingest_crawled_data(all_data)
#         print(f"Ingestion result: {result}")

import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from rag.ingestion.document_processor import DocumentProcessor


class APICrawler:
    def __init__(self, document_processor: DocumentProcessor = None):
        self.document_processor = document_processor or DocumentProcessor()
        self.session = requests.Session()

    def crawl_stackoverflow_questions(
        self, tags: List[str] = ["python", "machine-learning"], max_questions: int = 10
    ) -> List[Dict]:
        """Use StackOverflow API (no authentication needed for basic queries)"""
        try:
            url = "https://api.stackexchange.com/2.3/questions"
            results = []
            for tag in tags:
                params = {
                    "order": "desc",
                    "sort": "votes",
                    "tagged": tag,
                    "site": "stackoverflow",
                    "pagesize": max_questions,
                    "filter": "withbody",
                }

                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                for question in data.get("items", []):
                    results.append(
                        {
                            "title": question.get("title", ""),
                            "content": question.get("body", ""),
                            "url": question.get("link", ""),
                            "tags": question.get("tags", []),
                            "score": question.get("score", 0),
                            "source": "stackoverflow",
                            "scraped_at": datetime.now().isoformat(),
                        }
                    )
                time.sleep(1)
            return results
        except Exception as e:
            print(f"Error crawling StackOverflow: {e}")
            return []

    def crawl_news_api(
        self, api_key: str, query: str = "artificial intelligence"
    ) -> List[Dict]:
        """Use NewsAPI for finance/tech news (requires free API key)"""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": 20,
                "language": "en",
                "apiKey": api_key,
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            results = []

            for article in data.get("articles", []):
                results.append(
                    {
                        "title": article.get("title", ""),
                        "content": article.get("description", "")
                        + " "
                        + article.get("content", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", {}).get("name", "news"),
                        "published_at": article.get("publishedAt", ""),
                        "scraped_at": datetime.now().isoformat(),
                    }
                )
            return results
        except Exception as e:
            print(f"Error crawling news: {e}")
            return []

    def crawl_github_trending(self, language: str = "python") -> List[Dict]:
        """Use GitHub API for trending repositories"""
        try:
            url = "https://api.github.com/search/repositories"
            date_filter = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            params = {
                "q": f"language:{language} created:>{date_filter}",
                "sort": "stars",
                "order": "desc",
                "per_page": 10,
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            results = []

            for repo in data.get("items", []):
                results.append(
                    {
                        "title": repo.get("full_name", ""),
                        "content": f"Description: {repo.get('description', '')}\nLanguage: {repo.get('language', '')}\nStars: {repo.get('stargazers_count', 0)}",
                        "url": repo.get("html_url", ""),
                        "source": "github",
                        "language": repo.get("language", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "scraped_at": datetime.now().isoformat(),
                    }
                )
            return results
        except Exception as e:
            print(f"Error crawling GitHub: {e}")
            return []

    def crawl_rss_feeds(self, feeds: List[str]) -> List[Dict]:
        """Crawl RSS feeds for finance/tech news"""
        try:
            import feedparser

            results = []
            for feed_url in feeds:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:
                    results.append(
                        {
                            "title": entry.get("title", ""),
                            "content": entry.get("summary", "")
                            or entry.get("description", ""),
                            "url": entry.get("link", ""),
                            "source": feed.feed.get("title", "rss"),
                            "published_at": entry.get("published", ""),
                            "scraped_at": datetime.now().isoformat(),
                        }
                    )
                time.sleep(1)
            return results
        except ImportError:
            print("feedparser not installed. Run: pip install feedparser")
            return []
        except Exception as e:
            print(f"Error crawling RSS feeds: {e}")
            return []

    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict]:
        """Use DuckDuckGo search (more permissive than Google)"""
        try:
            from ddgs import DDGS  # Changed import

            results = []
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=max_results):
                    results.append(
                        {
                            "title": result.get("title", ""),
                            "content": result.get("body", ""),
                            "url": result.get("href", ""),
                            "source": "duckduckgo_search",
                            "scraped_at": datetime.now().isoformat(),
                        }
                    )
            return results
        except ImportError:
            print("Install: pip install ddgs")
            return []
        except Exception as e:
            print(f"Error searching DuckDuckGo: {e}")
            return []

    def comprehensive_crawl(
        self, search_queries: List[str] = None, use_paid_apis: bool = False
    ) -> Dict:
        """Run all crawlers and ingest data"""
        if search_queries is None:
            search_queries = [
                "artificial intelligence",
                "machine learning python",
                "fastapi tutorial",
            ]

        all_data = []
        api_results = {"used_apis": [], "skipped_apis": []}

        # Free APIs (always run)
        print("Running DuckDuckGo searches...")
        for query in search_queries:
            search_results = self.search_duckduckgo(query, max_results=3)
            all_data.extend(search_results)
            time.sleep(2)
        api_results["used_apis"].append("duckduckgo")

        print("Crawling StackOverflow...")
        so_data = self.crawl_stackoverflow_questions(["python", "ai"])
        all_data.extend(so_data)
        api_results["used_apis"].append("stackoverflow")

        print("Crawling GitHub...")
        gh_data = self.crawl_github_trending("python")
        all_data.extend(gh_data)
        api_results["used_apis"].append("github")

        print("Crawling RSS feeds...")
        finance_feeds = [
            "https://feeds.finance.yahoo.com/rss/2.0/headline",
            "https://www.reuters.com/markets/wealth/rss",
        ]
        rss_data = self.crawl_rss_feeds(finance_feeds)
        all_data.extend(rss_data)
        api_results["used_apis"].append("rss_feeds")

        # Paid/API Key required services (optional)
        if use_paid_apis:
            # Define API keys inline
            API_KEYS = {
                "news_api": os.getenv("NEWS_API_KEY"),
                "alpha_vantage": os.getenv("ALPHA_VANTAGE_KEY"),
            }

            # NewsAPI
            if API_KEYS["news_api"]:
                print("Crawling NewsAPI...")
                news_data = self.crawl_news_api(
                    API_KEYS["news_api"], "artificial intelligence"
                )
                all_data.extend(news_data)
                api_results["used_apis"].append("news_api")
            else:
                print("NewsAPI key not found, skipping...")
                api_results["skipped_apis"].append("news_api")

            # Alpha Vantage
            if API_KEYS["alpha_vantage"]:
                print("Crawling Alpha Vantage...")
                av_data = self.crawl_alpha_vantage_news(API_KEYS["alpha_vantage"])
                all_data.extend(av_data)
                api_results["used_apis"].append("alpha_vantage")
            else:
                print("Alpha Vantage key not found, skipping...")
                api_results["skipped_apis"].append("alpha_vantage")

        # Ingest all data
        if all_data:
            print(f"Collected {len(all_data)} items, ingesting...")
            result = self.document_processor.ingest_crawled_data(all_data)
            result.update(api_results)
            return result
        else:
            return {"success": False, "message": "No data collected", **api_results}

    def crawl_alpha_vantage_news(self, api_key: str) -> List[Dict]:
        """Use Alpha Vantage API for financial news"""
        try:
            url = "https://www.alphavantage.co/query"
            params = {"function": "NEWS_SENTIMENT", "apikey": api_key, "limit": 20}

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            results = []
            for article in data.get("feed", []):
                results.append(
                    {
                        "title": article.get("title", ""),
                        "content": article.get("summary", ""),
                        "url": article.get("url", ""),
                        "source": "alpha_vantage_news",
                        "published_at": article.get("time_published", ""),
                        "sentiment_score": article.get("overall_sentiment_score", 0),
                        "scraped_at": datetime.now().isoformat(),
                    }
                )

            return results
        except Exception as e:
            print(f"Error crawling Alpha Vantage: {e}")
            return []


if __name__ == "__main__":
    crawler = APICrawler()

    print("Testing comprehensive crawl...")
    search_queries = [
        "python machine learning tutorial",
        "fastapi rest api guide",
        "artificial intelligence news",
    ]

    # Test without API keys (free sources only)
    print("Testing comprehensive crawl (free sources only)...")
    result = crawler.comprehensive_crawl()
    print(f"Free crawl result: {result}")

    # Test with API keys (if available)
    print("\nTesting with paid APIs (if keys available)...")
    result_with_apis = crawler.comprehensive_crawl(use_paid_apis=True)
    print(f"Full crawl result: {result_with_apis}")

    result = crawler.comprehensive_crawl(search_queries)
    print(f"Comprehensive crawl result: {result}")

    # Test individual DuckDuckGo search
    print("\nTesting individual DuckDuckGo search...")
    search_results = crawler.search_duckduckgo("python programming", max_results=3)
    for i, result in enumerate(search_results):
        print(f"{i+1}. {result['title']} - {result['url']}")
