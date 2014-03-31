# -*- coding: utf-8 -*-
# Name:     File.py
# Purpose:  Manejar los encoders según los grupos.
#
# Author:   Pela
#
# Created:  07/03/2014
# Notas:
import logging
from .DataBase import db


class FileVersion:
    logger = logging.getLogger('Debug.FileVersion')
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
        self.found = False
        self.upload_path = None
        self.type = None
        self.play_default = 'no'
        if data is not None:
            if type(data) is int:
                sql = ("SELECT fv.id, fv.file_id, fv.extension, fv.label, fv.format_id, fv.engine, fv.source, "
                       "fv.play_default, fv.status, fv.error_description, fv.progress, fv.size, fv.width, fv.height, "
                       "fv.duration, fv.playable, fv.download, fv.playable_bberry, fv.playable_iphone, "
                       "fv.playable_html5, fv.playable_flash, fv.upload_to_s3, fv.s3_status, a.owner, a.code "
                       "FROM files_versions fv "
                       "LEFT JOIN files f ON f.is = fv.file_id "
                       "LEFT JOIN assets a ON a.id = f.asset_id "
                       "WHERE fv.id = {}")
                query = db.select(sql.format(data))
                if query is None:
                    return
                data = query

            if data:
                self.found = True
                self.id = data['id']
                self.file_id = data['file_id']
                self.extension = data['extension']
                self.label = data['label']
                self.format_id = data['format_id']
                self.engine = data['engine']
                self.source = data['source']
                self.play_default = data['play_default']
                self.status = data['status']
                self.error_description = data['error_description']
                self.progress = data['progress']
                self.size = data['size']
                self.width = data['width']
                self.height = data['height']
                self.duration = data['duration']
                self.playable = data['playable']
                self.download = data['download']
                self.playable_bberry = data['playable_bberry']
                self.playable_iphone = data['playable_iphone']
                self.playable_html5 = data['playable_html5']
                self.playable_flash = data['playable_flash']
                self.upload_to_s3 = data['upload_to_s3']
                self.s3_status = data['s3_status']
                self.owner = data['owner']
                self.asset_code = data['code']

    def move(self):
        # esto va en el File, método, move_source_file()

        where = self.upload_path
        to = to_folder + "{}.{}".format(self.id, self.extension)

        try:
            shutil.move(where, to)
            os.chown(to, 5001, 1000)
            self.logger.info("mv %s %s", where, to)
        except Exception as e:
            self.logger.error("ASSET_FOLDER MOVE ERROR: {}".format(e))
        else:
            db.restoreTalliesBytes(self.source_file, self.user)
        return

    def save(self):
        if self.found:
            sql = "UPDATE "
        else:
            sql = "INSERT INTO "
        sql += ("files_versions (file_id, extension, label, format_id, engine, source, play_default, "
                "status, error_description, progress, size, width, height, duration, playable, download, "
                "playable_flash, playable_iphone, playable_html5)"
                "VALUES ({!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, "
                "{!r}, {!r}, {!r}, {!r}, {!r})")
        sql = sql.format(self.file_id, self.extension, self.label, self.format_id, self.engine, self.source,
                         self.play_default, self.status, self.error_description, self.progress, self.size,
                         self.width, self.height, self.duration, self.playable, self.download, self.playable_flash,
                         self.playable_iphone, self.playable_html5)
        print(sql)
        #self.id = db.insert(sql, self.owner)
        #if self.id is not None:
        #    self.found = True

    def update_status(self, status, description=None):
        sql = "UPDATE files_versions SET status = {!r}, "
        if description:
            sql += "error_description = {!r}, ".format(description)
        sql += "encode_start = NOW() WHERE id = {}"
        db.update(sql.format(status, self.id))

    def update_thumb(self, status):
        sql = "UPDATE files_versions SET thumb = {!r} WHERE id = {}"
        db.update(sql.format(status, self.id))