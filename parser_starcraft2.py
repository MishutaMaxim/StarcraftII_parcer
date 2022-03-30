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
призовые за карьеру, игровая расса), отобрать ТОП 500 игроков.

APIkey = AeM6fd9sGXyZBOu8vwkE
APIurl = http://aligulac.com/api/v1/
"""

import requests
import json
import csv
import os
from threading import Thread
from time import time

from parser_params import *

RACE_NAME = {'P': 'Protoss',
             'T': 'Terran',
             'Z': 'Zerg',
             'R': 'random',
             'S': 'race switcher'}


def results_from_api():
    """
    Модуль отправляет запросы на API, получает ответ и возвращает список элементов
    """
    def api_request(offset):
        """
        Функция выполняет запрос к api, выбирает полученные элементы и добавляет их в общий список
        :param offset: стартовая позиция для выборки
        """
        # формируем параметры для запроса
        params = API_PARAMS.copy()
        params.update({"offset": offset})
        # Делаем сам запрос, результаты добавляем в общий список
        request_results = requests.get(API_URL, params=params)
        results = json.loads(request_results.text)['objects']
        for row in results:
            teams = row["current_teams"][0]["team"]["name"] if row["current_teams"] else ''
            result_row = [row["current_rating"]["rating"],
                          row["tag"],
                          row["name"],
                          row["country"],
                          teams,
                          row["birthday"],
                          row["total_earnings"],
                          RACE_NAME[row["race"]]]
            extract_results.append(result_row)

    # Объявляем общий список с результатами и список потоков
    extract_results = []
    response_threads = []
    print("Отправили API запрос на сервер, придется подождать ...")
    start_time = time()
    # Запускаем потоки
    for limit in range(0, DATA_LIMIT, REQUEST_LIMIT):
        th_req = Thread(target=api_request, args=(limit,))
        response_threads.append(th_req)
        th_req.start()
    # Ожидаем их завершения
    for thread in response_threads:
        thread.join()
    print(f"Ответ обработан, это заняло {time() - start_time} сек.")
    extract_results = sorted(extract_results, key=lambda x: x[0], reverse=True)
    return extract_results


def write_to_file_stats(request_results: list, path_file) -> None:
    """
    Модуль принимает список, парсит из него нужные данные и сохраняет в CSV файл
    :param request_results: Список для обработки
    :param path_file: Путь к файлу куда складывать результаты
    """
    # Формируем названия столбцов таблицы
    csv_columns = ("Рейтинг", "Ник", "Имя", "Страна", "Команда", "Дата рождения", "Призовые за карьеру", "Раса")
    # Создаем папку если это необходимо
    if not os.path.exists(path_file):
        os.mkdir(path_file)
    # Записываем данные в файл
    with open(f'{path_file}/stats.csv', 'w', newline='', encoding='utf-8') as stats:
        writer = csv.writer(stats, dialect='excel')
        writer.writerow(csv_columns)
        writer.writerows(request_results)
    print("Обработка результата завершена, результат сохранен в каталог " + path_file)


def write_to_file_flags(request_results: list, path_file):
    """
    Метод получает список элементов, парсит никнейм ,регион и передает в функцию сохранения файла.
    :param request_results: Список элементов
    :param path_file: Папка куда сложить файлики
    :return:
    """
    def save_flag(country_name: str, name: str):
        """
        Функция формирует линк, скачивает картинку и сохраняет в формате nickname.png
        :param country_name: название страны в международном формате
        :param name: Ник игрока
        """
        with open(f"{FLAGS_DIR_NAME}/{name}.png", "wb") as imgfile:
            flag_file = requests.get(f"{FLAGS_URL}{country_name}.png")
            imgfile.write(flag_file.content)

    save_threads = []
    # Создаем папку если это необходимо
    if not os.path.exists(path_file):
        os.mkdir(path_file)
    # Перебираем элементы и передаем в функцию параметры для скачивания флага
    for row in request_results:
        country = row[3].lower()
        file_name = row[1]
        save = Thread(target=save_flag, args=(country, file_name,))
        save.start()
        save_threads.append(save)
    # Ждем завершения всех потоков
    for thread in save_threads:
        thread.join()
    print("\tОбработка флагов завершена, результат сохранен в каталог " + path_file)


if __name__ == '__main__':
    print("Привет, я парсер, давай начнем работу.")
    api_request_results = results_from_api()
    write_to_file_stats(api_request_results, STAT_DIR_NAME)
    write_to_file_flags(api_request_results, FLAGS_DIR_NAME)
    print("Я закончил работу, это окно можно закрыть")
