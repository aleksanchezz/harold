# coding: utf-8
"""
Модуль, реализующий работу с файлами как то:
    - сохранение файлов с конфликтами
    - выгрузка конфликтов из этого файла

    - сохранение в pickle файлы информации о собранных статистиках

"""

import logging
from config.settings import FILES_FOLDER_PATH, CONFLICTS_FOLDER, PICKLES_FOLDER, NGRAMMS_FOLDER_PATH
import os
import io
import cPickle as pickle

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

        self.speech_parts_filename = '/'.join([self.pickles_folder, 'speech_parts.pkl'])
        self.punctuation_filename = '/'.join([self.pickles_folder, 'punctuation.pkl'])
        self.pos_filename = '/'.join([self.pickles_folder, 'pos.pkl'])
        self.ngramm_filename = '/'.join([NGRAMMS_FOLDER_PATH, 'ngramm.pkl'])

        self.ngramm_backup_folder = '/'.join([NGRAMMS_FOLDER_PATH, 'backups'])

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

    def save_speech_parts_to_pickle(self, speech_parts):
        """Сохраняет собранные части речи в файл
        """

        output = open(self.speech_parts_filename, 'wb')
        pickle.dump(speech_parts, output, 2)
        output.close()
        logger.info('[PICKLE] File was written: {file}'.format(file=self.speech_parts_filename))

    def load_speech_parts_from_pickle(self):
        """Загружает сохраненные части речи"""

        inp = open(self.speech_parts_filename, 'rb')
        obj = pickle.load(inp)
        inp.close()
        logger.info('[PICKLE] File was read: {file}'.format(file=self.speech_parts_filename))

        return obj

    def save_punctuation_to_pickle(self, punctuation):
        """Сохраняет собранные части речи в файл
        """

        output = open(self.punctuation_filename, 'wb')
        pickle.dump(punctuation, output, 2)
        output.close()
        logger.info('[PICKLE] File was written: {file}'.format(file=self.punctuation_filename))

    def load_punctuation_from_pickle(self):
        """Загружает сохраненные части речи"""

        inp = open(self.punctuation_filename, 'rb')
        obj = pickle.load(inp)
        inp.close()
        logger.info('[PICKLE] File was read: {file}'.format(file=self.punctuation_filename))

        return obj

    def save_pos_to_pickle(self, pos):
        """Сохраняет собранные части речи в файл
        """

        output = open(self.pos_filename, 'wb')
        pickle.dump(pos, output, 2)
        output.close()
        logger.info('[PICKLE] File was written: {file}'.format(file=self.pos_filename))

    def load_pos_from_pickle(self):
        """Загружает сохраненные части речи"""

        inp = open(self.pos_filename, 'rb')
        obj = pickle.load(inp)
        inp.close()
        logger.info('[PICKLE] File was read: {file}'.format(file=self.pos_filename))

        return obj

    def load_ngramm_from_pickle(self):
        """Загружает список ngramm
        """

        inp = open(self.ngramm_filename, 'rb')
        obj = pickle.load(inp)
        inp.close()
        logger.info('[PICKLE] File was read: {file}'.format(file=self.ngramm_filename))
        print 'ngramm loaded:', len(obj)

        return obj

    def save_ngramm_to_pickle(self, ngramm):
        """Сохраняет N-граммы в файл"""

        output = open(self.ngramm_filename, 'wb')
        pickle.dump(ngramm, output, 2)
        output.close()
        print 'ngramm saved:', len(ngramm)
        logger.info('[PICKLE] File was written: {file}'.format(file=self.ngramm_filename))

        # BACKUP
        filename = 'ngramms'
        counter = len(os.listdir(self.ngramm_backup_folder)) + 1
        filename = filename + '_' + str(counter) + '_' + str(len(ngramm)) + '.pkl'
        filename = '/'.join([self.ngramm_backup_folder, filename])

        output = open(filename, 'wb')
        pickle.dump(ngramm, output, 2)
        output.close()
