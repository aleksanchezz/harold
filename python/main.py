# coding: utf-8
"""
Точка входа в систему анализа текстов "Harold"
"""
from logger import set_logger
import logging
from parser.fiction_book import FictionBook


def main():
    set_logger()

    logger = logging.getLogger('harold.main')
    logger.info('Harold System has been launched')

    fb = FictionBook('/home/aln/diplom/example.fb2')

    return 0

if __name__ == "__main__":
    main()
