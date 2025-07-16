import logging, openai, requests
from telegram import Update, MessageEntity
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ---------- تنظیمات محیط ----------
BOT_TOKEN = "توکن_ربات_اینجا"
CHANNEL_USERNAME = "EditName_IRAN"
OPENAI_API_KEY = "کلید_OpenAI_اینجا"
MODEL_NAME = "gpt-3.5-turbo"

# ---------- تنظیم لاگ ----------
logging.basicConfig(level=logging.INFO)
openai.api_key = OPENAI_API_KEY

# ---------- تابع تماس با OpenAI ----------
async def ask_openai(user_message: str) -> str:
    system_prompt = (
        "تو یک فمبوی فارسی‌زبان، مهربون، شیطون، و ناز هستی که با لحنی صمیمی و غیررسمی با کاربر حرف می‌زنه. "
        "شوخی می‌کنی، گاهی ایموجی می‌ذاری، و جوری حرف می‌زنی که انگار با دوست صمیمیت صحبت می‌کنی. "
        "تا حد امکان پاسخ‌هات رو خودتونی و جذاب بده."
    )

    try:
        completion = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.95,
        )
        return completion["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        return "اوه اوه! مشکلی پیش اومده 😢 بعداً بیا دوباره امتحان کن!"

# ---------- بررسی عضویت در کانال ----------
async def is_member(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}"
    try:
        r = requests.get(url).json()
        return r.get("result", {}).get("status", "") in ["member", "administrator", "creator"]
    except:
        return False

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام خوشگل 😋 اول عضو کانال @EditName_IRAN شو تا با هم حرف بزنیم 💖")

# ---------- پاسخ به پیام‌ها ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user

    if not await is_member(user.id):
        await msg.reply_text("✨ اول عضو کانال @EditName_IRAN شو عزیز دلم 😘")
        return

    is_reply = msg.reply_to_message and msg.reply_to_message.from_user.username == "Arta_femboy_bot"
    mentioned = any(ent.type == MessageEntity.MENTION and "@arta_femboy_bot" in msg.text.lower() for ent in msg.entities or [])

    if msg.chat.type == "private" or is_reply or mentioned or "فمبوی" in msg.text.lower():
        user_msg = msg.text.replace("@arta_femboy_bot", "").strip()
        response = await ask_openai(user_msg)
        await msg.reply_text(response)

# ---------- اجرای ربات ----------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 ربات فمبوی به ChatGPT متصل شد!")
    app.run_polling()
