from typing import Dict
import json
import requests
from loader import bot
from site_API.utils.api_core import *
from states.request_information import RequestInfo


def api_request(method_endswith: str, params: Dict,method_type: str):
    """Функция осуществяет запрос к сайту:
      method_endswith: Меняется в зависимости от запроса. locations/v3/search либо properties/v2/list
      params: Параметры, если locations/v3/search, то {'q': 'Рига', 'locale': 'ru_RU'}
      method_type: Метод\тип запроса GET\POST """

    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"

    if method_type == 'GET':
        return get_request(
            url=url,
            params=params
        )
    else:
        return post_request(
            url=url,
            params=params
        )


def get_request(url: str, params: Dict):
    """Функция обработки запроса методом "GET" """
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )
        if response.status_code == requests.codes.ok:
            return response.text

    except BaseException as exc:
        print(f'Ошибка:{exc}')


def post_request(url:str, params:Dict):
    """Функция обработки запроса методом "POST" """
    try:
        response = requests.request(
            "POST",
            url,
            headers=headers,
            json=params,
            timeout=15
        )
        if response.status_code == requests.codes.ok:
            return response.text

    except BaseException as exc:
        print(f'Ошибка:{exc}')


def get_region_id(city: str, message):
    """Функция получения ID города
     :returns int """

    try:
        response = api_request(method_endswith='locations/v3/search',
                                  params={"q": city, "locale": "ru_RU"}, method_type='GET')

        search_dict = json.loads(response)
        print(search_dict)
        reg_id = search_dict['sr'][0]['essId']['sourceId']

        return reg_id
    except BaseException as exc:
        print(f'Ошибка:{exc}')
        bot.set_state(message.from_user.id, RequestInfo.city, message.chat.id)
        bot.send_message(message.from_user.id, f"Неверно указали название города. "
                                               f"Давайте попробуем еще раз.\nВ какой город поедите?")


def get_hotel_info(id_hotel:int):

    """Функция получения детальной информации об отеле.
     :returns Dict """

    response = api_request(method_endswith='properties/v2/detail',
                           params={
                                    "currency": "USD",
                                    "eapid": 1,
                                    "locale": "ru_RU",
                                    "propertyId": str(id_hotel)  # Обязательно строку надо передать
                                    },
                           method_type='POST'
                           )
    return response

