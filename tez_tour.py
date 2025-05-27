import os
import asyncio
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- ЯЗЫКОВЫЕ НАСТРОЙКИ ---

LANGUAGES = ['Русский 🇷🇺', 'Română 🇷🇴']

MESSAGES = {
    'Русский 🇷🇺': {
        'welcome': 'Добро пожаловать в TEZ TOUR MOLDOVA! Выберите отдел:',
        'departments': ['📞 Отдел продаж', '📊 Бухгалтерия', '📅 Бронирование', '✈️ Чартеры'],
        'managers': {
            '📞 Отдел продаж': (
                "📞 Контакты отдела продаж:\n\n"
                "Людмила – Старший менеджер\n📱 +37367612221\n\n"
                "Виталий – Менеджер по продажам\n📱 +37369181461\n\n"
                "Светлана – Менеджер по продажам\n📱 +37379010791\n\n"
                "Инна – Менеджер по продажам\n📱 +37369140267\n\n"
                "Email отдела: book@teztour.com.md"
            ),
            '📊 Бухгалтерия': (
                "📊 Контакты бухгалтерии:\n📱 022926121\nEmail: contabil@teztour.com.md"
            ),
            '📅 Бронирование': (
                "📅 Контакты бронирования:\n📱 022545830\nEmail: book@teztour.com.md"
            ),
            '✈️ Чартеры': (
                "✈️ Контакты отдела чартера:\n📱 022545830\nEmail: book@teztour.com.md"
            ),
        },
        'back': '🔙 Назад',
        'language_prompt': 'Выберите язык / Select language:'
    },
    'Română 🇷🇴': {
        'welcome': 'Bine ați venit la TEZ TOUR MOLDOVA! Alegeți un departament:',
        'departments': ['📞 Vânzări', '📊 Contabilitate', '📅 Rezervări', '✈️ Chartere'],
        'managers': {
            '📞 Vânzări': (
                "📞 Contacte Vânzări:\n\n"
                "Ludmila – Manager senior\n📱 +37367612221\n\n"
                "Vitalii – Manager\n📱 +37369181461\n\n"
                "Svetlana – Manager\n📱 +37379010791\n\n"
                "Ina – Manager\n📱 +37369140267\n\n"
                "Email: book@teztour.com.md"
            ),
            '📊 Contabilitate': (
                "📊 Contacte contabilitate:\n📱 022926121\nEmail: contabil@teztour.com.md"
            ),
            '📅 Rezervări': (
                "📅 Contacte rezervări:\n📱 022545830\nEmail: book@teztour.com.md"
            ),
            '✈️ Chartere': (
                "✈️ Contacte chartere:\n📱 022545830\nEmail: book@teztour.com.md"
            ),
        },
        'back': '🔙 Înapoi',
        'language_prompt': 'Alegeți limba / Choose language:'
    }
}

user_lang = {}

def get_keyboard(language):
    buttons = MESSAGES[language]['departments']
    return ReplyKeyboardMarkup(
        [[btn] for btn in buttons] + [[MESSAGES[language]['back']]],
        resize_keyboard=True
    )

# --- ОБРАБОТЧИКИ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(lang)] for lang in LANGUAGES],
        resize_keyboard=True
    )
    await update.message.reply_text("Выберите язык / Alegeți limba:", reply_markup=keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text in LANGUAGES:
        user_lang[user_id] = text
        await update.message.reply_text(
            MESSAGES[text]['welcome'],
            reply_markup=get_keyboard(text)
        )
        return

    if user_id not in user_lang:
        await update.message.reply_text("Пожалуйста, выберите язык / Alegeți limba.")
        return

    lang = user_lang[user_id]
    if text == MESSAGES[lang]['back']:
        await start(update, context)
        return

    managers = MESSAGES[lang]['managers']
    if text in managers:
        await update.message.reply_text(managers[text])
    else:
        await update.message.reply_text(MESSAGES[lang]['welcome'], reply_markup=get_keyboard(lang))


# --- Flask сервер ---

flask_app = Flask(__name__)
application = None  # глобальная переменная для telegram Application

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    if application is None:
        return "Application not initialized", 500

    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.create_task(application.update_queue.put(update))
    return "OK"

async def main():
    global application

    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN not set in environment variables")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Устанавливаем webhook
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        raise ValueError("RENDER_EXTERNAL_URL not set in environment variables")
    webhook_url = f"{url}/webhook"
    await application.bot.set_webhook(webhook_url)

    # Запускаем бота (без polling)
    await application.initialize()
    await application.start()
    print(f"Bot started with webhook {webhook_url}")

if __name__ == "__main__":
    import waitress
    import threading

    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, daemon=True).start()

    asyncio.run(main())
    waitress.serve(flask_app, host="0.0.0.0", port)
