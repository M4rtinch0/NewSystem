# -*- coding: utf-8 -*-
# Name:     Inbox.py
# Purpose:  Obj Inbox
#
# Author:   Pela
#
# Created:  07/03/2014
# Notas:
from .DataBase import db
from .Format import Format


class Inbox:
    def __init__(self, data=None, group=None):
        """
        Class Inbox

        :type data: int|str
        :param data: Es el id del inbox
        """
        self.found = False
        if data is not None:
            sql = "SELECT i.* FROM inboxes i "
            if type(data) is str:
                sql += "WHERE i.name = {!r} "
            if type(data) is int:
                sql += "WHERE i.id = {} "
            if group is not None:
                sql += "AND i.group = {}".format(group)

            query = db.select(sql.format(data))
            if query:
                self.found = True
                self.id = query['id']
                self.inbox_name = query['name']
                self.def_asset_privacy = query['default_asset_privacy']
                self.def_asset_comments = query['default_asset_comments']
                self.def_asset_external_embed = query['default_asset_externalembed']
                self.def_advertising = query['default_advertising']
                self.def_rating = query['default_rating']
                self.def_player_template = query['default_player_template']
                self.def_interstice = query['default_interstice']
                self.s3_upload = query['s3_upload']
                self.source_def_playable = query['source_playable']
                self.source_download = query['source_download']
                self.source_def_def = query['source_default']

    def get_categories(self):
        """
        Selecciona de la base de datos los id de las categorias definidas en el inbox

        :rtype : str
        :return: Si el query fue satisfactorio devuelve un string con los ids concatenados, sino None
        """
        sql = ("SELECT GROUP_CONCAT(DISTINCT c.category_id SEPARATOR ' ') as ids "
               "FROM inboxes i "
               "LEFT JOIN inbox_has_category c ON c.inbox_id = i.id "
               "WHERE i.id = {}")
        query = db.select(sql.format(self.id))
        if query:
            return query['ids']
        return ''

    def get_tags(self):
        """
        Selecciona de la base de datos los tags definidas en el inbox

        :rtype : None|str
        :return: Si el query fue satisfactorio devuelve un string con los tags concatenados, sino None
        """
        sql = ("SELECT GROUP_CONCAT(DISTINCT t.tag SEPARATOR ',') as tags "
               "FROM inboxes i "
               "LEFT JOIN inbox_has_tag t ON t.inbox_id = i.id "
               "WHERE i.id = {}")
        query = db.select(sql.format(self.id))
        if query:
            return query['tags']
        return None

    def get_formats(self, f_type):
        """
        Devuelve los formatos asociados al inbox para el tipo de archivo que sea el SOURCE.

        :type f_type: str
        :param f_type: Tipo de archivo video|audio|image|document

        :rtype : list
        :return: Si el query fue satisfactorio devuelve un list con objetos Format, sino None
        """
        sql = ("SELECT ihf.format_id, ihf.download, ihf.play_default, ihf.playable, f.label, f.format, "
               "f.engine, f.playable_flash, f.playable_iphone, f.playable_html5, f.playable_bberry, f.cmd "
               "FROM inbox_has_format ihf "
               "LEFT JOIN formats f ON f.id = ihf.format_id "
               "WHERE ihf.inbox_id = {} "
               "AND f.type = {!r}").format(self.id, f_type)
        query = db.select(sql, fetch='all')
        formats = []
        if query is not None:
            for q in query:
                formats.append(Format(q))
        return formats

    def get_shareds(self):
        """
        Devuelve los shareds por default que asigna el inbox.

        :rtype : None|dict
        :return: Si el query fue satisfactorio devuelve un dict con los resuldatos del query
        """
        sql = ("SELECT ids.user_to, ids.group_to, ids.editable "
               "FROM inbox_default_shared ids "
               "WHERE ids.inbox_id = {}").format(self.id)
        shares = db.select(sql, fetch='all')
        if shares:
            return shares
        return None

    def get_metadata(self):
        """
        Asocia la metadata por default estipulada en el inbox al asset recien creado.

        :rtype : None|dict
        :return: Si el query fue satisfactorio devuelve un dict con los resuldatos del query
        """
        # Seleccionamos la metadata default asociada al inbox.
        sql = ("SELECT idm.field_id, idm.label, idm.value, idm.public, idm.order "
               "FROM inbox_default_metadata idm "
               "WHERE idm.inbox_id = {}").format(self.id)
        metadatas = db.select(sql, fetch='all')
        if metadatas:
            return metadatas
        return None