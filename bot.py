import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN topilmadi!")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY topilmadi!")

SYSTEM_PROMPT = """Men Islomovman. Har qanday savolingizga o'zbek tilida do'stona va rasmiy javob beraman."""

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    bot_username = context.bot.username
    is_private = message.chat.type == "private"
    is_mentioned = f"@{bot_username}" in (message.text or "")
    is_reply_to_bot = (
        message.reply_to_message and
        message.reply_to_message.from_user and
        message.reply_to_message.from_user.username == bot_username
    )

    if not is_private and not is_mentioned and not is_reply_to_bot:
        return

    user_text = message.text.replace(f"@{bot_username}", "").strip()

    try:
        await context.bot.send_chat_action(chat_id=message.chat_id, action="typing")
        full_prompt = f"{SYSTEM_PROMPT}\n\nFoydalanuvchi: {user_text}"
        response = model.generate_content(full_prompt)
        reply = response.text
    except Exception as e:
        reply = "Kechirasiz, hozir xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
        logging.error(f"Xato: {e}")

    await message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot ishga tushdi!")
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
