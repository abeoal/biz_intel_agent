# analyzer/ranking_filter.py
import datetime
from config import settings

def bucket_score(score: float) -> str:
    """Buckets a continuous score into High, Medium, Low."""
    if score >= 0.75: return "High"
    if score >= 0.4:  return "Medium"
    return "Low"

def filter_article(article: dict, user_profile: dict) -> bool:
    """
    Applies hard filters based on user profile thresholds.
    Assumes article has 'scores' and 'published_at' (datetime object).
    """
    # Check score thresholds
    if article.get("scores", {}).get("relevance", 0.0) < user_profile.get("min_relevance", 0.0):
        return False
    if article.get("scores", {}).get("importance", 0.0) < user_profile.get("min_importance", 0.0):
        return False

    # Check publication date
    if "published_at" in article and isinstance(article["published_at"], datetime.datetime):
        min_date = datetime.datetime.now(datetime.timezone.utc) - \
                   datetime.timedelta(days=user_profile.get("min_date_days", 7))
        if article["published_at"] < min_date:
            return False
    else:
        # If published_at is missing or not a datetime, skip filtering by date
        pass # Or decide to return False if published_at is mandatory

    # Check interested topics (if specified in profile)
    if user_profile.get("interested_topics") and article.get("Topic"):
        if article["Topic"] not in user_profile["interested_topics"]:
            return False

    # Check interested sectors (if specified in profile)
    if user_profile.get("interested_sectors") and article.get("Sectors"):
        if not any(sector in user_profile["interested_sectors"] for sector in article["Sectors"]):
            return False

    # Check sentiment preference
    if user_profile.get("sentiment_preference") and user_profile["sentiment_preference"] != "any":
        if article.get("Sentiment", {}).get("label") != user_profile["sentiment_preference"]:
            return False

    return True

def priority_score(scores: dict) -> float:
    """Computes a composite priority score based on weighted individual scores."""
    total_score = 0.0
    for key, weight in settings.PRIORITY_WEIGHTS.items():
        total_score += scores.get(key, 0.0) * weight
    return total_score

def suggest_action(article: dict) -> str:
    """
    Suggests an action based on article classification and scores.
    This is a rule-based example, can be expanded.
    """
    sentiment_label = article.get("Sentiment", {}).get("label", "neutral")
    topic = article.get("Topic", "Unknown")
    urgency = article.get("Urgency", "Low") # Bucketed urgency

    if urgency == "High" and sentiment_label == "negative":
        return "Monitor Closely (High Urgency, Negative)"
    elif urgency == "High" and sentiment_label == "positive":
        return "Investigate Opportunity (High Urgency, Positive)"
    elif "Finance" in topic and article.get("scores", {}).get("actionable", 0.0) > 0.6:
        return "Consider Investment (Actionable Finance)"
    elif "crypto" in article.get("Sectors", []):
        return "Monitor Crypto Market"
    elif "AI" in topic and sentiment_label == "positive":
        return "Explore AI Trends"
    else:
        return "Monitor (General)"