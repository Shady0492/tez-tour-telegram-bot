import os
import asyncio
import threading
from flask import Flask
from waitress import serve
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

app = Application.builder().token(TOKEN).build()
flask_app = Flask(__name__)

# Telegram-обработчик
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Это бот TEZ TOUR Moldova!")

app.add_handler(CommandHandler("start", start))

# Flask webhook endpoint
@flask_app.route("/", methods=["GET", "POST"])
def index():
    return "Bot is running on Render!", 200

async def main():
    await app.initialize()

    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/"
        await app.bot.set_webhook(url=webhook_url)
    else:
        await app.start_polling()

    await app.start()
    await app.updater.start_polling()  # Для PTB 20.8, polling fallback
    await app.updater.idle()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, daemon=True).start()

    # ⚠️ Убедись, что порт подхватывается из переменной окружения!
    port = int(os.environ.get("PORT", 10000))

    # Запускаем Telegram-бот
    asyncio.run(main())

    # Запускаем Flask на том же порту, который Render ожидает
    serve(flask_app, host="0.0.0.0", port=port)
