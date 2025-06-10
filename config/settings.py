import os
import os
from dotenv import load_dotenv


TELEGRAM_NEWS_TOKEN = "8094377979:AAGFs-xQaKzkmqbNjiSJ0moTbA-lqx010kg"
TELEGRAM_ADVISOR_TOKEN = "7303509852:AAFvGx2CDrscGvjxJT5MoHIwezyha9hH4Fs"

# config/settings.py
# config/settings.py


# Load environment variables from .env file
load_dotenv()

# MongoDB Settings
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "biz_intel_db")

# NewsAPI Settings
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_KEYWORDS_STR = os.getenv("NEWS_KEYWORDS", "business intelligence, data analytics, market trends, geopolitics, crypto")
NEWS_KEYWORDS = [kw.strip() for kw in NEWS_KEYWORDS_STR.split(',')] if NEWS_KEYWORDS_STR else []

# Agent Configuration
FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES", 5))
NEWS_RETENTION_DAYS = int(os.getenv("NEWS_RETENTION_DAYS", 30))
CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", 24))

# --- NEW: Classification & Scoring Settings ---
# Zero-Shot Topic Classification Labels
TOPIC_LABELS = ["Technology", "Business", "Finance", "Geopolitics", "Health", "AI", "Cryptocurrency", "Economics", "Politics", "Environment"]

# Sector/Subsector Glossary (Add more as needed)
SECTOR_GLOSSARY = {
    "cloud": ["AWS", "Azure", "GCP", "cloud computing", "serverless"],
    "crypto": ["bitcoin", "ethereum", "stablecoin", "blockchain", "NFT", "DeFi", "crypto currency", "cryptocurrency"],
    "saas": ["SaaS", "subscription service", "cloud software", "software as a service"],
    "biotech": ["biotech", "biotechnology", "gene editing", "CRISPR", "pharmaceutical"],
    "fintech": ["fintech", "payment processing", "digital banking", "insurtech"],
    "e-commerce": ["e-commerce", "online retail", "shopify", "amazon"],
    "cybersecurity": ["cybersecurity", "data breach", "malware", "ransomware", "security"],
    "renewable_energy": ["solar", "wind power", "geothermal", "green energy", "renewable energy"],
    "automotive": ["automotive", "electric vehicle", "EV", "tesla", "ford", "general motors"],
    "real_estate": ["real estate", "property market", "housing market", "commercial real estate"],
}

# Weights for Composite Priority Score
PRIORITY_WEIGHTS = {
    "importance": 0.4,
    "relevance": 0.3,
    "actionable": 0.2,
    "urgency": 0.1
}

# Default User Profile Thresholds (Can be loaded dynamically later)
DEFAULT_USER_PROFILE = {
    "min_relevance": 0.5,
    "min_importance": 0.5,
    "min_date_days": 7, # Filter articles published within the last 7 days
    "interested_topics": ["Technology", "Finance", "AI", "Cryptocurrency"],
    "interested_sectors": ["cloud", "crypto", "saas"],
    "sentiment_preference": "positive" # Or "neutral", "negative", "any"
}

# --- END NEW SETTINGS ---


# Basic validation for critical keys
if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY environment variable not set.")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable not set.")