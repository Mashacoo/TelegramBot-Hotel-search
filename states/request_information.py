from telebot.handler_backends import State, StatesGroup


class RequestInfo(StatesGroup):

    city = State()
    checkin_date = State()
    checkout_date =State()
    qaunt_hotels = State()
    choice = State()
    photos = State()
    cont_search= State()
    hotel_call_dict = State()
    hotels_request= State()

