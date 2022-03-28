'''
Задание:
Написать скрипт, достающий информацию о игроках в Starcraft II.
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
'''


import requests
import json
import csv
from time import time
from threading import Thread, RLock

# параметры API и токен, Путь для файла статистики и флагов
request_limit = 10
data_limit = 500
params_for_api = {"apikey": "AeM6fd9sGXyZBOu8vwkE",
              "current_rating__isnull": "false",
              "order_by": "-current_rating__rating",
              "limit": (request_limit) }
api_url = 'http://aligulac.com/api/v1/player/'
flags_url = 'http://img.aligulac.com/flags/'
path_file_stat = 'stats/stats.csv'
path_file_flag = 'flags/'
race_name = {'P': 'Protoss',
             'T': 'Terran',
             'Z': 'Zerg',
             'R': 'random',
             'S': 'race switcher'}

start_time = time()

def results_from_api():
    def thread_request(offset):
        params = params_for_api.copy()
        params.update({"offset": offset})
        request_results = requests.get(api_url, params=params)
        results = json.loads(request_results.text)['objects']
        extract_results.extend(results)
    # инициируем запрос с заголовком
    extract_results = []
    response_threads = []
    print("Я пошел на ресурс с API запросом, придется подождать")
    for limit in range(0, data_limit, request_limit):
        th_req = Thread(target=thread_request, args=(limit,))
        response_threads.append(th_req)
        th_req.start()
    for thread in response_threads:
        thread.join()
    print("Ответ пришел")
    return extract_results


def write_to_file_stats(request_results: list, path_file):
    print("Начинаю запись в файл таблички")
    csv_columns = ("Ник", "Имя", "Страна", "Команда", "Дата рождения", "Призовые за карьеру", "Расса")
    with open(path_file, 'w', newline='', encoding='utf-8') as stats:
        writer = csv.writer(stats, dialect='excel')
        writer.writerow(csv_columns)
        for row in request_results:
            teams = row["current_teams"][0]["team"]["name"] if row["current_teams"] else ''
            result_row = [row["tag"],
                          row["name"],
                          row["country"],
                          teams,
                          row["birthday"],
                          row["total_earnings"],
                          race_name[row["race"]]]
            writer.writerow(result_row)
    print("Я закончил запись в файл")


def write_to_file_flags(request_results: list, file_path):
    def save_flag(country: str, name: str):
        imgfile = open(f"{path_file_flag}{name}.png", "wb")  # открываем файл для записи, в режиме wb
        flag_file = requests.get(f"{flags_url}{country}.png")  # делаем запрос
        imgfile.write(flag_file.content)  # записываем содержимое в файл
        imgfile.close()

    # Переберем все элементы в результатах, по ключам достанем ник и страну
    print("Я начинаю запись флагов")
    for row in request_results:
        country = row["country"].lower()
        file_name = row["tag"]
        save = Thread(target=save_flag, args=(country, file_name,))
        save.start()
    save.join()
    print("Я закончил запись флагов")


if __name__ == '__main__':
    print("Привет, я парсер, давай начнем работу.")
    print(f"Время от начала: {time() - start_time}")
    api_request_results = results_from_api()
    print(f"Время от начала: {time() - start_time}")
    write_to_file_stats(api_request_results, path_file_stat)
    print(f"Время от начала: {time() - start_time}")
    write_to_file_flags(api_request_results, path_file_flag)
    print(f"Время от начала: {time() - start_time}")
    print("Я закончил работу, это окно можно закрыть")
