# coding: utf-8
"""
Модуль, реализующий работу с файлами как то:
    - сохранение файлов с конфликтами
    - выгрузка конфликтов из этого файла

    - сохранение в pickle файлы информации о собранных статистиках

"""

import logging
from config.settings import FILES_FOLDER_PATH, CONFLICTS_FOLDER, PICKLES_FOLDER
import os
import io

logger = logging.getLogger('harold.file_processor')


class FileProcessor(object):

    def __init__(self, book_code_name):
        """Создает, если таковых нет три папки:

            - /etc/harold/<book_code_name>
            - /etc/harold/<book_code_name>/conflicts
            - /etc/harold/<book_code_name>/pickles
        """
        self.main_folder = '/'.join([FILES_FOLDER_PATH, book_code_name])
        if not os.path.exists(self.main_folder):
            os.makedirs(self.main_folder)

        self.conflicts_folder = '/'.join([self.main_folder, CONFLICTS_FOLDER])
        if not os.path.exists(self.conflicts_folder):
            os.makedirs(self.conflicts_folder)

        self.pickles_folder = '/'.join([self.main_folder, PICKLES_FOLDER])
        if not os.path.exists(self.pickles_folder):
            os.makedirs(self.pickles_folder)

    def save_conflicts_to_csv(self, conflicts, sentences):
        """Записывает слова с csv файл в следующем формате:

        <номер>, <чатсь речи>, <слово>, <кол-во таких слов>
               ,             ,        , <предложение>, <индекс-предложения>, <индекс-слова>

        """

        filename = 'conflicts'
        counter = len(os.listdir(self.conflicts_folder)) + 1

        filename = filename + '_' + str(counter) + '.csv'
        filename = '/'.join([self.conflicts_folder, filename])
        f = io.open(filename, 'w+', encoding='utf-8')

        # здесь counter используется как счетчик конфликтов
        counter = 0
        for word in conflicts:
            counter += 1
            line = ','.join([str(counter), word, conflicts[word]['speech_part'], str(len(conflicts[word]['indicies']))]) + '\n'

            for index in conflicts[word]['indicies']:
                sentence_to_write = sentences[index[0]]
                # Чтобы не было сдвигов в самом csv файле, из текста нужно убрать запятые и точки с запятой
                sentence_to_write = sentence_to_write.replace(',', ' ')
                sentence_to_write = sentence_to_write.replace(';', ' ')

                line += ',,,' + sentence_to_write + ',' + str(index[0]) + ',' + str(index[1]) + '\n'

            f.write(line)
        f.close()

        logger.info('\nConflicts ({n}) were written to file: {file}'. format(n=counter, file=filename))

        return counter, filename

    def read_conflicts_from_csv(self, filename):
        """Считывает информацию из обработанного файла, содержащего описание конфликтов

                   0          1           2         3                 4                   5
                <номер>, <чатсь речи>, <слово>, <кол-во таких слов>
                       ,             ,        , <предложение>, <индекс-предложения>, <индекс-слова>
                """
        result = []
        with io.open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            f.close()

        line_iter = iter(lines)

        while True:
            item = next(line_iter, None)
            if not item:
                break
            line = item.split(',')
            if line[0] is not None:

                capacity = line[3]
                pos = line[2]
                for i in range(int(capacity)):
                    line = next(line_iter, None).split(',')
                    result.append((pos, int(line[4]), int(line[5])))

        return result


