# coding: utf-8

import logging
from config.settings import LOG_FILE_NAME


def set_logger():
    """
    Настройки лгирования системы Harold
    """
    # logger.info('at: {start_time}'.format(start_time=datetime.datetime.fromtimestamp(t0)))
    #  create logger with 'harold' application
    logger = logging.getLogger('harold')
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOG_FILE_NAME)
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
