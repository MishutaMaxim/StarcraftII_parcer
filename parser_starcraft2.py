"""
Задание:
Написать скрипт, достающий информацию о игроках в StarСraft II.
Данные для обработки собирать на сайтах:
Данные о призовых: http://aligulac.com/

Что должно быть на выходе:
   - Батч-скрипт, запускающий целевой скрипт на питоне;
   - Сам скрипт на питоне;
   - Папка stats, в который лежит csv файлик с выгруженной статистикой;
   - Папка flags, где лежат флаги стран игроков в структуре {nickname}.png.

Статистику наполнить всеми найденными данными об игроках (ник, имя, команда, дата рождения, возраст,
призовые за карьеру, игровая раса), отобрать ТОП 500 игроков.

APIkey = AeM6fd9sGXyZBOu8vwkE
APIurl = http://aligulac.com/api/v1/
"""

import requests
import json
import csv
import os
from threading import Thread
from time import time

REQUEST_LIMIT = 50  # Ограничения на 1 запрос (оптимально 50-100, другие будут выполняться немного дольше)
DATA_LIMIT = 500  # Общее количество строк, которое нужно получить
API_URL = 'http://aligulac.com/api/v1/player/'  # Адрес для запросов
API_KEY = "AeM6fd9sGXyZBOu8vwkE"  # Ключ для api
API_PARAMS = {"apikey": API_KEY,  # Параметры для запроса
              "current_rating__isnull": "false",
              "order_by": "-current_rating__rating",
              "limit": REQUEST_LIMIT}
FLAGS_URL = 'http://img.aligulac.com/flags/'  # Адрес для флагов
STAT_DIR_NAME = 'stats'  # Папка для таблицы
FLAGS_DIR_NAME = 'flags'  # Папка для флагов
RACE_NAME = {'P': 'Protoss',  # Наименования рас для красоты
             'T': 'Terran',
             'Z': 'Zerg',
             'R': 'random',
             'S': 'race switcher'}


def benchmark(function_to_check_runtime):
    """ Декоратор который выводит время выполнения функции"""
    def wrapper(*args, **kwargs):
        start_time = time()
        function_to_check_runtime(*args, **kwargs)
        run_time = time() - start_time
        print(f">>> Время выполнения: {run_time} сек.")
    return wrapper


def get_data_from_api(api_url: str, api_params: dict, data_limit: int, request_limit: int) -> list:
    """
    Модуль отправляет запросы на API, получает ответ и возвращает список элементов
    :param api_url: Адрес для запросов
    :param api_params: Параметры запросов
    :param data_limit: Общее количество запросов
    :param request_limit: Количество запросов в потоке
    :return: Сырой список с результатами запросов
    """
    try:
        print("Отправили API запрос на сервер, придется подождать ...")
        api_results = []
        # Запускаем потоки
        response_threads = []
        for limit in range(0, data_limit, request_limit):
            th_req = Thread(target=api_request, args=(api_url, api_params, limit, api_results))
            response_threads.append(th_req)
            th_req.start()
        # Ожидаем их завершения
        for thread in response_threads:
            thread.join()
        print("... Ответ обработан")
        return api_results
    except() as error:
        print(f"Ошибка во время запроса: {error}")


def api_request(api_url: str, api_params: dict, offset: int, result_list: list) -> None:
    """
    Функция получает список выполняет запрос к api, выбирает полученные элементы и добавляет их в список
    :param api_params: параметры запроса
    :param api_url: урл запроса
    :param result_list: передаем лист куда складывать результаты
    :param offset: стартовая позиция для выборки
    """
    # формируем параметры для запроса
    params = api_params.copy()
    params.update({"offset": offset})
    # Делаем сам запрос, результаты добавляем в общий список
    request_results = requests.get(api_url, params=params)
    results = json.loads(request_results.text)['objects']
    result_list.extend(results)


def good_connect_to_api(api_url: str, api_key: str) -> bool:
    """
    Проверяем коннект к серверу, если ответ не 200 - кидаем в консоль ошибку
    :param api_url: Адрес апи
    :param api_key: Ключ апи
    :return: статус соединения: True - статус 200; False - статус не 200
    """
    params = {"apikey": api_key}
    connect_status = requests.get(api_url, params=params).status_code
    good_status = connect_status == 200
    if not good_status:
        print(f"Ошибка соединения с сервером. Status code: {connect_status}")
    return good_status


