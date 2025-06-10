# orchestrator/agent1_pipeline.py

import asyncio
import datetime
import traceback # <--- ADD THIS IMPORT
from config import settings
from fetcher.newsapi_client import NewsAPIClient
from storage.db import MongoDBManager

async def run_agent1_pipeline():
    db_manager = MongoDBManager()

    news_fetcher = NewsAPIClient(
        api_key=settings.NEWS_API_KEY,
        keywords=settings.NEWS_KEYWORDS,
        db_manager=db_manager
    )

    fetch_interval_seconds = settings.FETCH_INTERVAL_MINUTES * 60
    cleanup_interval_seconds = settings.CLEANUP_INTERVAL_HOURS * 3600
    last_cleanup_time = datetime.datetime.now(datetime.timezone.utc)

    print("--- Starting Agent 1 Pipeline: News Fetching & Cleanup ---")
    try:
        await db_manager.connect()

        while True:
            try: # <--- ADD THIS INNER TRY BLOCK
                # Step 1: Fetch and Save News
                await news_fetcher.fetch_and_save_news()
            except Exception as e: # <--- ADD THIS INNER EXCEPT BLOCK
                print(f"Error during news fetching/saving cycle: {e}")
                traceback.print_exc() # <--- PRINT THE FULL TRACEBACK HERE
                # Decide whether to continue the loop or break. For now, let's continue to see if it's transient.
                await asyncio.sleep(10) # Small delay before trying again
                continue # Skip the rest of this iteration and go to next loop cycle

            # Step 2: Periodically Clean Up Old Articles
            current_time = datetime.datetime.now(datetime.timezone.utc)
            if (current_time - last_cleanup_time).total_seconds() >= cleanup_interval_seconds:
                print(f"[{current_time.isoformat()}] Starting old article cleanup...")
                await db_manager.delete_old_articles(settings.NEWS_RETENTION_DAYS)
                last_cleanup_time = current_time

            print(f"Next fetch in {settings.FETCH_INTERVAL_MINUTES} minutes. (Cleanup in {round((last_cleanup_time + datetime.timedelta(seconds=cleanup_interval_seconds) - current_time).total_seconds()/3600, 2)} hours)")
            await asyncio.sleep(fetch_interval_seconds)

    except Exception as e: # This is the outer exception handler for pipeline startup/critical errors
        print(f"Agent 1 Pipeline encountered a critical error: {e}") # Changed message for clarity
        traceback.print_exc() # <--- Print traceback for critical errors too
    finally:
        if db_manager.client:
            await db_manager.close()
        print("--- Agent 1 Pipeline Finished ---")