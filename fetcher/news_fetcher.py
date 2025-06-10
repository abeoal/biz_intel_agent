# fetcher/news_fetcher.py

import asyncio
import aiohttp
import datetime
from dateutil.parser import isoparse # For robust ISO 8601 parsing
from newsapi import NewsApiClient # Assuming you are using the official NewsAPI Python client
# If you were using asyncnewsapi, ensure it returns datetime objects, otherwise use isoparse.

from config import settings
from storage.db import MongoDBManager

class NewsFetcher:
    def __init__(self, api_key: str, base_url: str, keywords: list):
        self.newsapi = NewsApiClient(api_key=api_key)
        self.base_url = base_url
        self.keywords = keywords
        self.db_manager = MongoDBManager()

    async def _fetch_articles_from_newsapi(self, query: str):
        try:
            # Using the official NewsApiClient for simplicity.
            # It handles the HTTP requests.
            # Adjust the language, country, etc., as needed.
            response = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='relevancy',
                page_size=100 # Fetch up to 100 articles per query
            )
            return response.get('articles', [])
        except Exception as e:
            print(f"Error fetching articles for query '{query}': {e}")
            return []

    async def _process_article(self, article: dict) -> dict:
        """Processes a raw article dict into a structured format for storage."""
        processed_article = {
            "source_id": article.get("source", {}).get("id"),
            "source_name": article.get("source", {}).get("name"),
            "author": article.get("author"),
            "title": article.get("title"),
            "description": article.get("description"),
            "url": article.get("url"),
            "urlToImage": article.get("urlToImage"),
            "published_at": None, # Initialize as None
            "content": article.get("content"),
            # 'timestamp' will be added by MongoDBManager if not present
        }

        # Convert 'published_at' string to datetime object
        published_at_str = article.get("publishedAt")
        if published_at_str:
            try:
                processed_article["published_at"] = isoparse(published_at_str)
            except ValueError as e:
                print(f"Warning: Could not parse published_at '{published_at_str}': {e}")
                # Fallback: if parsing fails, maybe store as string or omit
                processed_article["published_at"] = published_at_str # Store as string if parsing fails

        return processed_article

    async def fetch_and_save_news(self):
        print(f"[{datetime.datetime.now(datetime.timezone.utc).isoformat()}] Starting news fetch...")
        total_new_articles = 0
        for keyword in self.keywords:
            print(f"Fetching news for keyword: '{keyword}'")
            articles = await self._fetch_articles_from_newsapi(keyword)
            for article in articles:
                processed_article = await self._process_article(article)
                if processed_article["title"] and processed_article["url"]: # Basic validation
                    inserted_id, is_new = await self.db_manager.save_article(processed_article)
                    if is_new:
                        total_new_articles += 1
                        # print(f"  Saved new article: {processed_article['title']}")
        print(f"Finished fetching. Total new articles saved: {total_new_articles}")
        return total_new_articles

    async def run_fetcher_loop(self):
        """Main loop to periodically fetch news and clean up old data."""
        fetch_interval_seconds = settings.FETCH_INTERVAL_MINUTES * 60
        cleanup_interval_seconds = settings.CLEANUP_INTERVAL_HOURS * 3600
        last_cleanup_time = datetime.datetime.now(datetime.timezone.utc)

        while True:
            # Run the news fetching task
            await self.fetch_and_save_news()

            # Periodically run the cleanup task
            current_time = datetime.datetime.now(datetime.timezone.utc)
            if (current_time - last_cleanup_time).total_seconds() >= cleanup_interval_seconds:
                print(f"[{current_time.isoformat()}] Starting old article cleanup...")
                await self.db_manager.delete_old_articles(settings.NEWS_RETENTION_DAYS)
                last_cleanup_time = current_time

            print(f"Waiting for {settings.FETCH_INTERVAL_MINUTES} minutes before next fetch...")
            await asyncio.sleep(fetch_interval_seconds)

    async def close(self):
        await self.db_manager.close()

# Main execution block
if __name__ == "__main__":
    fetcher = NewsFetcher(
        api_key=settings.NEWS_API_KEY,
        base_url=settings.NEWS_API_BASE_URL,
        keywords=settings.NEWS_KEYWORDS
    )
    try:
        # Run the continuous fetching and cleanup loop
        asyncio.run(fetcher.run_fetcher_loop())
    except KeyboardInterrupt:
        print("Fetcher stopped by user.")
    finally:
        asyncio.run(fetcher.close()) # Ensure client is closed