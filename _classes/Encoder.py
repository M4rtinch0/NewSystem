# -*- coding: utf-8 -*-
# Name:     Encoder
# Purpose:  Clase base para el encodeo
#
# Author:   Pela
#
# Created:  11/03/2013
# Notas:
import os
from .DataBase import db
import Config


class Encoder:
    """ Maneja el encodeo de las imagenes. """

    sql_version = ("SELECT fv.*, fo.id as formatid, fo.format, fo.image_quality, fo.image_resize, fo.image_rotate, "
                   "fo.watermark, fo.w_pos, fo.w_perc, a.code, a.id as asset_id, a.owner "
                   "FROM files_versions fv "
                   "LEFT JOIN files f ON f.id = fv.file_id "
                   "LEFT JOIN assets a ON a.id = f.asset_id "
                   "LEFT JOIN users u ON u.id = a.owner "
                   "LEFT JOIN formats fo ON fo.id = fv.format_id "
                   "WHERE u.group = {} AND f.type = {} AND fv.engine = 'oxobox' AND fv.status = 'queued' "
                   "ORDER BY  play_default ASC, fv.id ASC")
    sql_format = ("")
    id = None
    group_id = None
    errors = None
    canceled = 'no'
    format_id = ""
    file_id = ""
    format = ""
    extension = ""
    code = ""
    asset_id = ""
    owner = ""
    quality = ""
    rotate = ""
    watermark = ""
    w_pos = ""
    w_perc = ""
    input = ""
    output = ""

    def __init__(self, data=None):
        """ Crea el Encoder con los datos necesarios segun el ID de grupo. """
        if data is not None:
            self.group_id = data
            #Seleccionamos algun FileVersion que este para encodearse
            query = db.select(sql, args)
            if query:
                source_av = self.check_source_availability(query)
                if not source_av:
                    return

                self.id = query['id']
                self.format_id = query['formatid']
                self.file_id = query['file_id']
                self.format = query['format']
                self.extension = query['extension']
                self.code = query['code']
                self.asset_id = query['asset_id']
                self.owner = query['owner']
                self.quality = Config.imagesQ[query['image_quality']]
                self.rotate = query['image_rotate']
                self.watermark = query['watermark']
                self.w_pos = query['w_pos']
                self.w_perc = query['w_perc']
                self.input = Config.assetFolder % (self.group_id, self.code)
                self.output = Config.assetFolder % (self.group_id, self.code)
                self.getResizeType(query['image_resize'])

                #Seleccionamos el SOURCE
                sql = "SELECT id, extension FROM files_versions WHERE file_id = %(id)s AND source = 'yes' AND status = 'available'"
                args = {
                    'id': self.file_id
                }
                query = db.select(sql, args)
                #Si no existe SOURCE en el la base de datos de FileVersion es porque no hay que guardarlo
                if not query:
                    _debugger.error("NO EXISTE EL SOURCE \"%s\"", sql)
                    return

                self.input += str(query['id']) + '.' + query['extension']

                #Seteamos el watermark
                if self.watermark == 'yes':
                    self._wPath = Config.waterPath % self.format_id

                    if not os.path.exists(self._wPath):
                        self.watermark = 'no'

                #Si el input no existe mandamos error
                if not os.path.exists(self.input):
                    _debugger.error("[%s] [%s] [%s] - %s", self.group_id, self.id, self.code, Config.errors['input'])
                    self.errorHandler('input')
                    return

                self.output += str(self.id) + '.' + self.extension

    @staticmethod
    def check_source_availability(file_id):
        sql = ("SELECT fv.status "
               "FROM files_versions fv "
               "WHERE fv.file_id = {} AND fv.source = 'yes' AND fv.status = 'available'")
        query = db.select(sql.format(file_id))
        if query:
            return True
        return False

    def errorHandler(self, error):
        """ Maneja los errores. """

        _debugger.error(Config.errors[error])
        self.errors = Config.errors[error]

    def startEncoding(self):
        """" Arranca el encodeo, actualiza en base de datos es estado de encodeo. """

        _debugger.info("[%s] [%s] [%s] - Start Encoding", self.group_id, self.id, self.code)
        sql = """
                UPDATE
                        files_versions
                SET
                        status = 'encoding',
                        encode_start = NOW()
                WHERE
                        id = %(id)s
        """
        args = {
            'id': self.id
        }
        db.update(sql, args)

        #Creamos el objeto imagen con el INPUT
        try:
            self._image = Image.open(self.input)
        except Exception, e:
            _debugger.error("[%s] [%s] [%s] - START ENCODING ERROR: %s", self.group_id, self.id, self.code, e)
            self.errorHandler('copen')
            return

        #Definimos que tipo de Resize vamos a hacer
        if self._resizeType == 'perc':
            self.resizePerc()
        elif self._resizeType == 'fit':
            self.resizeFit()
        else:
            self.resizeForce()

        if self.watermark == 'yes':
            self.applyWatermark()

        return

    def getResizeType(self, data):
        """ Devuelve que tipo de resize se le va a hacer a la imagen, dependiendo de los datos de base de datos. """

        if '%' in data:
            self._resizeType = 'perc'
            self.size = data[:-1]
        elif '>' in data:
            self._resizeType = 'fit'
            self.size = data[:-1]
        else:
            self._resizeType = 'force'
            self.size = data
        return

    def resizeFit(self):
        """ Resize para que quepa en el tamanio dado, manteniendo el aspecto. """
        try:
            self._encodedIm = self._image
            W, H = self.size.split('x')
            size = int(W), int(H)
            self._encodedIm.thumbnail(size)
            self._encodedIm = self._encodedIm.rotate(int(self.rotate))

            if (self._encodedIm.mode != 'RGBA'):
                self._encodedIm = self._encodedIm.convert('RGBA')

            self._encodedIm.save(self.output, quality=self.quality)
        except Exception, e:
            _debugger.error("[%s] [%s] [%s] - RESISZE FIT ERROR: %s", self.group_id, self.id, self.code, e)
            self.errorHandler('eresize')

        return

    def resizePerc(self):
        """ Resizeo por porcentaje. """
        try:
            self._encodedIm = self._image
            W, H = self._encodedIm.size
            factor = int(self.size) / float(100)
            size = int(W * factor), int(H * factor)
            self._encodedIm = self._encodedIm.resize(size, Image.ANTIALIAS)
            self._encodedIm = self._encodedIm.rotate(int(self.rotate))

            if (self._encodedIm.mode != 'RGBA'):
                self._encodedIm = self._encodedIm.convert('RGBA')

            self._encodedIm.save(self.output, quality=self.quality)
        except Exception, e:
            _debugger.error("[%s] [%s] [%s] - RESISZE PERC ERROR: %s", self.group_id, self.id, self.code, e)
            self.errorHandler('eresize')

        return

    def resizeForce(self):
        """ Resize forzado, fuerza a una medida dada si importar el aspecto. """

        try:
            self._encodedIm = self._image
            W, H = self.size.split('x')
            size = int(W), int(H)
            self._encodedIm = self._encodedIm.resize(size, Image.ANTIALIAS)
            self._encodedIm = self._encodedIm.rotate(int(self.rotate))

            if (self._encodedIm.mode != 'RGBA'):
                self._encodedIm = self._encodedIm.convert('RGBA')

            self._encodedIm.save(self.output, quality=self.quality)
        except Exception, e:
            _debugger.error("[%s] [%s] [%s] - RESISZE FORCE ERROR: %s", self.group_id, self.id, self.code, e)
            self.error_handler('eresize')
        return

    def applyWatermark(self):
        """ Aplica la marca de agua a la imagen encodeada. """
        _debugger.info("Aplico Watermark")
        position = self.w_pos
        _debugger.info(position)
        _debugger.info(self._wPath)

        try:
            im = self._encodedIm
        except Exception, e:
            _debugger.error("[%s] [%s] [%s] - WaterMarking Error: %s", self.group_id, self.id, self.code, e)
            self.errorHandler('eresize')

        #Layer transparente para dibujar el watermark sobre el
        layer = Image.new('RGBA', im.size, (0, 0, 0, 0))

        try:
            mark = Image.open(self._wPath)
        except Exception, e:
            _debugger.error("[%s] [%s] [%s] - WaterMarking Error: %s", self.group_id, self.id, self.code, e)
            self.errorHandler('eresize')

        _debugger.info(self.w_perc)

        #Tamanio del watermark definido por porcentaje
        if self.w_perc != None:
            perc = int(self.w_perc) / float(100)
            _debugger.info(perc)
            mW, mH = mark.size
            mA = mW / float(mH)
            mW = int(im.size[0] * perc)
            mH = int(mW / float(mA))

            try:
                #Esto es por si la marca es grande
                mark = mark.resize((mW, mH), Image.ANTIALIAS)
            except Exception, e:
                _debugger.error("RESISZE MARK ERROR: %s", e)

        mW, mH = mark.size
        _debugger.info((mW, mH))

        if position == 'bottom-left':
            position = (0, (im.size[1] - mH))
        elif position == 'bottom-right':
            position = ((im.size[0] - mW), (im.size[1] - mH))
        elif position == 'top-left':
            position = (0, 0)
        elif position == 'top-right':
            position = ((im.size[0] - mW), 0)
        else:
            position = ((im.size[0] - mW) / 2, (im.size[1] - mH) / 2)

        layer.paste(mark, position)
        im.paste(layer, None, layer)
        im.save(self.output, quality=self.quality)

        return

    def genThumb(self):
        """ Genera un thumb de la imagen encodeada. """
        sql = """
                UPDATE
                        files_versions
                SET
                        thumb = 'generating'
                WHERE
                        id = %(id)s
        """
        args = {
            'id': self.id
        }
        db.update(sql, args)

        try:
            im = self._image
            output = Config.assetFolder % (self.group_id, self.code) + Config.thumbs % str(self.id)
            im.thumbnail(self.size)
            im = im.rotate(int(self.rotate))

            if (im.mode != 'RGB'):
                im = im.convert('RGB')

            im.save(output)
            sql = """
                    UPDATE
                            files_versions
                    SET
                            thumb = 'done'
                    WHERE
                            id = %(id)s
            """
        except Exception, e:
            _debugger.error("[%s] [%s] [%s] - GEN THUMB ERROR: %s", self.group_id, self.id, self.code, e)
            sql = """
                    UPDATE
                            files_versions
                    SET
                            thumb = 'error'
                    WHERE
                            id = %(id)s
            """

        args = {
            'id': self.id
        }
        db.update(sql, args)

        return

    def fileExist(self):
        """ Valida la existencia del OUTPUT. """
        if self.errors == None:
            if not os.path.exists(self.output):
                self.errorHandler('output')

        return

    def encodingComplete(self):
        """ Actualiza el status del FileVersion a encoded y ademas manda una notificacion de que se encodeo. """
        _debugger.info("[%s] [%s] [%s] - Encoding Complete", self.group_id, self.id, self.code)

        try:
            size = os.stat(self.output)[6]
        except:
            size = 0

        im = Image.open(self.output)
        W, H = im.size
        sql = """
                UPDATE
                        files_versions
                SET
                        status = 'available',
                        progress = 100,
                        size = %(size)s,
                        width = %(W)s,
                        height = %(H)s,
                        encode_end = NOW()
                WHERE
                        id = %(id)s
        """
        args = {
            'id': self.id,
            'W': W,
            'H': H,
            'size': size
        }
        db.update(sql, args)
        self.updateDeliveryFiles()
        notification = Notification(self.owner, self.asset_id)
        notification.createNotification(Config.ENCODED_FILEVERSION)
        return

    def updateDeliveryFiles(self):
        sql = """
                SELECT
                        df.id as dfid,
                        dest.id as destid,
                        dest.type
                FROM
                        delivery_files df
                LEFT JOIN
                        delivery_transfers dlt ON dlt.id = df.delivery_transfer
                LEFT JOIN
                        destinies dest ON dest.id = dlt.destiny_id
                WHERE
                        df.file_version = %(id)s
                """
        args = {'id': self.id}
        query = db.select(sql, args, fetch='all')
        if query:
            sql = """
                    UPDATE
                            delivery_files
                    SET
                            status = %(stat)s
                    WHERE
                            id = %(id)s
            """
            for q in query:
                args2 = {
                    'stat': 'queued',
                    'id': q['dfid']
                }
                if q['type'] == 'web':
                    args2['stat'] = 'ready'
                db.update(sql, args2)
                try:
                    os.system(Config.execDestiny % q['destid'])
                except:
                    pass

    def sendMail(self, who, id, event, description=None):
        """
        Enviamos mails a quien corresponda
        """
        import commands

        commandOutput = commands.getoutput(Config.phpBin + Config.mailGenerator % (who, id, event, description))
        _debugger.info(commandOutput)
        return