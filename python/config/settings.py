# coding: utf-8

import sys
from string import punctuation

DATABASE_HOST = '127.0.0.1'

# DB Postgres
PHAROLD_SETTINGS = {
    'host': DATABASE_HOST,
    'port': 5432,
    'user': 'harold',
    'dbname': 'harold'
}

LOG_FILE_NAME = '/logs/harold/harold.log'
FILES_FOLDER_PATH = '/etc/harold'
CONFLICTS_FOLDER = 'conflicts'
PICKLES_FOLDER = 'pickles'

# Добавлять вручную выявленные в процессе парсинга новые знаки пунктуации
# попавшие в конфликты (см. лог файл)
CUSTOM_PUNCTUATION_SYMBOLS = [u'«', u'»', u'…', u'—', u'“', u'„', u'–']

# Сводный веткор символов пунктуации для сохранения информации в память
PUNCTUATION_SYMBOLS = list(punctuation) + CUSTOM_PUNCTUATION_SYMBOLS
