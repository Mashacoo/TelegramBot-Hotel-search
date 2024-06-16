from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def choice_of_method()-> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True,True)
    bt1 = KeyboardButton("Подороже")
    bt2 = KeyboardButton("Подешевле")
    bt3 = KeyboardButton("Ближе к центру")
    bt_new= KeyboardButton("Новый поиск")
    keyboard.add(bt1, bt2, bt3,bt_new)
    return keyboard



