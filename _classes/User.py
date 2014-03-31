# -*- coding: utf-8 -*-
# Name:     User.py
# Purpose:  Objeto usuario.
#
# Author:   Pela
#
# Created:  07/03/2014
# Notas:
import logging
from .DataBase import db


class User:
    logger = logging.getLogger('Debug.User')

    def __init__(self, data=None, path=None):
        """
        Class User

        :type data: None|int|str|dict
        :param data: Si es int o string quiere decir que es el id del formato, sino se le pasa un dict con los datos
            para iniciar el objeto (default None)

        :type path: None|str
        :param path: Path del archivo subido (default None)
        """
        self.found = False
        self.ftp_upload_dir = path
        self.inbox_id = None
        if data is not None:
            sql = "SELECT u.id, u.userid, u.group, u.homedir FROM users u "
            if type(data) is int:
                sql += "WHERE u.id = {}"
            if type(data) is str:
                sql += "WHERE u.userid = {!r}"
            query = db.select(sql.format(data))
            if query is None:
                return

            data = query
            if data:
                self.found = True
                self.id = data['id']
                self.userid = data['userid']
                self.group = data['group']
                self.homedir = data['homedir']

    def check_inbox(self, inbox_id):
        """
        Chequea si el inbox existe

        :type inbox_id: int
        :param inbox_id: Id del inbox

        :rtype: bool
        :return: True si existe, False si no es así
        """
        sql = "SELECT * FROM user_has_inbox uhi WHERE uhi.user_id = {} AND uhi.inbox_id = {}"
        query = db.select(sql.format(self.id, inbox_id))
        if query:
            return True
        return False

    def check_asset_space(self):
        """
        Chequea el espacio en disco utilizado por Todo los assets del grupo del usuario, si se exedio de la cuota
        no crea el asset.

        :rtype: bool
        :return: Devuelve True si no se excedio, False si lo hizo.
        """
        sql = ("SELECT SUM(fv.size) as size "
               "FROM assets a "
               "JOIN files f ON  f.asset_id = a.id "
               "JOIN files_versions fv ON fv.file_id = f.id "
               "JOIN users u ON u.id = a.owner "
               "WHERE u.group = {}").format(self.group)
        data = db.select(sql)
        if data:
            total_size_used = data['size']
            sql = "SELECT assets_space_limit FROM groups g WHERE g.id = {}".format(self.group)
            data = db.select(sql)
            if data:
                assets_space_limit = data['assets_space_limit']
                self.logger.info("{} < {}".format(total_size_used, assets_space_limit))
                if total_size_used < assets_space_limit:
                    return True
        return False