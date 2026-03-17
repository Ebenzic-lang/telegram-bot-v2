import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== CONFIG =====
BOT_TOKEN = "8540733828:AAFByY8rg8p1kCL95msly_5XoGi40zqlN5g"
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

# ===== AUTO POST TO CHANNEL =====
async def send_to_channel(context):
    text = "🔥 New Drop Alert!\n\nDon't miss today's winning opportunity."

    keyboard = [
        [InlineKeyboardButton("🎰 Play Now", url=PLAY_LINK)]
    ]

    await context.bot.send_message(
        chat_id=CHANNEL_USERNAME,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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

# ===== OFFER (SECURED) =====
async def offer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

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

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(unlock, pattern="unlock"))
    app.add_handler(CallbackQueryHandler(offer, pattern="offer"))

    # ===== SCHEDULER =====
    job_queue = app.job_queue

    # Post to channel every 1 hour
    job_queue.run_repeating(send_to_channel, interval=3600, first=10)

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
