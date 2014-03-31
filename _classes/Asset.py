# -*- coding: utf-8 -*-
# Name:     Asset.py
# Purpose:  Obj Asset
#
# Author:   Pela
#
# Created:  07/03/2014
# Notas:
import os
import logging
from .Inbox import Inbox
from .Config import ASSET_FOLDER
from .DataBase import db


class Asset:
    logger = logging.getLogger('Debug.Asset')

    def __init__(self, data=None):
        """
        Class Asset

        :type data: dict|None|int|str
        :param data: Si es un int o un string es el Id del asset y toma los datos de la db, sino es un dict con los
            datos (default None)
        """
        self.found = False
        if data is not None:
            if type(data) is int or type(data) is str:
                sql = ("SELECT a.id, a.title, a.code, a.owner, a.inbox, a.privacy, a.comments, a.externalembed, "
                       "a.player_template, a.advertising, a.rating, a.interstice, a.updated, a.cat_ids "
                       "FROM assets a "
                       "WHERE a.id = {}")
                query = db.select(sql.format(data))
                if query is None:
                    return
                data = query

            if data:
                self.found = True
                self.id = data['id']
                self.title = data['title']
                self.code = data['code']
                self.owner = data['onwer']
                self.inbox_id = data['inbox']
                self.privacy = data['privacy']
                self.comments = data['comments']
                self.externalembed = data['externalembed']
                self.player_template = data['player_template']
                self.advertising = data['advertising']
                self.rating = data['rating']
                self.interstice = data['interstice']
                self.updated = data['updated']
                self.cat_ids = data['cat_ids']

    def add_to_playlist(self):
        """
        HARDCODE
        Esto en principio es solo para OXOCIAL, agrega el asset a un playlist especifico.
        """
        if self.owner == 430:
            sql = "INSERT INTO playlist_items(playlist_id, asset_id) VALUES(112953, {})"
        else:
            sql = "INSERT INTO playlist_items(playlist_id, asset_id) VALUES(112911, {})"
        db.insert(sql.format(self.id), user_id=self.owner)

    def set_defaults(self, inbox_id):
        inbox = Inbox(inbox_id)
        self.set_default_tags(inbox.get_tags())
        self.set_default_shareds(inbox.get_shareds())
        self.set_default_metadata(inbox.get_metadata())

    def set_default_tags(self, tags=None):
        """
        Asocia los tags definidos en el INBOX al asset recien creado.

        :type tags: str
        :param tags: String con los datos de la metadata default (default None)
        """
        #Si hay tags definido los insertamos en la base de datos ligados al ID del asset creado.
        if tags is not None:
            tags = tags.split(',')
            taglist = []
            sql = "INSERT INTO asset_tags (asset_id, tag) VALUES "
            for tag in tags:
                if tag is not None and tag != "":
                    taglist.append("({}, {!r})".format(self.id, tag))
            if len(taglist):
                sql += ','.join(taglist)
                db.insert(sql, user_id=self.owner)

    def set_default_shareds(self, shares=None):
        """
        Asocia el asset a los usarios compartidos por default.

        :type shares: dict
        :param shares:  Lista con los datos del las comparticiones default (default None)
        """
        if shares is not None:
            sql = ("INSERT INTO assets_shared (user_from, user_to, group_to, asset_id, editable) "
                   "VALUES ")
            sharelist = []
            for share in shares:
                sharelist.append("({}, {}, {}, {}, {!r})".format(self.owner,
                                                                 share['user_to'] if share['user_to'] else 'NULL',
                                                                 share['group_to'] if share['group_to'] else 'NULL',
                                                                 self.id,
                                                                 share['editable']))
            if len(sharelist):
                sql += ','.join(sharelist)
                db.insert(sql, user_id=self.owner)

    def set_default_metadata(self, metadatas=None):
        """
        Asocia la metadatada que se definio en el INBOX al asset recien creado.

        :type metadatas: dict
        :param metadatas:  Lista con los datos de la metadata default (default None)
        """
        if metadatas is not None:
            sql = ("INSERT INTO asset_metadata (asset_id, field_id, label, value, user_id, asset_order, public)"
                   "VALUES ")
            mdlist = []
            for md in metadatas:
                mdlist.append("({}, {}, {!r}, {!r}, {}, {}, {!r})").format(
                    self.id,
                    md['field_id'] if md['field_id'] else 'NULL',
                    md['label'],
                    md['value'] if md['value'] else 'NULL',
                    self.owner,
                    md['order'],
                    md['public'])

            if len(mdlist):
                sql += ','.join(mdlist)
                db.insert(sql, user_id=self.owner)

    def create_folder(self, group):
        """
        Crea la carpeta del asset y obra según se tenga que guardar el SOURCE o no.

        :type group: str|int
        :param group: Id del grupo
        """
        # to_folder = "{}/{}/{}".format(ASSET_FOLDER, group, self.code)
        # if not os.path.isdir(to_folder + 'thumbs/'):
        #     try:
        #         os.umask(0)
        #         os.makedirs(to_folder + 'thumbs/', 755)
        #         os.chown(to_folder, 5001, 1000)
        #         os.chown(to_folder + 'thumbs/', 5001, 1000)
        #     except Exception as e:
        #         self.logger.error("ASSET_FOLDER MKDIRS ERROR: {}".format(e))

    def save(self):
        """
        Inserta en la db todos los datos del asset
        """
        sql = ("INSERT INTO assets (title, code, owner, inbox, privacy, comments, externalembed, "
               "player_template, advertising, rating, interstice, updated, cat_ids) "
               "VALUES "
               "(%(title)s, %(code)s, %(owner)s, %(inbox)s, %(privacy)s, %(comments)s, %(externalembed)s, "
               "%(player_template)s, %(advertising)s, %(rating)s, %(interstice)s, NOW(), %(cat_ids)s)")

        args = {'title': self.title,
                'code': self.code,
                'owner': self.owner,
                'inbox': self.inbox_id,
                'privacy': self.privacy,
                'comments': self.comments,
                'externalembed': self.externalembed,
                'player_template': self.player_template,
                'advertising': self.advertising,
                'rating': self.rating,
                'interstice': self.interstice,
                'cat_ids': self.cat_ids}

        # AGREGAR NOTIFICACIONES
        self.id = db.insert(sql, args, self.owner)
        if self.id is not None:
            self.found = True
            db.full_text_concat(self.id)