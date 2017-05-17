# coding: utf-8
"""
Модуль содержит набор классов для удобной работы с БД postgres harold
"""
from psycopg2 import connect
from config.settings import PHAROLD_SETTINGS


class MetaInformation(object):

    def __init__(self):
        self._connection_string = None
        self._cursor = None
        self._connection = None

    @property
    def connection_string(self):
        if self._connection_string is None:
            self._connection_string = 'host={host} port={port} dbname={dbname} user={user}'.format(
                **PHAROLD_SETTINGS)
        return self._connection_string

    @property
    def connection(self):
        if self._connection is None:
            self._connection = connect(self.connection_string)
        return self._connection

    @property
    def cursor(self):
        if self._cursor is None:
            self._cursor = self.connection.cursor()
        return self._cursor

    def _save_to_database(self, table, values):
        pass

    def select_from_database(self, table):
        select = """
            SELECT * FROM {table};
        """.format(table=table)

        self.cursor.execute(select)
        result = self.cursor.fetchall()

        return result
