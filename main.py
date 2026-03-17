import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== CONFIG =====
BOT_TOKEN = "8540733828:AAHqB3b7h0k0cmKIaS6m2zhg5lByv0_5waU"
CHANNEL_USERNAME = "@Chealseanews"

PLAY_LINK = "https://yourtrackinglink.com/play"
OFFER_LINK = "https://yourtrackinglink.com/offer"

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
        [InlineKeyboardButton("🔓 I Joined", callback_data="unlock")]
    ]

    await update.message.reply_text(
        "👋 Welcome!\n\nJoin the channel to unlock access.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== UNLOCK =====
async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)

        if member.status in ["member", "administrator", "creator"]:
            keyboard = [
                [InlineKeyboardButton("🎰 Play Now", url=PLAY_LINK)],
                [InlineKeyboardButton("🎁 Offer", url=OFFER_LINK)]
            ]

            await query.edit_message_text(
                "✅ Access unlocked!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.answer("❌ Join the channel first!", show_alert=True)

    except Exception as e:
        await query.message.reply_text("⚠️ Error. Try again.")

# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(unlock, pattern="unlock"))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
