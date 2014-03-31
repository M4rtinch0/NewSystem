# -*- coding: utf-8 -*-
# Name:         Format
# Purpose:      Objeto Format 
#
# Author:       Pela
#
# Created:      11/03/2013
# Notas:
import logging
from json import loads
from .Tools import send_mail
from .DataBase import db
from .FileVersion import FileVersion


class Format(object):
    logger = logging.getLogger('Debug.Format')

    def __init__(self, data=None):
        """
        Class Format

        :type data: dict|None|int|str
        :param data: Si es Int o Str quiere decir que es el id del formato, sino se le pasa un dict con los datos
            para iniciar el objeto (default None)
        """
        self.found = False
        if data is not None:
            if type(data) is int or type(data) is str:
                sql = ("SELECT fo.id, fo.name, fo.label, fo.engine, fo.type, fo.format_id, fo.extension, fo.hd "
                       "fo.smart_encode, fo.paid_format, fo.playable_in,  fo.watermark, fo.edition, fo.command, "
                       "ihf.download, ihf.play_default, ihf.playable, i.s3_upload "
                       "FROM formats f "
                       "LEFT JOIN inbox_has_format ihf  ON ihf.format_id = f.id "
                       "LEFT JOIN inbox i ON i.id = ihf.inbox_id "
                       "WHERE f.id = {}").format(data)

                query = db.select(sql)
                if query is None:
                    return
                data = query

            if data:
                self.found = True
                self.id = data['id']
                self.name = data['name']
                self.label = data['label']
                self.engine = data['engine']
                self.type = data['type']
                self.format_id = data['format_id']
                self.extension = data['extension']
                self.hd = data['hd']
                self.smart_encode = data['smart_encode']
                self.paid_format = data['paid_format']
                self.playable_in = data['playable_in']
                self.watermark = data['watermark']
                self.edition = data['edition']
                self.command = data['command']
                self.download = data['download']
                self.play_default = data['play_default']
                self.playable = data['playable']
                self.s3_upload = data['s3_upload']

    def create_version(self, file_id, user_id):
        """
        Genera el file version segun la especificaciones del formato

        :type file_id: int|str
        :param file_id: Id del file

        :type user_id: int|str
        :param user_id: Id del usuario
        """
        self.logger.debug("Creando version: ")
        file_version = FileVersion()
        upload_to_s3 = 'no'
        s3_status = 'none'

        if self.play_default == 'yes':
            if self.s3_upload == 'yes':
                upload_to_s3 = 'yes'
                s3_status = 'queued'

        status = 'queued'

        if self.engine == 'manual':
            status = 'none'

        file_version.file_id = file_id
        file_version.extension = self.extension
        file_version.label = self.label
        file_version.format_id = self.id
        file_version.engine = self.engine
        file_version.source = 'no'
        file_version.play_default = self.play_default
        file_version.status = status
        file_version.progress = None
        file_version.size = None
        file_version.width = None
        file_version.height = None
        file_version.duration = None
        file_version.playable = self.playable
        file_version.download = self.download
        data = loads(self.playable_in)
        file_version.playable_bberry = data['bberry']
        file_version.playable_iphone = data['iphone']
        file_version.playable_html5 = data['html5']
        file_version.playable_flash = data['flash']
        file_version.upload_to_s3 = upload_to_s3
        file_version.s3_status = s3_status
        file_version.owner = user_id
        file_version.save()

        # Si el engine es manual y se inserto correctamente en la db, mandamos un email
        if self.engine == 'manual' and file_version.id:
            send_mail('manualfv', id, 'notification')