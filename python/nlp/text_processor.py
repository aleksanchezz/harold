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
from file_processor import FileProcessor
import re
from nltk import sent_tokenize, word_tokenize
from config.settings import CUSTOM_PUNCTUATION_SYMBOLS, PUNCTUATION_SYMBOLS, SPEECH_PARTS
from pymorphy2 import MorphAnalyzer

logger = logging.getLogger('harold.text_processor')


class TextProcessor(object):

    def __init__(self, filename):

        self.file = FictionBook(filename)
        self.file_processor = FileProcessor(self.file.book_code_name)
        self.sentences = []
        self.sentences_count = 0
        self.words = []
        self.words_count = 0
        self.speech_parts = []
        self._punctuation_symbols = None
        # Статистические словари
        self._punctuation = {}
        self._pos = {}

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

    @property
    def pos(self):
        if not bool(self._pos):
            for item in SPEECH_PARTS:
                self._pos.update({item: 0})
        return self._pos

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

        logger.info('\n[Text cleaning] Resulting lengths:\n'
                    '\traw: {raw}\n'
                    '\tno brackets: {brackets}\n'
                    '\tno tabs: {tabs}\n'
                    '\tcleaned paragraphs: {clean}'.format(**text_len))

        return cleaned_text

    def _split_into_tokens(self, text):
        """Разбирает текст на предложения и слова, попутно решая возникающие конфликты и считающие пунтктуацию"""

        self.sentences = sent_tokenize(text, language='russian')
        _count = 0
        for s, sentence in enumerate(self.sentences):
            self.sentences_count += 1
            _words = word_tokenize(sentence, language='russian')
            clean_words = []
            for w, _word in enumerate(_words):
                if _word in self.punctuation:
                    self.punctuation[_word] += 1
                else:
                    self.words_count += 1
                    _word = self._process_word(_word).lower()
                    clean_words.append(_word)
                    if not _word.isalpha() and '-' not in _word and not _word.isnumeric():
                        _count += 1
                        logger.warn('Tokenization failure: {word}\n'
                                    '\t sentence ({n}, {m}):\n[ {sentence} ]\n'.format(word=_word.encode('utf-8'),
                                                                                       n=s,
                                                                                       m=w,
                                                                                       sentence=sentence.encode('utf-8')
                                                                                       )
                                    )

            self.words.append(clean_words)

        return _count

    def _resolve_conflicts(self, filename):
        """Заменяет элменты со значением 'NOPOS' в массиве self.speech_parts,
        считав информацию из указанного файла
        """

        resolved_conflicts = self.file_processor.read_conflicts_from_csv(filename)

        for item in resolved_conflicts:
            self.speech_parts[item[1]][item[2]] = item[0]
            self.pos[item[0]] += 1

        result = self._check_for_conflicts()

        if result:
            logger.info('\nConflicts were successfully resolved from file: {file}'.format(file=filename))
        else:
            logger.error('\nNot all conflicts were resolved from file: {file}'.format(file=filename))

        return

    def _define_part_of_speech(self):
        """Проходит по тексту и определяет части речи каждого слова"""
        conflicts = dict()
        print "in morph"
        morph = MorphAnalyzer()
        _count = 0
        for s in range(self.sentences_count):

            _sentence_pos = []
            for w in range(len(self.words[s])):

                word = self.words[s][w]
                m = morph.parse(word)

                if m[0].tag.POS is None:
                    _sentence_pos.append('NOPOS')
                    _count += 1
                    if word not in conflicts:
                        conflicts.update(
                            {
                                word: {
                                    'speech_part': u'NOUN',
                                    'indicies': [(s, w)]
                                    }
                            })
                    else:
                        conflicts[word]['indicies'].append((s, w))
                else:
                    _sentence_pos.append(m[0].tag.POS.__str__())
                    self.pos[m[0].tag.POS.__str__()] += 1
            self.speech_parts.append(_sentence_pos)

        logger.info('\n[MORPH] Words were proceeded with pymorph:\n'
                    '\tTotal words in text: {words}\n'
                    '\tTotal sentences in text: {sent}\n'
                    '\tTotal words with no POS determined: {confl}\n'
                    '\tUnique words with no POS : {un}'.format(words=self.words_count,
                                                               sent=self.sentences_count,
                                                               confl=_count,
                                                               un=len(conflicts)))

        return conflicts

    def _check_for_conflicts(self):
        """Проверяет массив self.speech_parts на наличие записи 'NOPOS'
        """
        for sentence in self.speech_parts:
            for word in sentence:
                if word == 'NOPOS':
                    return False
        return True

    def main_text_processing(self):
        """
        Фактически точка входу в обработку текста:

            + убрать из текста лишние символы
            + разбить текст на предложения
            + разбить предложения на слова
            + обработать слова
            + КОНФЛИКТЫ
            - собрать статистику
            - сохранить новые N-граммы
        """
        """
        При тестировании неразумно каждый раз загружать информацию из файла
        Реализован механизм считывания частей речи из файла .pickle

        raw_text = self.file.text

        cleared_raw_text = self._remove_and_replace_symbols(raw_text)
        parsing_conflicts = self._split_into_tokens(cleared_raw_text)

        if parsing_conflicts > 0:
            print 'Parsing conflicts were detected {n},\n' \
                  '\twe advice you to deal with them before further processing'.format(n=parsing_conflicts)

        v = self._define_part_of_speech()

        morph_conflicts, path = self.file_processor.save_conflicts_to_csv(v, self.sentences)
        print '{} conflicts were written to file: {}'.format(morph_conflicts, path)

        self._resolve_conflicts('/etc/harold/Po_kom_zvonit_kolokol/conflicts/conflicts_2.csv')

        self.file_processor.save_speech_parts_to_pickle(self.speech_parts)
        self.file_processor.save_pos_to_pickle(self.pos)
        self.file_processor.save_punctuation_to_pickle(self.punctuation)
        """

        self.speech_parts = self.file_processor.load_speech_parts_from_pickle()
        self._pos = self.file_processor.load_pos_from_pickle()
        self._punctuation = self.file_processor.load_punctuation_from_pickle()

        import pdb
        pdb.set_trace()

        for item in self.punctuation:
            print item, self.punctuation[item]

        for item in self.pos:
            print item, self.pos[item]

