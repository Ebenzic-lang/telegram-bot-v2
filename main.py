import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== CONFIG =====
BOT_TOKEN = "8540733828:AAGl8jMF8UDckUauFMeq8cRX91SSQMl75kk"
CHANNEL_USERNAME = "@Chealseanews"

PLAY_LINK = "https://yourtrackinglink.com/play"
OFFER_LINK = "https://yourtrackinglink.com/offer"

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO)

# ===== HELPER FUNCTION (ANTI-BYPASS) =====
async def is_user_joined(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

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

    joined = await is_user_joined(context, user_id)

    if joined:
        keyboard = [
            [InlineKeyboardButton("🎰 Play Now", url=PLAY_LINK)],
            [InlineKeyboardButton("🎁 Offer", callback_data="offer")]
        ]

        await query.edit_message_text(
            "✅ Access unlocked!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.answer("❌ Join the channel first!", show_alert=True)

# ===== OFFER (NOW SECURED) =====
async def offer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # 🔐 CHECK AGAIN (ANTI-BYPASS)
    joined = await is_user_joined(context, user_id)

    if not joined:
        await query.message.reply_text("❌ You must join the channel first.")
        return

    keyboard = [
        [InlineKeyboardButton("🎰 Play Now", url=PLAY_LINK)]
    ]

    await query.message.reply_text(
        "🎁 *Today's Special Offer*\n\nTap below to start.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(unlock, pattern="unlock"))
    app.add_handler(CallbackQueryHandler(offer, pattern="offer"))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
