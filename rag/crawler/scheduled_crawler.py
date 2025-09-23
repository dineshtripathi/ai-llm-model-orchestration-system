import time
from datetime import datetime

import schedule
from web_crawler import WebCrawler


class ScheduledCrawler:
    def __init__(self):
        self.crawler = WebCrawler()

    def daily_tech_news_crawl(self):
        """Daily crawl of tech news sources"""
        print(f"Starting daily crawl at {datetime.now()}")

        # Educational and news sources
        urls = [
            "https://en.wikipedia.org/wiki/Artificial_intelligence",
            "https://en.wikipedia.org/wiki/Machine_learning",
            "https://en.wikipedia.org/wiki/Large_language_model",
        ]

        result = self.crawler.crawl_and_ingest(urls)
        print(f"Daily crawl completed: {result}")

    def start_scheduler(self):
        """Start the scheduled crawler"""
        # Schedule daily crawls
        schedule.every().day.at("09:00").do(self.daily_tech_news_crawl)

        print("Crawler scheduler started. Press Ctrl+C to stop.")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


if __name__ == "__main__":
    scheduler = ScheduledCrawler()
    scheduler.start_scheduler()
