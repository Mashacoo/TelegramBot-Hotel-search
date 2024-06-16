import datetime
from keyboards.reply.choiсe_of_method import choice_of_method
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from loader import bot
from states.request_information import RequestInfo
from telebot.types import Message
from utils.work_funk import print_result, save_history,price_check

"""Цепочка функций для обработки запросов "Новый поиск", "Старт". 

 1. Реализует запросы следующей пользовательской информации:
 - Название города,
 - Дата заезда,
 - Дада выезда,
 - Количество отелей, которые хочет видеть пользователь в каждом запросе,
 - Запрос критерия сортировки отелей( Дешевые, Дорогие, Ближе к центру)
 - Перевод пользователя на новый поиск ( кнопка: "Новый поиск")
  2. Обрабатывает информацию и выводит ответ пользователю (через функцию "choice_meth()")
  """


@bot.message_handler(commands=['new_search'])
def new_search(message: Message) -> None:
    bot.set_state(message.from_user.id, RequestInfo.city, message.chat.id)
    bot.send_message(message.from_user.id, f"В какой город поедите?")


@bot.message_handler(state=RequestInfo.city)
def get_city(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text
        data['hotel_call_dict'] = {}
        data['hotels_request'] = {}
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=datetime.date.today()).build()
    bot.send_message(message.from_user.id, f"Дата заезда?", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(c):
    result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=datetime.date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru',
                                                  min_date=result).build()
        bot.edit_message_text(f"Заезд: {result}",
                              c.message.chat.id,
                              c.message.message_id)

        with bot.retrieve_data(c.from_user.id, c.message.chat.id) as data:
            data['checkin_date'] = result
        bot.send_message(c.from_user.id, f"Дата выезда?", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal(c):
    with bot.retrieve_data(c.from_user.id, c.message.chat.id) as data:
        date_to_add = data['checkin_date']  # отсекаем лишние даты в календаре
    result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=date_to_add).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Выезд {result}",
                              c.message.chat.id,
                              c.message.message_id)

        with bot.retrieve_data(c.from_user.id, c.message.chat.id) as data:
            data['checkout_date'] = result

        bot.send_message(c.from_user.id, f"Сколько отелей показывать?")
        bot.set_state(c.from_user.id, RequestInfo.qaunt_hotels, c.message.chat.id)


@bot.message_handler(state=RequestInfo.qaunt_hotels)
def get_qaunt_hotels(message: Message) -> None:
    bot.send_message(message.from_user.id, f"Какие отели смотрим?", reply_markup=choice_of_method())
    bot.set_state(message.from_user.id, RequestInfo.choice, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['qaunt_hotels'] = message.text


@bot.message_handler(state=RequestInfo.choice)
def choice_meth(message: Message) -> None:

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        city, checkin_date, checkout_date, qaunt_hotels =\
            data['city'], data['checkin_date'], \
            data['checkout_date'], data['qaunt_hotels']

    if message.text == "Подороже":
        res_hp = price_check(city, checkin_date, checkout_date, qaunt_hotels, 'PRICE_HIGH_TO_LOW', message)
        save_history(city=city, command_name="Подороже", res_dict=res_hp, message=message)
        print_result(res_hp, message)

    elif message.text == "Подешевле":
        res_lp = price_check(city, checkin_date, checkout_date, qaunt_hotels, 'PRICE_LOW_TO_HIGH',message)
        save_history(city=city, command_name="Подешевле", res_dict=res_lp, message=message)
        print_result(res_lp, message)

    elif message.text == "Ближе к центру":
        res_bd = price_check(city, checkin_date, checkout_date, qaunt_hotels, 'DISTANCE',message)
        save_history(city=city, command_name="Ближе к центру", res_dict=res_bd, message=message)
        print_result(res_bd, message)

    elif message.text == "Новый поиск":
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotel_call_dict'].clear()
            data['hotels_request'].clear()
        bot.set_state(message.from_user.id, RequestInfo.city, message.chat.id)
        bot.send_message(message.from_user.id, f"В какой город поедите?")