def results_parser(unparsed_list: list, races: dict) -> list:
    """
    Функция парсит список игроков выделяя только нужные данные, затем сортирует по столбцу
    :param races: Список игровых рас
    :param unparsed_list: Сырой список игроков
    :return: Красивый и отсортированный список
    """
    try:
        parsed_list = []
        for row in unparsed_list:
            team = row["current_teams"][0]["team"]["name"] if row["current_teams"] else ''
            result_row = {"Рейтинг": row["current_rating"]["rating"],
                          "Ник": row["tag"],
                          "Имя": row["name"],
                          "Страна": row["country"],
                          "Команда": team,
                          "Дата рождения": row["birthday"],
                          "Призовые за карьеру": row["total_earnings"],
                          "Раса": races[row["race"]]}
            parsed_list.append(result_row)
        parsed_list.sort(key=lambda x: x["Рейтинг"], reverse=True)
        return parsed_list
    except() as error:
        print(f"Ошибка при обработке результатов: {error}")


def make_dir(dir_name: str) -> None:
    """
    Проверяем есть ли нужная папка в директории, создаем если нет.
    :param dir_name: Имя папки
    """
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


@benchmark
def save_stats_file(request_results: list, path_file: str) -> None:
    """
    Модуль принимает список и сохраняет в CSV таблицу
    :param request_results: Список для обработки
    :param path_file: Путь к файлу куда складывать результаты
    """
    try:
        # Создаем папку если это необходимо
        make_dir(path_file)
        print("Записываем статистику в файл")
        with open(f'{path_file}/stats.csv', 'w', newline='', encoding='utf-8') as stats:
            columns_name = request_results[0].keys()
            writer = csv.DictWriter(stats, fieldnames=columns_name, dialect='excel')
            writer.writeheader()
            writer.writerows(request_results)
        print("... Обработка завершена, результат сохранен в каталог " + path_file)
    except() as error:
        print(f"Произошла ошибка при сохранении файла статистики: {error}")


def save_flag(country_name: str, name: str) -> None:
    """
    Функция формирует линк, скачивает картинку и сохраняет в формате nickname.png
    :param country_name: название страны в международном формате
    :param name: Ник игрока
    """
    with open(f"{FLAGS_DIR_NAME}/{name}.png", "wb") as imgfile:
        flag_file = requests.get(f"{FLAGS_URL}{country_name}.png")
        imgfile.write(flag_file.content)


@benchmark
def write_flags_files(request_results: list, path_file: str) -> None:
    """
    Метод получает список элементов, парсит никнейм, регион и передает в функцию сохранения файла.
    :param request_results: Список элементов
    :param path_file: Папка куда сложить файлы
    :return:
    """
    try:
        print("Записываем флаги на диск")
        make_dir(path_file)
        # Перебираем элементы и передаем в функцию параметры для скачивания флага
        save_threads = []
        for row in request_results:
            country = row["Страна"]
            if country:
                file_name = row["Ник"]
                save = Thread(target=save_flag, args=(country.lower(), file_name,))
                save.start()
                save_threads.append(save)
        # Ждем завершения всех потоков
        for thread in save_threads:
            thread.join()
        print("... Обработка флагов завершена, результат сохранен в каталог " + path_file)
    except() as error:
        print(f"Произошла ошибка при сохранении флагов: {error}")


if __name__ == '__main__':
    print("Привет, я скрипт, давай начнем работу.")
    if good_connect_to_api(API_URL, API_KEY):
        api_request_results = get_data_from_api(API_URL, API_PARAMS, DATA_LIMIT, REQUEST_LIMIT)
        if api_request_results and len(api_request_results) == DATA_LIMIT:
            finally_list = results_parser(api_request_results, RACE_NAME)
            if finally_list:
                save_stats_file(finally_list, STAT_DIR_NAME)
                write_flags_files(finally_list, FLAGS_DIR_NAME)
            else:
                print("Пустой список после обработки")
        else:
            print("Пустой/не полный список от сервера")
    print("Я закончил работу, это окно можно закрыть")
