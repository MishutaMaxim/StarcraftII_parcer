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

# параметры API и токен, Путь для файла статистики и флагов
params_for_api = {"apikey": "AeM6fd9sGXyZBOu8vwkE",
              "current_rating__isnull": "false",
              "order_by": "-current_rating__rating",
              "limit": "500"}
api_url = 'http://aligulac.com/api/v1/player/'
flags_url = 'http://img.aligulac.com/flags/'
path_file_stat = 'stats/stats.csv'
path_file_flag = 'flags/'
race_name = {'P': 'Protoss',
             'T': 'Terran',
             'Z': 'Zerg',
             'R': 'random',
             'S': 'race switcher'}


def results_from_api(params: dict, url: str):
    # инициируем запрос с заголовком
    print("Я пошел на ресурс с API запросом, придется подождать")
    request_results = requests.get(api_url, params=params)
    print("Ответ пришел")
    extract_results = json.loads(request_results.text)['objects']
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
    # Переберем все элементы в результатах, по ключам достанем ник и страну
    print("Я начинаю запись флагов")
    for row in request_results:
        country = row["country"].lower()
        file_name = row["tag"]
        full_file_path = f"{file_path}{file_name}.png" #
        imgfile = open(full_file_path, "wb")  # открываем файл для записи, в режиме wb
        flag_file = requests.get(f"{flags_url}{country}.png")  # делаем запрос
        imgfile.write(flag_file.content)  # записываем содержимое в файл
        imgfile.close()
    print("Я закончил запись флагов")


if __name__ == '__main__':
    print("Привет, я парсер, давай начнем работу.")
    api_request_results = results_from_api(params_for_api, api_url)
    write_to_file_stats(api_request_results, path_file_stat)
    write_to_file_flags(api_request_results, path_file_flag)
    print("Я закончил работу, это окно можно закрыть")