import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Весь твой словарь и функции (оставим как у тебя)

LANGUAGES = ['Русский 🇷🇺', 'Română 🇷🇴']

MESSAGES = {
    'Русский 🇷🇺': {
        'welcome': 'Добро пожаловать в TEZ TOUR MOLDOVA! Выберите отдел:',
        'departments': ['📞 Отдел продаж', '📊 Бухгалтерия', '📅 Бронирование', '✈️ Чартеры'],
        'managers': {
            '📞 Отдел продаж': "📞 Контакты отдела продаж: ...",  # сократил для примера
            '📊 Бухгалтерия': "📊 Контакты бухгалтерии: ...",
            '📅 Бронирование': "📅 Контакты отдела бронирования: ...",
            '✈️ Чартеры': "✈️ Контакты отдела чартера: ...",
        },
        'back': '🔙 Назад',
        'language_prompt': 'Выберите язык / Select language:'
    },
    'Română 🇷🇴': {
        # Аналогично
    }
}

user_lang = {}

def get_keyboard(language):
    buttons = MESSAGES[language]['departments']
    return ReplyKeyboardMarkup([[btn] for btn in buttons] + [[MESSAGES[language]['back']]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup([[KeyboardButton(lang)] for lang in LANGUAGES], resize_keyboard=True)
    await update.message.reply_text("Выберите язык / Alegeți limba:", reply_markup=keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text in LANGUAGES:
        user_lang[user_id] = text
        await update.message.reply_text(MESSAGES[text]['welcome'], reply_markup=get_keyboard(text))
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

def main():
    TOKEN = os.getenv("BOT_TOKEN")  # читаем токен из переменной окружения
    if not TOKEN:
        print("Error: BOT_TOKEN not set in environment variables")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
