from telebot.types import Message
from database.common.models import *
from loader import bot


"""Функция выводит последние 10 отелей выданные по запросу пользователя."""


@bot.message_handler(commands=['history'])
def get_history(message: Message):
    retrieved = History.select().where(History.telegram_id == message.from_user.id
                                       and History.user_name == message.from_user.username)
    for element in retrieved[:-11:-1]: # Последние 10 записей
        bot.send_message(message.from_user.id,
                         f"{element.created_at.date()}, {element.city}, {element.command_name}, {element.hotel_name}")
