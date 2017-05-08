# coding: utf-8
"""
Модуль обработки текста, полученного из внешних файлов (в частности fb2)

Обеспечивает испраление кодировки, токенизацию и обработку входных данных в
соотвествии с реализуемым методом

Для использования nltk необходимо скачать словари

    >>> import nltk
    >>> nltk.download()

"""

import logging
from parser.fiction_book import FictionBook
import re

logger = logging.getLogger('harold.text_processor')


class TextProcessor(object):

    def __init__(self, filename):

        self.file = FictionBook(filename)

    def handle_encoding(self):
        pass

    def _remove_and_replace_symbols(self, text):
        """
        Один из наиболее важных методов при обработке текста. Благодаря тому, что изначально текст берется
        из предварительно отфрматированного файла *.fb2 в тексте находятся только текстовые символы.

        Но из-за особенностей библиотеки парсинга и устройства формата fb2 в тексте
        присутсвуют следующие лишние символы:

            -   [*], где * - это число      // ссылки на дополнительные элементы (картинки, переводы)
            -   \t                          // символы табуляции, отделяющие параграфы (тэги <p>)
            -   обазначение "глав" книги    // числа окруженные знаком '\n'

        Из-за ошибок и неточностей верстки набивки текста могут быть следующие ситуации:

            -   В конце параграфов может не быть символа конца предложения (лишь знак '\n')
            -   После символа конца предложения может не быть пробела (не будет обработано корректно библиотекой nltk)
            -   Такая же ситуация может быть с любым другим знаком окончания предолжения

        Алгоритм:

            1) удалить из текста следующие последовательности символов:
                +   '\t'
                +   '\n${numbers}\n'
                +   '[${numbers}]'

            2) заменить в тексте след. последовательности символов:
                + если '${not(${sentence_end})}\n' -> '.\n'

            3) удалить из текста все символы '\n'

        """
        text_len = {}

        text_len.update({"raw": len(text)})

        text = re.sub('[[].*?]', '', text)
        text_len.update({"brackets": len(text)})

        text = text.replace('\t', '')
        text_len.update({"tabs": len(text)})

        paragraphs = text.split('\n')
        clean_paragraphs = []

        for p in range(len(paragraphs)):
            if len(paragraphs[p]) > 0 and not paragraphs[p].isnumeric():
                paragraphs[p] = paragraphs[p].strip()
                if paragraphs[p][-1].isalpha():
                    paragraphs[p] += '.'
                clean_paragraphs.append(paragraphs[p])

        cleaned_text = ' '.join(clean_paragraphs)
        text_len.update({"clean": len(cleaned_text)})

        logger.info('\nText was cleaned lengths:\n'
                    '\traw: {raw}\n'
                    '\tno brackets: {brackets}\n'
                    '\tno tabs: {tabs}\n'
                    '\tcleaned paragraphs: {clean}'.format(**text_len))

        return cleaned_text

    def main_text_processing(self):
        """
        Фактически точка входу в обработку текста:

            - убрать из текста лишние символы
            - разбить текст на предложения
            - разбить предложения на слова
            - обработать слова
            - КОНФЛИКТЫ??
            - собрать статистику
            - сохранить новые N-граммы
        """
        raw_text = self.file.text

        cleared_raw_text = self._remove_and_replace_symbols(raw_text)
        print len(cleared_raw_text) - len(raw_text)

