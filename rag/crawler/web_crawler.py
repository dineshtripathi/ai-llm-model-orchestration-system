import requests
from bs4 import BeautifulSoup
import time
import sys
import os
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from rag.ingestion.document_processor import DocumentProcessor

class WebCrawler:
    def __init__(self, document_processor: DocumentProcessor = None):
        self.document_processor = document_processor or DocumentProcessor()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Educational RAG System Crawler 1.0 (Learning Purpose)'
        })
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def crawl_url(self, url: str, max_length: int = 10000) -> Optional[Dict]:
        """Crawl a single URL and extract text content"""
        try:
            # Respect rate limiting
            time.sleep(1)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract text content
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No Title"
            
            # Get main content (prefer article, main, or fallback to body)
            content_selectors = ['article', 'main', '.content', '.post', 'body']
            content = None
            
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
            if not content:
                content = soup
            
            # Extract and clean text
            text_content = content.get_text(separator=' ', strip=True)
            
            # Limit content length
            if len(text_content) > max_length:
                text_content = text_content[:max_length] + "..."
            
            return {
                "url": url,
                "title": title_text,
                "content": text_content,
                "scraped_at": datetime.now().isoformat(),
                "content_length": len(text_content)
            }
            
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {e}")
            return None
    
    def crawl_urls(self, urls: List[str]) -> List[Dict]:
        """Crawl multiple URLs"""
        results = []
        
        for url in urls:
            self.logger.info(f"Crawling: {url}")
            result = self.crawl_url(url)
            
            if result:
                results.append(result)
            
            # Rate limiting between requests
            time.sleep(2)
        
        return results
    
    def crawl_news_sources(self) -> List[Dict]:
        """Crawl predefined news and tech sources"""
        # Safe, educational URLs that typically allow crawling
        urls = [
            "https://en.wikipedia.org/wiki/Artificial_intelligence",
            "https://en.wikipedia.org/wiki/Machine_learning", 
            "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "https://en.wikipedia.org/wiki/Web_development",
            "https://en.wikipedia.org/wiki/FastAPI"
        ]
        
        return self.crawl_urls(urls)
    
    def ingest_crawled_data(self, crawled_data: List[Dict]) -> Dict:
        """Process crawled data and ingest into ChromaDB"""
        if not crawled_data:
            return {"success": False, "message": "No data to ingest"}
        
        documents = []
        
        for data in crawled_data:
            # Create document chunks from crawled content
            content_with_title = f"Title: {data['title']}\n\nContent: {data['content']}"
            
            # Use document processor to chunk the content
            chunks = self.document_processor.chunk_text(content_with_title)
            
            for i, chunk in enumerate(chunks):
                doc_data = {
                    "content": chunk,
                    "metadata": {
                        "source": data["url"],
                        "title": data["title"],
                        "chunk_id": i,
                        "scraped_at": data["scraped_at"],
                        "content_type": "web_crawled",
                        "total_chunks": len(chunks)
                    }
                }
                documents.append(doc_data)
        
        # Ingest into ChromaDB
        success = self.document_processor.ingest_documents(documents)
        
        return {
            "success": success,
            "urls_processed": len(crawled_data),
            "documents_created": len(documents),
            "sources": [data["url"] for data in crawled_data]
        }
    
    def crawl_and_ingest(self, urls: List[str] = None) -> Dict:
        """Complete pipeline: crawl URLs and ingest into RAG system"""
        if urls is None:
            self.logger.info("Using default news sources")
            crawled_data = self.crawl_news_sources()
        else:
            crawled_data = self.crawl_urls(urls)
        
        return self.ingest_crawled_data(crawled_data)

if __name__ == "__main__":
    # Test the web crawler
    crawler = WebCrawler()
    
    # Test with educational Wikipedia pages
    test_urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Large_language_model"
    ]
    
    print("Starting web crawl...")
    result = crawler.crawl_and_ingest(test_urls)
    
    print(f"Crawl Result: {result}")
    
    # Test search with newly crawled data
    if result["success"]:
        print("\nTesting search with crawled data...")
        search_results = crawler.document_processor.chroma_manager.search_documents(
            "What is artificial intelligence?", 
            n_results=3
        )
        
        for i, doc in enumerate(search_results["documents"]):
            print(f"{i+1}. {doc[:200]}...")