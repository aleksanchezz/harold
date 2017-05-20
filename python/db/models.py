# coding: utf-8
"""
Модуль содержащий ORM классы для работы с БД harold
"""

from config.settings import PHAROLD_SETTINGS
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Column, String, Integer, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


class DataBaseConnection(object):

    def __init__(self):
        self._database = None
        self._metadata = None
        self._connection_string = None
        self._base = None
        self._session = None

    @property
    def connection_string(self):
        if self._connection_string is None:
            self._connection_string = 'postgresql://{user}@{host}:{port}/{dbname}'.format(
                **PHAROLD_SETTINGS
            )
        return self._connection_string

    @property
    def database(self):
        if self._database is None:
            self._database = create_engine(
                self.connection_string, client_encoding='utf8')
        return self._database

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = MetaData(bind=self.database, reflect=True)
        return self._metadata

    @property
    def base(self):
        if self._base is None:
            self._base = declarative_base(
                bind=self.database, metadata=self.metadata)
        return self._base

    @property
    def session(self):
        if self._session is None:
            _session = sessionmaker(self.database)
            self._session = _session()
        return self._session

    def simple_select(self, table):

        result = []
        table_entity = self.session.query(table)
        for entity in table_entity:
            result.append(entity)

        return result

    def simple_update(self, table, value):
        """
        <table_row_object>.<key> = <value>
        self.session.commit()
        """
        pass

    def create(self, table_row_object):
        self.session.add(table_row_object)
        self.session.flush()
        self.session.refresh(table_row_object)
        return table_row_object.id

    def create_or_update(self, table_row_object):
        """При сохранении текстов инофрмация может меняться от итерации к итерации, чтобы каждый раз
        не обрабатывать исключение и не дропать запись из БД сделан механизм обновления"""
        _class = table_row_object.__class__
        v = self.session.query(_class.id).filter(_class.code_name==table_row_object.code_name)

        if v.count() > 0:
            obj = self.session.query(table_row_object.__class__).get(v.first()[0])
            for item in table_row_object.__dict__:
                if item != '_sa_instance_state' and 'id' not in item:
                    new_value = table_row_object.__getattribute__(item)
                    obj.__setattr__(item, new_value)

            return v.first()[0]
        else:
            self.session.add(table_row_object)
            self.session.flush()
            self.session.refresh(table_row_object)
            return table_row_object.id

    def close_session(self):
        self.session.commit()

    def get_id(self, table, code_name=None):
        if code_name:
            v = self.session.query(table.id).filter(table.code_name==code_name)
            if v.count() > 0:
                return v.first()[0]

        return len(self.simple_select(table)) + 1


dbc = DataBaseConnection()


class Author(dbc.base):
    __tablename__ = 'authors'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code_name = Column(String, unique=True)


class Book(dbc.base):
    __tablename__ = 'books'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey('authors.id'))
    genre = Column(String)
    date = Column(String)
    code_name = Column(String, unique=True)


class Text(dbc.base):
    __tablename__ = 'texts'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    author_id = Column(Integer, ForeignKey('authors.id'))
    ngramms_array = Column(ARRAY(Integer, dimensions=1))
    parts_array = Column(ARRAY(Integer, dimensions=1))
    punct_array = Column(ARRAY(Integer, dimensions=1))
    code_name = Column(String, unique=True)
