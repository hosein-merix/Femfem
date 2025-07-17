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

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیمات ربات
BOT_TOKEN = "8036736810:AAEARzlKaVmm1udMsShJyLDIyiP7fHnfcIk"
CHANNEL_USERNAME = "@EditName_IRAN"  # بدون @
CHANNEL_LINK = "https://t.me/EditName_IRAN"
REQUIRED_WORD = "نوری"
RESPONSE_TEXT = "نور علی نور 💡"

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """بررسی آیا کاربر در کانال عضو شده است یا نه"""
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command"""
    user = update.effective_user
    
    if await check_membership(update, context):
        await update.message.reply_text(
            f"سلام {user.first_name}! 👋\n"
            "خوش آمدید! شما در کانال عضو هستید.\n"
            f"اگر کلمه '{REQUIRED_WORD}' را بنویسید، پاسخ می‌دهم."
        )
    else:
        keyboard = [
            [InlineKeyboardButton("عضویت در کانال", url=CHANNEL_LINK)],
            [InlineKeyboardButton("بررسی عضویت", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"سلام {user.first_name}! 👋\n"
            "برای استفاده از ربات باید در کانال ما عضو شوید:\n"
            f"{CHANNEL_LINK}\n"
            "پس از عضویت، دکمه 'بررسی عضویت' را بزنید.",
            reply_markup=reply_markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام‌های دریافتی"""
    if not await check_membership(update, context):
        keyboard = [
            [InlineKeyboardButton("عضویت در کانال", url=CHANNEL_LINK)],
            [InlineKeyboardButton("بررسی عضویت", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚠️ برای استفاده از ربات باید در کانال ما عضو شوید:\n"
            f"{CHANNEL_LINK}\n"
            "پس از عضویت، دکمه 'بررسی عضویت' را بزنید.",
            reply_markup=reply_markup
        )
        return
    
    user_message = update.message.text
    if user_message and REQUIRED_WORD in user_message:
        await update.message.reply_text(RESPONSE_TEXT)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش کلیک روی دکمه‌های اینلاین"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_membership":
        if await check_membership(update, context):
            await query.edit_message_text(
                "✅ شما در کانال عضو هستید!\n"
                f"حالا می‌توانید کلمه '{REQUIRED_WORD}' را بنویسید تا پاسخ دهم."
            )
        else:
            keyboard = [
                [InlineKeyboardButton("عضویت در کانال", url=CHANNEL_LINK)],
                [InlineKeyboardButton("بررسی عضویت", callback_data="check_membership")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "❌ هنوز در کانال عضو نشده‌اید!\n"
                f"لطفاً در کانال عضو شوید: {CHANNEL_LINK}\n"
                "سپس دکمه 'بررسی عضویت' را بزنید.",
                reply_markup=reply_markup
            )

def main():
    """راه‌اندازی ربات"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ثبت هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # اجرای ربات
    application.run_polling()

if __name__ == "__main__":
    main()
