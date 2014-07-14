# -*- coding: utf-8 -*-
# Name:         DataBase
# Purpose:      Objeto DataBase es un wrapper del mysql connector
#
# Author:       Pela
#
# Created:      11/03/2013
# Copyright:    (c) Pela 2013
import sys
import logging
from random import choice
from string import ascii_letters, digits

import mysql.connector
from mysql.connector import errorcode

from .Config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DBNAME


class MySQLCursorDict(mysql.connector.cursor.MySQLCursor):
    """Extiende a un class que hace la conversion del tipo de dato de mysql a uno de python"""
    def _row_to_python(self, rowdata, desc=None):
        row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
        if row:
            return dict(zip(self.column_names, row))
        return None


class DataBase(object):
    database_logger = logging.getLogger('Debug.DataBase')
    config = {'user': MYSQL_USER, 'password': MYSQL_PASSWORD, 'host': '127.0.0.1', 'database': MYSQL_DBNAME,
              'raise_on_warnings': False, 'use_unicode': True}

    def __init__(self):
        self.db = None

    def connect_mysql(self):
        """
        Establece la conexion con la base de datos con los parametros MYSQL_USER, MYSQL_PASS y MYSQL_DB que se definen
        en Config.py
        """
        try:
            self.db = mysql.connector.connect(**DataBase.config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.database_logger.critical("Something is wrong your username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self.database_logger.critical("Database does not exists")
            else:
                self.database_logger.critical("No puedo acceder a la base de datos.")
                self.database_logger.critical(err)
            sys.exit()

    def select(self, sql, args=None, fetch='one', user_id=None):
        """
        Realiza los SELECTS con el query que le pasamos.

        :type sql: str
        :param sql: string con la sentencia e busqueda de MySQL

        :type fetch: str
        :param fetch: Cuantos resultados debe devolver, one o all

        :type user_id: int|str
        :param user_id: id de usuario, sirbe para algunos procedures y functions de MySQL (default None)

        :return: data del select
        """
        data = None
        self.connect_mysql()
        cursor = self.db.cursor(cursor_class=MySQLCursorDict)
        try:
            if user_id is not None:
                cursor.execute("SET @user_id = {}".format(user_id))
            cursor.execute(sql, args)
        except Exception as e:
            self.database_logger.error("[{}] {} {}".format(e, sql, args))
            self.db.close()
        else:
            if fetch == 'one':
                data = cursor.fetchone()
            else:
                data = cursor.fetchall()
            cursor.close()
            self.db.close()
        return data

    def update(self, sql, args=None, user_id=None):
        """
        Realiza los UPDATES con el query que le pasamos.

        :type sql: str
        :param sql: string con la sentencia de update de MySQL

        :type user_id: int|str
        :param user_id: id de usuario, sirbe para algunos procedures y functions de MySQL (default None)

        :rtype: bool
        :return: True si se updateo correctamente
        """
        self.connect_mysql()
        cursor = self.db.cursor()
        try:
            if user_id is not None:
                cursor.execute("SET @user_id = {}".format(user_id))
            cursor.execute(sql, args)
        except Exception as e:
            self.database_logger.error("MYSQL UPDATE ERROR: {} ({})".format(e, sql))
            self.db.close()
            return False
        else:
            self.db.commit()
            self.db.close()
            return True

    def insert(self, sql, args=None, user_id=None):
        """
        Realiza los UPDATES con el query que le pasamos.

        :type sql: str
        :param sql: string con la sentencia de insert de MySQL

        :type user_id: int|str
        :param user_id: id de usuario, sirbe para algunos procedures y functions de MySQL (default None)

        :rtype: int
        :return: 0 si esta todo mal, != 0 cuando se inserto Ok
        """
        try:
            self.connect_mysql()
            cursor = self.db.cursor()
            if user_id is not None:
                cursor.execute("SET @user_id = {}".format(user_id))
            cursor.execute(sql, args)
            last_id = int(cursor.lastrowid)
        except Exception as e:
            self.database_logger.error("MYSQL INSERT ERROR: {} ({}) {}".format(e, sql, args))
            self.db.close()
            return 0
        else:
            self.db.commit()
            # cursor.close()
            self.db.close()
            return last_id

    def gen_code(self, table):
        """
        Genera el código del elemento de la tabla seleccionada, previo chequear que no exista en ella.

        :type table: str
        :param table: Nombre de la tabla.

        :return: El código generedo
        """
        sql = "SELECT id FROM {} WHERE code = {!r}"
        while 1:
            chars = ascii_letters + digits
            code = ''.join([choice(chars) for _ in range(8)])
            q_code = self.select(sql.format(table, code), None, 'one')
            if not q_code:
                return code

    def full_text_concat(self, asset_id):
        """
        Ejecuta en la base de datos el procedure fullTextConcat

        :type asset_id: int|str
        :param asset_id: Id del asset
        """
        self.connect_mysql()
        cursor = self.db.cursor()
        try:
            cursor.execute("CALL fullTextConcat({})".format(asset_id))
        except Exception as responce:
            self.database_logger.error("MYSQL INSERT ERROR: ({})".format(responce))
        self.db.close()


db = DataBase()