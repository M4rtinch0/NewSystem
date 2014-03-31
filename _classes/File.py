# -*- coding: utf-8 -*-
# Name:     File.py
# Purpose:  Manejar los encoders según los grupos.
#
# Author:   Pela
#
# Created:  07/03/2014
# Notas:
import logging

from .Inbox import Inbox
from .Tools import get_extension, get_file_name, get_file_type, is_playable
from .DataBase import db
from .FileVersion import FileVersion
from .MediaInspector import Mediainfo


class File:
    logger = logging.getLogger('Debug.File')
    VIDEO_TYPE = 'video'
    AUDIO_TYPE = 'audio'
    IMAGE_TYPE = 'image'
    DOC_TYPE = 'document'
    UNKNOWN_TYPE = 'unknown'

    def __init__(self, data=None):
        """
        Constructor
        Genera el nuevo asset en base de datos segun las opciones establecidas en el INBOX.
        :param data
        """
        self.id = None
        self.found = False
        self.playable = 'no'
        self.upload_path = None
        self.source_fv_id = None
        if id is not None:
            if type(data) is int:
                sql = ("SELECT f.id, f.name, f.type, f.code, f.asset_id, f.asset_order, f.active, f.main, a.owner) "
                       "FROM files f "
                       "LEFT JOIN assets a ON a.id = f.asset_id "
                       "WHERE f.id = {}")
                query = db.select(sql.format(data))
                if query is None:
                    return
                data = query

            if data:
                self.found = True
                self.id = data['id']
                self.name = data['name']
                self.type = data['type']
                self.code = data['code']
                self.asset_id = data['asset_id']
                self.asset_order = data['asset_order']
                self.active = data['active']
                self.main = data['main']
                self.owner = data['owner']

    def set_upload_path(self, path):
        self.upload_path = path
        self.name = get_file_name(path)
        self.type = get_file_type(get_extension(path))
        self.playable = is_playable(get_extension(path))

    def save(self):
        """
        Crea en Base de datos el File asociado al asset
        """
        sql = ("INSERT INTO files (name, type, code, asset_id, asset_order, active, main) "
               "VALUES "
               "(%(name)s, %(type)s, %(code)s, %(id)s, 0, 'yes', 'yes')")

        args = {"name": self.name,
                "type": self.type,
                "code": self.code,
                "id": self.asset_id}

        self.id = db.insert(sql, args, user_id=self.owner)
        if self.id is not None:
            self.found = True

    def create_source_versions(self, inbox_id):
        inbox = Inbox(inbox_id)
        media_inf = Mediainfo(self.upload_path)
        source_version = FileVersion()
        source_version.upload_path = media_inf.file_abs_path
        source_version.file_id = self.id
        source_version.type = self.type
        source_version.download = inbox.source_download
        source_version.owner = self.owner
        source_version.playable = self.playable
        if self.playable == 'yes' and inbox.source_def_def == 'yes':
            source_version.play_default = 'yes'
        source_version.extension = get_extension(self.upload_path)
        source_version.label = 'SOURCE'
        source_version.format_id = None
        source_version.engine = 'oxobox'
        source_version.source = 'yes'
        source_version.status = 'available'
        source_version.progress = None
        source_version.size = media_inf.info['general_size']
        source_version.playable_bberry = self.playable
        source_version.playable_iphone = self.playable
        source_version.playable_html5 = self.playable
        source_version.playable_flash = self.playable
        source_version.upload_to_s3 = 'no'
        source_version.s3_status = None
        if self.type == File.VIDEO_TYPE:
            source_version.width = media_inf.info['video_width']
            source_version.height = media_inf.info['video_height']
        if self.type == File.IMAGE_TYPE:
            source_version.width = media_inf.info['image_width']
            source_version.height = media_inf.info['image_height']
        if self.type == File.AUDIO_TYPE or self.type == File.VIDEO_TYPE:
            source_version.duration = media_inf.info['general_duration']
        source_version.save()
        return source_version