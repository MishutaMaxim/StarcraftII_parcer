"""
Параметры для парсера
"""

# Ограничения на 1 запрос (оптимально 50-100, другие будут выполняться немного дольше
REQUEST_LIMIT = 50

# Общее количество строк которое нужно получить
DATA_LIMIT = 100

# Адрес для запросов
API_URL = 'http://aligulac.com/api/v1/player/'

# Ключ для api
API_KEY = "AeM6fd9sGXyZBOu8vwkE"

# Параметры для запроса,
API_PARAMS = {"apikey": API_KEY,
                  "current_rating__isnull": "false",
                  "order_by": "-current_rating__rating",
                  "limit": REQUEST_LIMIT}

# Адрес для флагов
FLAGS_URL = 'http://img.aligulac.com/flags/'

# Папка для таблицы
STAT_DIR_NAME = 'stats'

# Папка для флагов
FLAGS_DIR_NAME = 'flags'
