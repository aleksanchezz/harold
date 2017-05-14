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

# Части речи, встречающие в в библиотеке pymorphy2
SPEECH_PARTS = [u'NOUN',
                u'ADJF',
                u'ADJS',
                u'COMP',
                u'VERB',
                u'INFN',
                u'PRTF',
                u'PRTS',
                u'GRND',
                u'NUMR',
                u'ADVB',
                u'NPRO',
                u'PRED',
                u'PREP',
                u'CONJ',
                u'PRCL',
                u'INTJ'
                ]

SPEECH_PARTS_HUMANABLE = [u'имя существительное',
                          u'имя прилагательное (полное)',
                          u'имя прилагательное (краткое)',
                          u'компаратив',
                          u'глагол (личная форма)',
                          u'глагол (инфинитив)',
                          u'причастие (полное)',
                          u'причастие (краткое)',
                          u'деепричастие',
                          u'числительное',
                          u'наречие',
                          u'местоимение-существительное',
                          u'предикатив',
                          u'предлог',
                          u'союз',
                          u'частица',
                          u'междометие'
                          ]
