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
              "limit": "10"}
api_url = 'http://aligulac.com/api/v1/player/'
flags_url = 'http://img.aligulac.com/flags/'
path_file_stat = 'stats/stats.csv'
path_file_flag = 'flags/'


def results_from_api(params: dict, url: str):
    # инициируем запрос с заголовком
    request_results = requests.get(api_url, params=params).text
    extract_results = json.loads(request_results)['objects']
    print(extract_results)
    return extract_results


def write_to_file_stats(request_results: list, path_file):
    csv_columns = tuple()
    print(csv_columns)

    with open(path_file, 'w') as stats:
        writer = csv.DictWriter(stats, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(request_results)


def write_to_file_flags(request_results: list, file_path):
    # Переберем все элементы в результатах, по ключам достанем ник и страну
    for row in request_results:
        country = row["country"].lower()
        file_name = row["tag"]
        full_file_path = f"{file_path}{file_name}.png" #
        imgfile = open(full_file_path, "wb")  # открываем файл для записи, в режиме wb
        ufr = requests.get(f"{flags_url}{country}.png")  # делаем запрос
        imgfile.write(ufr.content)  # записываем содержимое в файл
        imgfile.close()


api_request_results = results_from_api(params_for_api, api_url)
#write_to_file_stats(api_request_results, path_file_stat)
write_to_file_flags(api_request_results, path_file_flag)
