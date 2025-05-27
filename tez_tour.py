import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Словари языков
LANGUAGES = ['Русский 🇷🇺', 'Română 🇷🇴']

MESSAGES = {
    'Русский 🇷🇺': {
        'welcome': 'Добро пожаловать в TEZ TOUR MOLDOVA! Выберите отдел:',
        'departments': ['📞 Отдел продаж', '📊 Бухгалтерия', '📅 Бронирование', '✈️ Чартеры'],
        'managers': {
            '📞 Отдел продаж': (
                "📞 Контакты отдела продаж:\n\n"
                "Людмила – Старший менеджер\n"
                "📱 +37367612221\n\n"
                "Виталий – Менеджер по продажам\n"
                "📱 +37369181461\n\n"
                "Светлана – Менеджер по продажам\n"
                "📱 +37379010791\n\n"
                "Инна – Менеджер по продажам\n"
                "📱 +37369140267\n\n"
                "Общий email отдела: book@teztour.com.md"
            ),
            '📊 Бухгалтерия': (
                "📊 Контакты бухгалтерии:\n\n"
                "📱 022926121\n\n"
                "Email: contabil@teztour.com.md"
            ),
            '📅 Бронирование': (
                "📅 Контакты отдела бронирования:\n\n"
                "📱 022545830\n\n"
                "Email: book@teztour.com.md"
            ),
            '✈️ Чартеры': (
                "✈️ Контакты отдела чартера:\n\n"
                "📱 022545830\n\n"
                "Email: book@teztour.com.md"
            )
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
                "Ludmila – Manager senior\n"
                "📱 +37367612221\n\n"
                "Vitalii – Manager\n"
                "📱 +37369181461\n\n"
                "Svetlana – Manager\n"
                "📱 +37379010791\n\n"
                "Ina – Manager\n"
                "📱 +37369140267\n\n"
                "Email general: book@teztour.com.md\n"
                "Telefon general: 022545830"
            ),
            '📊 Contabilitate': (
                "📊 Contacte contabilitate:\n\n"
                "📱 022926121\n\n"
                "Email: contabil@teztour.com.md"
            ),
            '📅 Rezervări': (
                "📅 Contacte rezervări:\n\n"
                "📱 022545830\n\n"
                "Email: book@teztour.com.md"
            ),
            '✈️ Chartere': (
                "✈️ Contacte chartere:\n\n"
                "📱 022545830\n\n"
                "Email: book@teztour.com.md"
            )
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

async def on_startup(app):
    print("Бот запущен и ожидает вебхуков...")

def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    PORT = int(os.getenv("PORT", "8443"))
    WEBHOOK_URL = f"https://tez-tour-telegram-bot.onrender.com/{BOT_TOKEN}"

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.on_startup(on_startup)

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
