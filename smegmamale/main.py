
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8134096184:AAHJ3sCStLl6hSpM-zD2u26HoKs4J-ktXzA"

# Хранение данных в памяти
habits = ["Спорт", "Чтение", "Вода 2л","Выкурить пачку петро пирвово"]
completions = {}  # {user_id: {date: [habit1, habit2]}}
partners = {}     # {user_id: partner_username}

# Клавиатура с привычками
def get_habits_keyboard():
    return ReplyKeyboardMarkup([[habit] for habit in habits], resize_keyboard=True)

# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n"
        "Я помогу вам и вашему партнёру отслеживать привычки.\n\n"
        "🔹 Выберите привычку, чтобы отметить её выполнение.\n"
        "🔹 Добавьте партнёра: /partner @username",
        reply_markup=get_habits_keyboard()
    )

# Отметка привычки
async def track_habit(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    habit_name = update.message.text
    today = datetime.now().strftime('%Y-%m-%d')

    if habit_name not in habits:
        await update.message.reply_text("❌ Привычка не найдена.")
        return

    if user.id not in completions:
        completions[user.id] = {}

    if today not in completions[user.id]:
        completions[user.id][today] = []

    if habit_name in completions[user.id][today]:
        await update.message.reply_text(f"⚠️ Вы уже отмечали «{habit_name}» сегодня.")
    else:
        completions[user.id][today].append(habit_name)
        await update.message.reply_text(f"✅ «{habit_name}» — отлично! Так держать!")

# Установка партнёра
async def set_partner(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("🚫 Используйте: /partner @username")
        return

    partner_username = context.args[0].lstrip('@')
    partners[user.id] = partner_username
    await update.message.reply_text(
        f"👥 Партнёр @{partner_username} добавлен!\n"
        "Теперь вы можете проверять его прогресс: /check"
    )

# Проверка прогресса партнёра
async def check_partner(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    today = datetime.now().strftime('%Y-%m-%d')

    if user.id not in partners:
        await update.message.reply_text(
            "❌ У вас нет партнёра.\n"
            "Добавьте его: /partner @username"
        )
        return

    partner_username = partners[user.id]
    partner_progress = []

    for uid, data in completions.items():
        if today in data:
            partner_progress.extend(data[today])

    if partner_progress:
        await update.message.reply_text(
            f"📊 Партнёр @{partner_username} сегодня выполнил:\n"
            "• " + "\n• ".join(partner_progress)
        )
    else:
        await update.message.reply_text(
            f"😢 Партнёр @{partner_username} сегодня ничего не отметил.\n"
            "Напомните ему! 😉"
        )

def main() -> None:
    # Создаем Application вместо Updater
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("partner", set_partner))
    application.add_handler(CommandHandler("check", check_partner))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_habit))

    # Запускаем бота
    application.run_polling()
    print("Бот запущен! Остановить: Ctrl+C")

if __name__ == '__main__':
    main()