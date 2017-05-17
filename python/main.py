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

    tp = TextProcessor('/home/aln/diplom/example.fb2')
    tp.main_text_processing()


def main_menu(prev):
    print
    print "Choose your option: [Previous option: {prev}]\n" \
          "\t[1] Process as new text - clean tokenize + punctuation\n" \
          "\t[2] First morphological analysis - after handling tokenization issues\n" \
          "\t[3] Resolve morphological conflicts - read from generated csv file\n" \
          "\t[4] Collect N-gramms - save all statistics vectors to DB Harold\n" \
          "\t[5] Exit".format(prev=prev)
    option = raw_input("> ")
    return int(option)


def ui():
    set_logger()

    logger = logging.getLogger('harold.main')
    logger.info('Harold System has been launched')

    print
    print "Welcome to the Harold Morphology Analytics System"
    filename = raw_input("Please enter filename with fb2 extension to proceed: ")
    tp = TextProcessor(filename)
    previous_option = 0
    option = 0
    saved_to_file = False

    while option != 5:

        option = main_menu(previous_option)

        if option == 1:
            if tp and tp.file.text:
                tp.raw_text_processing()
            else:
                print 'ERROR - no text!'

        if option == 2:
            if tp and tp.words:
                tp.morphological_definition()
            else:
                print 'ERROR - parse text first'

        if option == 3:
            if tp:
                _ = raw_input("\tPlease, enter file with resolved conflicts: ")
                if not tp.speech_parts:
                    tp.load_pickles()
                tp.morphological_resolution(_)
                print "\tAll conflicts were resolved, now you can collect N-gramm statistics"
            else:
                print 'ERROR - no text'

        if option == 4:
            if tp:
                if not tp.speech_parts:
                    tp.load_pickles()
                tp.statistics()
                print "\tText processing is finished. result is saved to DB"
            else:
                print 'ERROR - no text'


        if option == 5:
            break

        previous_option = option

    print filename
    print option

    # tp = TextProcessor('/home/aln/diplom/example.fb2')
    # tp.main_text_processing()

    return 0

if __name__ == "__main__":
    ui()
