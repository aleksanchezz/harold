# coding: utf-8
"""
Модуль обработки текста, полученного из внешних файлов (в частности fb2)

Обеспечивает испраление кодировки, токенизацию и обработку входных данных в
соотвествии с реализуемым методом

Для использования nltk необходимо скачать словари

    >>> import nltk
    >>> nltk.download()

tokenization/punkt/russian.pickle -> $ git clone https://github.com/mhq/train_punkt.git

"""

import logging
from parser.fiction_book import FictionBook
import re
from nltk import sent_tokenize, word_tokenize
from config.settings import CUSTOM_PUNCTUATION_SYMBOLS, PUNCTUATION_SYMBOLS
from pymorphy2 import MorphAnalyzer
from pymorphy2.tagset import OpencorporaTag

logger = logging.getLogger('harold.text_processor')


class TextProcessor(object):

    def __init__(self, filename):

        self.file = FictionBook(filename)
        self.sentences = []
        self.sentences_count = 0
        self.words = []
        self.words_count = 0
        self.speech_parts = []
        self._punctuation_symbols = None
        self._punctuation = {}

    @property
    def punctuation_symbols(self):
        if self._punctuation_symbols is None:
            self._punctuation_symbols = CUSTOM_PUNCTUATION_SYMBOLS
        return self._punctuation_symbols

    @property
    def punctuation(self):
        if not bool(self._punctuation):
            for symbol in PUNCTUATION_SYMBOLS:
                self._punctuation.update({symbol: 0})
        return self._punctuation

    def handle_encoding(self):
        pass

    def _process_word(self, word):
        """Разрешает конфликты внутри слова, когда парсер не может отделить
        некотрые знаки пунктуации от слова в основном: кавычки и многоточия

        будет использован список self.punctuation_symbols"""
        _clean_word = ''
        for symbol in word:
            if symbol not in self.punctuation_symbols:
                _clean_word += symbol
            else:
                self._punctuation[symbol] += 1
        return _clean_word

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

    def _split_into_tokens(self, text):
        """Разбирает текст на предложения и слова, попутно решая возникающие конфликты и считающие пунтктуацию"""

        self.sentences = sent_tokenize(text, language='russian')
        _count = 0
        for sentence in self.sentences:
            self.sentences_count += 1
            _words = word_tokenize(sentence, language='russian')
            clean_words = []
            for _word in _words:
                if _word in self.punctuation:
                    self.punctuation[_word] += 1
                else:
                    self.words_count += 1
                    _word = self._process_word(_word).lower()
                    clean_words.append(_word)
                    if not _word.isalpha() and '-' not in _word:
                        _count += 1
                        logger.warn('Neither word not punctuation: {}'.format(_word.encode('utf-8')))
            self.words.append(clean_words)

        return _count

    def _define_part_of_speech(self):
        """Проходит по тексту и определяет части речи каждого слова"""
        conflicts = dict()
        print "in morph"
        morph = MorphAnalyzer()
        _count = 0
        for sentence in self.words:
            for word in sentence:
                m = morph.parse(word)
                if m[0].tag.POS is None:
                    import pdb
                    pdb.set_trace()
                    _count += 1
                    if word not in conflicts:
                        conflicts.update({word: u'NOUN'})

        print self.words_count, _count

        return conflicts

    def main_text_processing(self):
        """
        Фактически точка входу в обработку текста:

            + убрать из текста лишние символы
            + разбить текст на предложения
            + разбить предложения на слова
            + обработать слова
            - КОНФЛИКТЫ??
            - собрать статистику
            - сохранить новые N-граммы
        """
        raw_text = self.file.text

        cleared_raw_text = self._remove_and_replace_symbols(raw_text)
        parsing_conflicts = self._split_into_tokens(cleared_raw_text)

        v = self._define_part_of_speech()

        import pdb
        pdb.set_trace()

        for item in self.punctuation:
            print item, self.punctuation[item]

