def advice(update: Update, ctx):
    recs = get_latest_recommendations(user_id=USER_PROFILE['name'], limit=3)
    for r in recs:
        msg = f"💡 *{r['opportunity_type']}* in {r['sector']}\n{r['summary']}\n_Action:_ {r['action']}"
        update.message.reply_markdown(msg)

def profile(update: Update, ctx):
    # show or allow edits to your USER_PROFILE

def run_advisor_bot():
    updater = Updater(TELEGRAM_ADVISOR_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("advice", advice))
    dp.add_handler(CommandHandler("profile", profile))
    updater.start_polling()
