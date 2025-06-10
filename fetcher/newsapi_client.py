# fetcher/newsapi_client.py

import asyncio
import datetime
from dateutil.parser import isoparse
from newsapi import NewsApiClient

from config import settings
from storage.db import MongoDBManager
from processor import nlp_enricher # <--- IMPORT THE NEW NLP ENRICHER
from analyzer import ranking_filter # <--- IMPORT THE NEW RANKING/FILTER MODULE

class NewsAPIClient:
    def __init__(self, api_key: str, keywords: list, db_manager: MongoDBManager):
        self.newsapi = NewsApiClient(api_key=api_key)
        self.keywords = keywords
        self.db_manager = db_manager

    async def _fetch_articles_from_newsapi(self, query: str):
        """Fetches articles from NewsAPI for a given query, running the synchronous call in a separate thread."""
        try:
            print(f"DEBUG: Inside _fetch_articles_from_newsapi for query: '{query}'")
            print(f"DEBUG: About to call asyncio.to_thread for self.newsapi.get_everything...")

            api_response = await asyncio.to_thread(
                self.newsapi.get_everything,
                q=query,
                language='en',
                sort_by='relevancy',
                page_size=100
            )

            print(f"DEBUG: Finished asyncio.to_thread. Type of api_response: {type(api_response)}")
            print(f"DEBUG: Content of api_response (first 200 chars): {str(api_response)[:200]}")


            if api_response and api_response.get('status') == 'ok':
                print(f"DEBUG: NewsAPI response status is OK for query: '{query}'")
                return api_response.get('articles', [])
            else:
                print(f"NewsAPI error for query '{query}': {api_response.get('message', 'Unknown error')}")
                return []
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
            "published_at": None,
            "content": article.get("content"),
        }

        published_at_str = article.get("publishedAt")
        if published_at_str:
            try:
                processed_article["published_at"] = isoparse(published_at_str)
            except ValueError as e:
                print(f"Warning: Could not parse published_at '{published_at_str}' for article '{article.get('title')}': {e}")
                processed_article["published_at"] = published_at_str

        return processed_article

    async def fetch_and_save_news(self):
        """Fetches news for configured keywords and saves them to the database."""
        print(f"[{datetime.datetime.now(datetime.timezone.utc).isoformat()}] Starting news fetch...")
        total_new_articles_saved = 0
        for keyword in self.keywords:
            print(f"  Fetching news for keyword: '{keyword}'...")
            articles = await self._fetch_articles_from_newsapi(keyword)

            print(f"DEBUG_FETCH_SAVE: After fetching. Type of 'articles' variable: {type(articles)}")
            print(f"DEBUG_FETCH_SAVE: Number of articles returned: {len(articles)}")
            if articles and len(articles) > 0:
                print(f"DEBUG_FETCH_SAVE: Type of FIRST article in list: {type(articles[0])}")
                print(f"DEBUG_FETCH_SAVE: Content of FIRST article (first 100 chars): {str(articles[0])[:100]}")

            for i, article in enumerate(articles):
                if not isinstance(article, dict):
                    print(f"CRITICAL ERROR: Expected article at index {i} to be a dictionary, but found type: {type(article)}")
                    print(f"Skipping malformed article: {article}")
                    continue

                processed_article = await self._process_article(article)
                if processed_article["title"] and processed_article["url"]:
                    inserted_id, is_new = await self.db_manager.save_article(processed_article)
                    if is_new:
                        total_new_articles_saved += 1
                        # --- NEW: Enrich the article after saving ---
                        processed_article["_id"] = inserted_id # Ensure _id is present for update
                        enriched_article = await nlp_enricher.enrich_article_nlp(processed_article)
                        await self.db_manager.update_article(enriched_article)
                        # --- END NEW ---
        print(f"Finished current fetch cycle. Total new articles saved: {total_new_articles_saved}")
        return total_new_articles_saved

    async def close(self):
        """No longer closes the DB connection directly, as it's shared."""
        pass