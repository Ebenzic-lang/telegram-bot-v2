import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# ===== CONFIG =====
BOT_TOKEN = "8540733828:AAG1Rga-VZ89xwR2_mJHTmZmTc40smGrBsg"
CHANNEL_USERNAME = "@Chealseanews"

PLAY_LINK = "https://yourtrackinglink.com/play"
OFFER_LINK = "https://yourtrackinglink.com/offer"

# ===== STORAGE =====
users_db = {}
clicks_db = {}

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO)

# ===== HELPER =====
async def is_user_joined(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ===== FOLLOW-UP SYSTEM =====
async def follow_up_1(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data

    await context.bot.send_message(
        chat_id=user_id,
        text="⏳ Many users are already claiming today's offer...\nDon't miss out 👇"
    )

async def follow_up_2(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data

    await context.bot.send_message(
        chat_id=user_id,
        text="⚠️ Last chance today!\nThis offer may expire soon 👇"
    )

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # SAVE USER
    users_db[user_id] = True

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

        # SCHEDULE FOLLOW UPS
        context.job_queue.run_once(follow_up_1, 120, data=user_id)
        context.job_queue.run_once(follow_up_2, 600, data=user_id)

        keyboard = [
            [InlineKeyboardButton("🎰 Play Now", callback_data="play")],
            [InlineKeyboardButton("🎁 Offer", callback_data="offer")]
        ]

        await query.edit_message_text(
            "✅ Access unlocked!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.answer("❌ Join the channel first!", show_alert=True)

# ===== PLAY (TRACK CLICKS) =====
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # TRACK CLICK
    clicks_db[user_id] = clicks_db.get(user_id, 0) + 1

    keyboard = [
        [InlineKeyboardButton("🎰 Continue", url=PLAY_LINK)]
    ]

    await query.message.reply_text(
        "🔥 Click below to continue:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== OFFER =====
async def offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🎰 Play Now", url=PLAY_LINK)]
    ]

    await query.message.reply_text(
        "🎁 Special offer available now 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== BROADCAST COMMAND =====
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = " ".join(context.args)

    if not message:
        await update.message.reply_text("Usage: /broadcast your message")
        return

    for user_id in users_db:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
        except:
            pass

    await update.message.reply_text("✅ Broadcast sent!")

# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))

    app.add_handler(CallbackQueryHandler(unlock, pattern="unlock"))
    app.add_handler(CallbackQueryHandler(play, pattern="play"))
    app.add_handler(CallbackQueryHandler(offer, pattern="offer"))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
