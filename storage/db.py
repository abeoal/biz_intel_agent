# storage/db.py

from motor.motor_asyncio import AsyncIOMotorClient # Asynchronous MongoDB driver
from config import settings # Your settings module
import datetime # Import for type hinting

class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.uri = settings.MONGODB_URI
        self.db_name = settings.MONGODB_DB_NAME

    async def connect(self):
        """Establishes connection to MongoDB."""
        if self.client is None:
            try:
                print(f"Attempting to connect to MongoDB at: {self.uri}")
                self.client = AsyncIOMotorClient(self.uri)
                # Ping the database to ensure connection is active
                await self.client.admin.command('ping')
                self.db = self.client[self.db_name]
                print(f"Successfully connected to MongoDB database: {self.db_name}")
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
                self.client = None # Reset client on failure
                raise # Re-raise the exception to propagate it

    async def save_article(self, article: dict):
        """Saves a processed article to the database, checking for duplicates by URL."""
        if self.db is None:
            await self.connect()

        articles_collection = self.db.articles
        # Check if an article with the same URL already exists
        existing_article = await articles_collection.find_one({"url": article["url"]})

        if existing_article:
            return existing_article["_id"], False # Return existing ID and False for not new
        else:
            result = await articles_collection.insert_one(article)
            return result.inserted_id, True # Return new ID and True for new article

    async def update_article(self, article: dict):
        """
        Updates an existing article in the database using its _id.
        This is used after NLP enrichment to add new fields.
        """
        if self.db is None:
            await self.connect()

        articles_collection = self.db.articles
        if '_id' in article:
            # We use $set to only update the fields provided in the article dict,
            # leaving other fields untouched.
            await articles_collection.update_one({"_id": article["_id"]}, {"$set": article})
        else:
            print(f"Warning: Cannot update article without an '_id' field: {article.get('title', 'No Title')}")


    async def delete_old_articles(self, retention_days: int):
        """Deletes articles older than retention_days from the database."""
        if self.db is None:
            await self.connect()

        cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=retention_days)
        result = await self.db.articles.delete_many({"published_at": {"$lt": cutoff_date}})
        print(f"  Deleted {result.deleted_count} old articles.")

    async def close(self):
        """Closes the MongoDB client connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            print("MongoDB client closed.")