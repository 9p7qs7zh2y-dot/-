import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import os

# Получаем токен из переменных окружения Render
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8237220454:AAHIs1zJ_h2db7tbPFu7DJWTpp9_PwoLOls")

bot = telebot.TeleBot(BOT_TOKEN)

# Кнопка запуска мини-приложения
game_button = KeyboardButton(
    text="🐨 Тапать!",
    web_app=WebAppInfo(url="https://9p7qs7zh2y-dot.github.io/vallid/")
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """🐨 KOALA × TAP × KOALA

🍃 Факт о коалах:
Коалы спят до 22 часов в день — они настоящие эксперты по энергосбережению.

Что умеет этот бот?
🐨 Кормить эвкалиптом
🐨 Соревноваться
🐨 Прокачивать коалу

Присоединяйся и нажимай «Старт», чтобы начать тапать!

✅ Нажми на кнопку ниже, чтобы играть"""

    play_button = KeyboardButton(
        text="🐨 Играть",
        web_app=WebAppInfo(url="https://9p7qs7zh2y-dot.github.io/vallid/")
    )
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(play_button)
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """📚 Доступные команды:

/start - начать игру с коалами
/help - эта справка

💡 Просто нажми «🐨 Играть» и тапай по коале!"""
    
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(func=lambda message: True)
def handle_other(message):
    response = f"""🍃 Добро пожаловать, {message.from_user.first_name}!

Твоя коала уже ждёт эвкалипт.
Нажми на кнопку ниже, чтобы начать тапать!"""
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(game_button)
    
    bot.send_message(message.chat.id, response, reply_markup=keyboard)

if __name__ == "__main__":
    print('✅ Бот-коала запущен!')
    # Удаляем старый webhook перед запуском
    bot.remove_webhook()
    # Запускаем polling (на Render работает)
    bot.infinity_polling(skip_pending=True)