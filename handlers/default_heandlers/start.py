from telebot.types import Message
from loader import bot
from states.request_information import RequestInfo


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.full_name}!\n Я помогу тебе спланировать поездку.")
    bot.send_message(message.from_user.id, f"В какой город поедите?")
    bot.set_state(message.from_user.id, RequestInfo.city, message.chat.id)

