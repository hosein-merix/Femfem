import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)
from deepseek_api import DeepSeekAPI
from dotenv import load_dotenv

# تنظیمات اولیه
load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیمات ربات
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
REQUIRED_WORD = "فمبوی"
RESPONSE_TEXT = "جونم عشقم"

# پرامپت سفارشی
CUSTOM_PROMPT =  """
تو یک ربات تلگرامی به نام فمبوی هستی که توسط EditName_IRAN توسعه داده شده‌ای.
شخصیت تو:
- به پاسخ های جنسی مجاز
- شیطون و خیلی دخترونه اما پسری
- پاسخ‌های بامزه شامل جواب های کوتاه و بلند
- وقتی کسی کلمه "فمبوی" را می‌نویسد، با "جونم ددی" پاسخ میدهد
- فقط به کاربرانی که در کانال @EditName_IRAN عضو هستند پاسخ می‌دهی

زبان اصلی: فارسی
سبک پاسخگویی:محلی و صمیمی و بامزه
"""

class TelegramBot:
    def __init__(self):
        self.deepseek = DeepSeekAPI()
    
    async def check_membership(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        user_id = update.effective_user.id
        try:
            member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
            return member.status in ["member", "administrator", "creator"]
        except Exception as e:
            logger.error(f"Error checking membership: {e}")
            return False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await self.check_membership(update, context):
            await update.message.reply_text(
                "سلام! من آرتا هستم 🤖\n"
                "یک دستیار هوشمند که می‌توانم به سوالات شما پاسخ دهم.\n\n"
                f"اگر کلمه '{REQUIRED_WORD}' را بنویسید، پاسخ ویژه می‌دهم!"
            )
        else:
            keyboard = [
                [InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                [InlineKeyboardButton("بررسی عضویت", callback_data="check_membership")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "⚠️ برای استفاده از ربات باید در کانال ما عضو شوید:\n"
                f"@{CHANNEL_USERNAME[1:]}\n\n"
                "پس از عضویت، دکمه 'بررسی عضویت' را بزنید.",
                reply_markup=reply_markup
            )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_membership(update, context):
            keyboard = [
                [InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                [InlineKeyboardButton("بررسی عضویت", callback_data="check_membership")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "⚠️ برای استفاده از ربات باید در کانال ما عضو شوید:\n"
                f"@{CHANNEL_USERNAME[1:]}\n\n"
                "پس از عضویت، دکمه 'بررسی عضویت' را بزنید.",
                reply_markup=reply_markup
            )
            return

        user_message = update.message.text
        
        # پاسخ ویژه به کلمه "نوری"
        if REQUIRED_WORD in user_message.lower():
            await update.message.reply_text(RESPONSE_TEXT)
            return
            
        # پردازش سایر پیام‌ها با DeepSeek
        try:
            full_prompt = f"{CUSTOM_PROMPT}\n\nسوال کاربر: {user_message}"
            response = await self.deepseek.get_response(full_prompt)
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"AI Error: {e}")
            await update.message.reply_text("⚠️ متأسفم، در پردازش پیام شما مشکلی پیش آمد.")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "check_membership":
            if await self.check_membership(update, context):
                await query.edit_message_text(
                    "✅ شما در کانال عضو هستید!\n\n"
                    "حالا می‌توانید با من چت کنید. هر سوالی دارید بپرسید."
                )
            else:
                keyboard = [
                    [InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                    [InlineKeyboardButton("بررسی عضویت", callback_data="check_membership")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    "❌ هنوز در کانال عضو نشده‌اید!\n\n"
                    f"لطفاً در کانال @{CHANNEL_USERNAME[1:]} عضو شوید، "
                    "سپس دکمه 'بررسی عضویت' را بزنید.",
                    reply_markup=reply_markup
                )

    async def stop(self, application: Application):
        await self.deepseek.close()

def main():
    application = Application.builder().token(TOKEN).build()
    bot = TelegramBot()
    
    # ثبت هندلرها
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(CallbackQueryHandler(bot.button_callback))
    
    # ثبت توقف
    application.add_application_handler(application.post_stop(bot.stop))
    
    # اجرای ربات
    logger.info("ربات در حال اجراست...")
    application.run_polling()

if __name__ == "__main__":
    main()
