from telebot import types
from site_API.utils.site_api_handler import *
from database.common.models import *
from loader import bot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict


def price_check(city: str, checkin_date, checkout_date, qaunt_hotels: int, sortik: str, message: Message):

    """Функция:
     1/ формирует список отелей по запросу
     2/ создает каталог фотографий
     3/ оформляет информацию в требуемом виде
     Для избежания потерь информации в случае ошибки встроен механизм подавления исключений.
     :returns
     Dict если функция отработала нормально
     False если пользователь ввел несуществующий город"""

    req_dict_id = {}  # Детализация по каждому отелю
    reg_id = get_region_id(city, message=message)

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",  # Язык запроса, ставлю русский
        "destination": {"regionId": reg_id},
        "checkInDate": {
            "day": checkin_date.day,
            "month": checkin_date.month,
            "year": checkin_date.year
        },
        "checkOutDate": {
            "day": checkout_date.day,
            "month": checkout_date.month,
            "year": checkout_date.year
        },
        "rooms": [
            {
                "adults": 1,
                "children": []
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": int(qaunt_hotels),  # размер выборки
        "sort": str(sortik)  # сортировка
    }
    try:
        response = api_request(method_endswith='properties/v2/list',
                               params=payload,
                               method_type='POST')
        resp_dict = json.loads(response)

        hotel_dict = resp_dict['data']['propertySearch']['properties']  # получаем словарь из отелей по запросу

        for i_hotel in hotel_dict:

            hotel = get_hotel_info(i_hotel['id'])  # делаем отдельный запрос для формирования альбома фотографий
            hotel_details = json.loads(hotel)
            lst_links_photos = []

            for i_dict in hotel_details["data"]["propertyInfo"]["propertyGallery"]["images"]:
                lst_links_photos.append(i_dict["image"]["url"])

            # Подавление всех ошибок, чтобы цикл не прерывался и вся инфа по отелю вывелась.
            req_dict_id[i_hotel['id']] = {}
            list_info = [
                ['Название', 'i_hotel["name"]'],
                ['Рейтинг', 'float(i_hotel["reviews"]["score"])'],
                ['Фото', 'i_hotel["propertyImage"]["image"]["url"]'],
                ['Расстояние до центра, км', 'int(i_hotel["destinationInfo"]["distanceFromDestination"]["value"])'],
                ['Стандартная цена за 1 ночь,$', 'int(i_hotel["price"]["strikeOut"]["amount"])'],
                ['Цена со скидкой за 1 ночь,$', 'int(i_hotel["price"]["lead"]["amount"])'],
                ['Адрес', 'hotel_details["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"]'],
                ['Звезды',
                 'int(hotel_details["data"]["propertyInfo"]["summary"]["overview"][ "propertyRating"]["rating"])'],
                ['Архив_фото', 'lst_links_photos']
            ]
            for info in list_info:
                try:
                    req_dict_id[i_hotel['id']][info[0]] = eval(info[1])

                except BaseException as exc:
                    continue

        return req_dict_id

    except BaseException as exc:
        print(f'Ошибка: {exc}')


def print_result(res_dict:Dict, message: Message):

    """Функция:
     1/ Фильтрует данные полученнного словаря по требуемым критериям,
    2/ Выводит пользователю Основную фотографию(при наличии) и информацию об отеле,
    3/ Формирует кнопку при нажатии на которую пользователь может посмотреть дополнительные фотографии,
     4/ Сохраняет историю запросов в оперативную память, чтобы можно было в рамках одной сессии вызывать
     просмотр фотографий отелей нажатием кнопки "Еще фото"
     """

    filtered_keys = [
        'Название', 'Звезды', 'Рейтинг', 'Адрес', 'Расстояние до центра, км', 'Цена со скидкой за 1 ночь,$',
        'Стандартная цена за 1 ночь,$']

    for num, i_hotel in enumerate(res_dict):

        inform = ''
        for k, v in res_dict[i_hotel].items():
            if k in filtered_keys:
                inform += f'{k}:{res_dict[i_hotel][k]}\n'

        if res_dict[i_hotel].get('Фото', 0) == 0:

            bot.send_message(message.from_user.id, text=f"{inform}")

        else:
            photo_url = str(res_dict[i_hotel]['Фото'])  # обязательно строку

            keyboard = InlineKeyboardMarkup()
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:

                next_num = len(data['hotel_call_dict'])
                keyboard.add(InlineKeyboardButton("Еще фото", callback_data=str(next_num)))

                bot.send_photo(message.chat.id, photo_url, caption=inform, reply_markup=keyboard)

                data['hotel_call_dict'][next_num] = i_hotel
                data['hotels_request'][i_hotel] = (res_dict[i_hotel])

    print(data['hotel_call_dict'])
    print(data['hotels_request'])

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            id_hotel = data['hotel_call_dict'][int(call.data)]
            photos_lst = data['hotels_request'][id_hotel]['Архив_фото']
            media=[]
            for url_photo in photos_lst[:5]:  # по умолчанию поставила 5 фоток выводить
                media.append(types.InputMediaPhoto(media=url_photo))
            bot.send_message(message.from_user.id,f"{data['hotels_request'][id_hotel]['Название']}: ")
            try:
                bot.send_media_group(chat_id=message.from_user.id, media=media)
            except BaseException as exc:
                bot.send_message(message.from_user.id, f"{data['hotels_request'][id_hotel]['Название']}:"
                                                       f"\nДополнительные фото отсутствуют")


def save_history(city: str, command_name: str, res_dict: Dict, message):

    """Функция сохраняет историю поиска в базу данных"""

    base_param = {"command_name": command_name, "city": city,
                  "telegram_id": int(message.from_user.id),"user_name": message.from_user.username}

    for i_hotel in res_dict:
        data = base_param.copy()
        data['hotel_name'] = res_dict[i_hotel]['Название']
        History.create(**data)

