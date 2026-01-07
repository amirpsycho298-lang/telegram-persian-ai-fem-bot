import requests
from datetime import date
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = "AAFi6Bwx6cBwiETlTOzFe2NbmFUl47hrwOY"
HF_TOKEN = "MmGfUGXwdTJCpSdsozEWVIZJfbtpGnXxam"
ADMIN_ID = 8569184435
DAILY_LIMIT = 20
MODEL = "mistralai/Mistral-7B-Instruct"

user_usage = {}

def can_use(user_id):
    today = date.today()

    if user_id == ADMIN_ID:
        return True

    if user_id not in user_usage or user_usage[user_id]["date"] != today:
        user_usage[user_id] = {"count": 0, "date": today}

    if user_usage[user_id]["count"] >= DAILY_LIMIT:
        return False

    user_usage[user_id]["count"] += 1
    return True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if not can_use(user_id):
        await update.message.reply_text(
            "❌ سقف استفاده امروزت تموم شده\n"
            "⏳ فردا دوباره ۲۰ پیام داری"
        )
        return

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    payload = {
        "inputs": f"به فارسی و لحن خودمونی جواب بده:\n{text}",
        "parameters": {"max_new_tokens": 200}
    }

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{MODEL}",
        headers=headers,
        json=payload
    )

    result = response.json()

    try:
        reply = result[0]["generated_text"]
    except:
        reply = "⚠️ الان سرور شلوغه، بعداً دوباره امتحان کن"

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
