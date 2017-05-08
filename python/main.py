# coding: utf-8
"""
Точка входа в систему анализа текстов "Harold"
"""
from logger import set_logger
import logging
from parser.fiction_book import FictionBook
from nlp.text_processor import TextProcessor


def main():
    set_logger()

    logger = logging.getLogger('harold.main')
    logger.info('Harold System has been launched')

    fb = FictionBook('/home/aln/diplom/example.fb2')

    tp = TextProcessor('/home/aln/diplom/example.fb2')
    tp.main_text_processing()

    return 0

if __name__ == "__main__":
    main()
