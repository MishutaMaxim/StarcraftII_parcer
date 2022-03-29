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

request_limit = 50
data_limit = 500
params_for_api = {"apikey": "AeM6fd9sGXyZBOu8vwkE",
                  "current_rating__isnull": "false",
                  "order_by": "-current_rating__rating",
                  "limit": request_limit}
api_url = 'http://aligulac.com/api/v1/player/'
flags_url = 'http://img.aligulac.com/flags/'
path_file_stat = 'stats'
path_file_flag = 'flags'
race_name = {'P': 'Protoss',
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
        params = params_for_api.copy()
        params.update({"offset": offset})
        # Делаем сам запрос, результаты добавляем в общий список
        request_results = requests.get(api_url, params=params)
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
                          race_name[row["race"]]]
            extract_results.append(result_row)

    # Объявляем общий список с результатами и список потоков
    extract_results = []
    response_threads = []
    print("Отправили API запрос на сервер, придется подождать ...")
    start_time = time()
    # Запускаем потоки
    for limit in range(0, data_limit, request_limit):
        th_req = Thread(target=api_request, args=(limit,))
        response_threads.append(th_req)
        th_req.start()
    # Ожидаем их завершения
    for thread in response_threads:
        thread.join()
    print(f"Ответ обработан, это заняло {time() - start_time} сек.")
    extract_results = sorted(extract_results, key=lambda x: x[0], reverse=True)
    return extract_results


def write_to_file_stats(request_results: list, path_file):
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
        with open(f"{path_file_flag}/{name}.png", "wb") as imgfile:
            flag_file = requests.get(f"{flags_url}{country_name}.png")
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
    print("Обработка флагов завершена, результат сохранен в каталог " + path_file)


if __name__ == '__main__':
    print("Привет, я парсер, давай начнем работу.")
    api_request_results = results_from_api()
    write_to_file_stats(api_request_results, path_file_stat)
    write_to_file_flags(api_request_results, path_file_flag)
    print("Я закончил работу, это окно можно закрыть")
