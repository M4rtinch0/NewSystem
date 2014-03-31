# -*- coding: utf-8 -*-
# Name:     EImage.py
# Purpose:  Obj Asset
#
# Author:   Pela
#
# Created:  07/03/2014
# Notas:
import logging
from PIL import Image
from json import loads
from _classes.Config import file_path, errors, thumb_path
from _classes.Tools import file_exist, send_mail
from _classes.DataBase import db
from _classes.FileVersion import FileVersion
from _classes.Format import Format
from _classes.MediaInspector import Mediainfo


class EImage:
    logger = logging.getLogger('Debug.EImage')

    RESIZE_FIT = 'fit'
    RESIZE_PERC = 'perc'
    RESIZE_FORCE = 'force'

    sql = ("SELECT fv.id, fv.file_id, fv.extension, fv.label, fv.format_id, fv.engine, fv.source, "
           "fv.play_default, fv.status, fv.progress, fv.size, fv.width, fv.height, fv.duration, "
           "fv.playable, fv.download, fv.playable_bberry, fv.playable_iphone, fv.playable_html5, "
           "fv.playable_flash, fv.upload_to_s3, fv.s3_status, a.owner, a.code "
           "FROM files_versions fv "
           "LEFT JOIN files f ON f.id = fv.file_id "
           "LEFT JOIN assets a ON a.id = f.asset_id "
           "LEFT JOIN users u ON u.id = a.owner "
           "WHERE u.group = {} AND f.type = 'image' AND fv.engine = 'oxobox' AND fv.status = 'queued' "
           "ORDER BY  play_default ASC, fv.id ASC")

    def __init__(self, data=None):
        """ Crea el Encoder con los datos necesarios segun el ID de grupo. """
        self.found = False
        self.input = None
        self.output = None
        self.output_thumb = None
        self._pil_image = None
        self.error = None
        self.thumb_sizes = None
        self.quality = None
        self.rotate = None
        self.resize_type = None
        self.resize_data = None
        if data is not None:
            self.group_id = data
            #Seleccionamos algun FileVersion que este para encodearse
            query = db.select(EImage.sql.format(self.group_id))
            if query:
                self.found = True
                self.version = FileVersion(query)
                self.format = Format(self.version.format_id)
                self.source_file = self.get_source_file()
                if self.source_file.found is not None:
                    # /oxobox/assets/{}/{}/{}.{}
                    self.input = file_path.format(self.group_id, self.version.asset_code, self.source_file.id,
                                                  self.source_file.extension)
                    self.output = file_path.format(self.group_id, self.version.asset_code, self.version.id,
                                                   self.version.extension)
                    self.output_thumb = thumb_path.format(self.group_id, self.version.asset_code,
                                                          "{}.jpg".format(self.version.id))

    def get_source_file(self):
        sql = ("SELECT fv.id "
               "FROM files_versions fv "
               "WHERE fv.file_id = {} AND fv.source = 'yes' AND fv.status = 'available'")
        query = db.select(sql.format(self.version.file_id))
        return FileVersion(query['id'])

    def parse_command(self):
        # '{"thumb_sizes":"99999x99999","quality":"vpoor"|"poor"|"good"|"vgood"|"excelent",
        # "rotate":"0-360","resize":[{"type":"fit|perc|force"},{"data":"99999x99999|0-100"}]}'
        try:
            command = loads(self.format.command)
            self.thumb_sizes = command['thumb_sizes']
            self.quality = command['quality']
            self.rotate = command['rotate']
            self.resize_type = command['resize']['type']
            self.resize_data = command['resize']['data']
        except Exception as responce:
            self.logger.debug("Error al parsear: {}".format(responce))
            return 0
        else:
            return 1

    def encode(self):
        self.start()
        if self.error is None:
            self.do_resize()
        if self.error is None:
            self.apply_watermark()
        self.complete()

    def start(self):
        self.logger.info("[{}] [{}] [{}] - Start Encoding".format(self.group_id, self.version.id,
                                                                  self.version.asset_code))
        self.version.update_status('encoding')

        if not file_exist(self.input):
            self.logger.error(("[{}] [{}] [{}] - START ENCODING ERROR: "
                               "El input no existe").format(self.group_id, self.source_file.id,
                                                            self.source_file.asset_code))
            self.error = errors['input']

    def do_resize(self):
        try:
            self._pil_image = Image.open(self.input)

            if self.resize_type == EImage.RESIZE_PERC:
                width, height = self._pil_image.size
                factor = int(self.resize_data) / float(100)
                size = (int(width * factor), int(height * factor))
            else:
                width, height = self.resize_data.split('x')
                size = (int(width), int(height))  # Una tupla de int, es lo que recibe thumbnail

            if self.resize_type == EImage.RESIZE_FIT:
                self._pil_image.thumbnail(size, Image.ANTIALIAS)
            else:
                self._pil_image = self._pil_image.resize(size, Image.ANTIALIAS)

            self._pil_image = self._pil_image.rotate(int(self.rotate))
            if self._pil_image.mode != 'RGBA':
                self._pil_image = self._pil_image.convert('RGBA')
        except IOError:
            self.logger.error("[{}] [{}] [{}] - ERROR: No existe".format(self.group_id, self.version.id,
                                                                         self.version.asset_code))
            self.error = errors['copen']
        except Exception as responce:
            self.logger.error("[{}] [{}] [{}] - RESISZE ERROR: {}".format(self.group_id, self.version.id,
                                                                          self.version.asset_code, responce))
            self.error = errors['eresize']

    def complete(self):
        try:
            self._pil_image.save(self.output, quality=self.quality)
        except Exception as responce:
            self.logger.error("[{}] [{}] [{}] - ERROR: No se pudo salvar {}".format(self.group_id, self.version.id,
                                                                                    self.version.asset_code, responce))
            self.error = errors['save']

        media_info = Mediainfo(self.output)

        if not media_info.found:
            self.logger.error("[{}] [{}] [{}] - ERROR: No existe el output fiel".format(self.group_id,
                                                                                        self.version.id,
                                                                                        self.version.asset_code))
            self.error = errors['output']

        if self.error is not None:
            send_mail('System', self.version.id, 'error')
            self.logger.error("Hubo un error al encodear, no existe el archivo de la version ({})".format(
                self.version.id))
            self.version.status = 'error'
            self.version.error_description = self.error
        else:
            self.logger.info("{} {} {} - Encoding Complete".format(self.group_id, self.version.id,
                                                                   self.version.asset_code))
            self.gen_thumb()
            self.version.status = 'available'
            self.version.size = media_info.info['general_size']
            self.version.progress = 100
            width, height = self._pil_image.size
            self.version.width = width
            self.version.height = height
        self.version.save()
        return

    def apply_watermark(self):
        if self.format.watermark is None:
            return

        self.logger.info("Aplico Watermark")

        try:
            watermark = loads(self.format.watermark)
            position = watermark['pos']
            perc = watermark['perc']
            path = watermark['path']
        except Exception as responce:
            self.logger.error("[{}] [{}] [{}] - WaterMarking Error: {}".format(self.group_id, self.version.id,
                                                                               self.version.asset_code, responce))
            self.error = errors['eresize']
            return

        #Layer transparente para dibujar el watermark sobre el
        layer = Image.new('RGBA', self._pil_image.size, (0, 0, 0, 0))

        try:
            mark = Image.open(path)
        except Exception as responce:
            self.logger.error("[{}] [{}] [{}] - WaterMarking Error: {}".format(self.group_id, self.version.id,
                                                                               self.version.asset_code, responce))
            self.error = errors['eresize']
            return

        factor = int(perc) / float(100)
        mark_width, mark_height = mark.size
        mark_aspect = mark_width / float(mark_height)
        mark_width = int(self._pil_image.size[0] * factor)
        mark_height = int(mark_width / float(mark_aspect))

        try:
            #Esto es por si la marca es grande
            mark = mark.resize((mark_width, mark_height), Image.ANTIALIAS)
        except Exception as responce:
            self.logger.error("[{}] [{}] [{}] - WaterMarking Error: Resize mark {}".format(self.group_id,
                                                                                           self.version.id,
                                                                                           self.version.asset_code,
                                                                                           responce))
            self.error = errors['eresize']
            return

        if position == 'bottom-left':
            position = (0, (self._pil_image.size[1] - mark_height))
        elif position == 'bottom-right':
            position = ((self._pil_image.size[0] - mark_width), (self._pil_image.size[1] - mark_height))
        elif position == 'top-left':
            position = (0, 0)
        elif position == 'top-right':
            position = ((self._pil_image.size[0] - mark_width), 0)
        else:
            position = ((self._pil_image.size[0] - mark_width) / 2, (self._pil_image.size[1] - mark_height) / 2)

        layer.paste(mark, position)
        self._pil_image.paste(layer, None, layer)

    def gen_thumb(self):
        self.version.update_thumb('generating')
        try:
            thumb = self._pil_image
            t_width, t_height = self.thumb_sizes.split('x')
            thumb.thumbnail((t_width, t_height))
            thumb = thumb.rotate(int(self.rotate))

            if thumb.mode != 'RGBA':
                thumb = thumb.convert('RGBA')

            thumb.save(self.output_thumb)
        except Exception as responce:
            self.logger.error("[{}] [{}] [{}] - GEN THUMB ERROR: {}".format(self.group_id, self.version.id,
                                                                            self.version.asset_code, responce))
            self.version.update_thumb('error')
        else:
            self.version.update_thumb('done')