from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater
from storage.db import get_latest_articles  # a helper you’ll write

def start(update: Update, ctx):
    update.message.reply_text("Welcome! Use /latest or /category <name> to get news.")

def latest(update: Update, ctx):
    articles = get_latest_articles(limit=5)
    for a in articles:
        msg = f"*{a['title']}*\n_{a['summary']}_\n[Read more]({a['url']})"
        update.message.reply_markdown(msg)

def category(update: Update, ctx):
    cat = (ctx.args or ["business"])[0]
    articles = get_latest_articles(category=cat, limit=5)
    # …format and send…

def run_news_bot():
    updater = Updater(TELEGRAM_NEWS_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("latest", latest))
    dp.add_handler(CommandHandler("category", category))
    updater.start_polling()
