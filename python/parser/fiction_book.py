# coding: utf-8
"""
Модуль содержит класс, реализующий сериализацию и первичную обработку
файлов в формате *.fb2 (fiction book format, XML - подобный формат)

Библиотека pyfb2 взята с https://github.com/gigimon/pyfb2.git

Описание формата приведено на официальном сайте http://www.fictionbook.org/index.php
"""

from pyfb2.fb2 import PyFb2, PublishInfo
from pyfb2.body import TagBody, MainTag, TagP, TAGS
from db.models import DataBaseConnection, Author, Book
from transliterate import translit


class FictionBook(PyFb2):

    def __init__(self, path_to_file):

        super(FictionBook, self).__init__(fpath=path_to_file)
        self._meta = dict()
        self._document = self._get_tree()
        self._author = None
        self._title = None
        self._genres = None
        self._date = None
        self._text = None
        self._file_info = None
        self._book_info = None
        self._book_code_name = None

    @property
    def author(self):
        if self._author is None:
            self._author = self.get_title_info().author or self.get_document_info().author
        return self._author

    @property
    def title(self):
        if self._title is None:
            self._title = self.get_title_info().title
        return self._title

    @property
    def genres(self):
        if self._genres is None:
            self._genres = self.get_title_info().genres
        return self._genres

    @property
    def date(self):
        if self._date is None:
            self._date = self.get_document_info().date
        return self._date

    @property
    def text(self):
        if self._text is None:
            self._text = TagP(self.root[1]).to_text()
        return self._text

    @property
    def file_info(self):
        if self._file_info is None:
            self._file_info = self._get_meta_info()
        return self._file_info

    @property
    def book_info(self):
        if self._book_info is None:
            self._book_info = self._get_book_info()
        return self._book_info

    @property
    def book_code_name(self):
        if self._book_code_name is None:
            self._book_code_name = self.traslit(self.book_info['title'])
        return self._book_code_name

    def _get_meta_info(self):
        res = {}
        res.update({"encoding": self._get_encoding()})
        res.update({"filename": self._get_url()})
        res.update({"root": self._get_root_name()})
        res.update({"namespace": self._get_namespace()})
        return res

    def _get_book_info(self):
        res = {}
        res.update({"author": self.author})
        res.update({"title": self.title})
        res.update({"genres": self.genres})
        res.update({"date": self.date})
        return res

    def _get_url(self):
        return self.file or self._document.docinfo.URL

    def _get_encoding(self):
        return self._document.docinfo.encoding

    def _get_root_name(self):
        return self._document.docinfo.root_name

    def _get_namespace(self):
        return self.root.nsmap

    def traslit(self, word):
        result = translit(word, 'ru', reversed=True).lower()
        return result.replace(' ', '_')

    def save_book_info_to_db(self):
        """
        Сохраняет информацию об обработанной книге и авторе в БД harold
        """
        dbc = DataBaseConnection()
        _author_id = dbc.get_id(Author)
        _book_id = dbc.get_id(Book)

        author = Author(id=_author_id,
                        name=self.book_info['author'],
                        code_name=self.traslit(self.book_info['author'])
                        )

        book = Book(id=_book_id,
                    title=self.book_info['title'],
                    author_id=_author_id,
                    genre=','.join(self.book_info['genres']),
                    date=self.book_info['date'],
                    code_name=self.book_info['title']
                    )

        _author_id = dbc.create_or_update(author)
        _book_id = dbc.create_or_update(book)
        dbc.close_session()
        return _book_id
