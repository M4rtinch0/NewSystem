# -*- coding: utf-8 -*-
# Name:         DeliveryFile
# Purpose:      Objeto File para utilizar con los destinos
#
# Author:       Pela
#
# Created:      11/03/2013
# Copyright:    (c) Pela 2013
import os
import logging
import subprocess
from .MetadataFile import MetadataFile
from .DataBase import db


class DeliveryFile(object):
    
    delivery_file_logger = logging.getLogger('NewDeliveries.DeliveryFile')    
    STATUS_SENDING = 'sending'
    STATUS_SENT = 'sent'
    STATUS_CANCELED = 'canceled'
    STATUS_WAITING_FILES = 'waiting_files'
    STATUS_QUEUED = 'queued'
    STATUS_RESTART = 'restart'
    STATUS_WARNING = 'warning'
    STATUS_ERROR = 'error'
    FILES_PATH = '/oxobox/assets/'

    def __init__(self, dest_id):
        self.found = False
        self.others = False
        self.dest_id = dest_id 
        self.file_id = 0
        self.file_size = 0
        self.file_name = ""
        self.old_speed_limit = 0
        self.new_speed_limit = 0
        self.asset_id = 0
        self.asset_code = ""
        self.group_id = 0
        self.file_version_id = 0
        self.file_version_label = ""
        self.file_version_format_id = 0
        self.file_version_extension = ""
        self.delivery_code = ""
        self.delivery_title = ""
        self.delivery_transfer_id = 0
        self.remote_path = []
        sql = ("SELECT df.id as df_id, df.file_version, df.delivery_transfer, df.speed_limit, df.remote_path, "
               "df.md_file, a.id as asset_id, a.code, u.group, f.name, fv.extension, fv.label, "
               "de.code as delivery_code, de.title as delivery_title, fv.file_id, fv.format_id "
               "FROM destinies d "
               "LEFT JOIN delivery_transfers dt ON dt.destiny_id = d.id "
               "LEFT JOIN delivery_files df ON df.delivery_transfer = dt.id "
               "LEFT JOIN files_versions fv ON fv.id = df.file_version "
               "LEFT JOIN files f ON f.id = fv.file_id "
               "LEFT JOIN assets a ON a.id = f.asset_id "
               "LEFT JOIN deliveries de ON de.id = dt.delivery_id "
               "LEFT JOIN users u ON u.id = a.owner "
               "WHERE df.status IN ('queued', 'warning') AND d.id = %s "
               "ORDER BY df.priority ASC, df.status DESC, df.id ASC")
        query = db.select(sql, self.dest_id)
        if query is not None:
            self.file_id = query['df_id']
            self.file_name = query['name']
            self.old_speed_limit = query['speed_limit']
            self.new_speed_limit = query['speed_limit']
            self.asset_id = query['asset_id']
            self.asset_code = query['code']
            self.group_id = query['group']
            self.file_version_extension = query['extension']
            self.file_version_id = query['file_version']
            self.file_version_label = query['label']
            self.file_version_format_id = query['format_id']
            self.delivery_code = query['delivery_code']
            self.delivery_title = query['delivery_title']
            self.delivery_transfer_id = query['delivery_transfer']
            remote_path = self.__get_remote_path(query['remote_path'])
            self.remote_file_name = remote_path[-1]
            self.remote_path = remote_path[:-1]
            self.md_file = MetadataFile(query['md_file'])
            self.md_file.set_remote_file_name(self.remote_file_name)
            self.found = self.__file_exist()
            
    def __file_exist(self):
        """
        El archivo existe?
        :return: bool
        """
        path = self.get_local_path()
        try:
            self.file_size = os.path.getsize(path)
        except:
            self.file_size = 0
        finally:
            return os.path.isfile(path)
    
    def get_local_path(self):
        """
        Retorna el path LOCAL en donde esta el archivo a enviar
        :return: str
        """
        local_path = "{}{}/{}/{}.{}".format(self.FILES_PATH, self.group_id, self.asset_code, 
                                            self.file_version_id, self.file_version_extension)
        return local_path
    
    def __get_remote_path(self, remote_path):
        """
        Si no tiene remote path generamos uno.
        :param remote_path: string que viene de la base de datos, si no tiene nada creamos uno nosotros
        :type remote_path: str
        :return: string con el path remoto
        :rtype: str
        """
        if not remote_path or remote_path == "" or remote_path is None:
            f_name = "{0}_{1}.{2}".format(self.file_version_label, self.file_name, self.file_version_extension)
            remote_path = "{0}_{1}_{2}_{3}".format(self.__get_date(), self.delivery_code, self.delivery_title, f_name)
        return remote_path.split('/')
        # return remote_path.replace(' ', '_').split('/')
            
    def update_status(self, status, description=''):
        """
        Updatea el estado del delivery files
        :param status: string con el estado
        :type status: str
        :param description: string con una descripción, por si ocurrió un error (default "")
        :type description: str
        """
        if self.check_status() == self.STATUS_CANCELED:
            return 0

        sql = ("UPDATE delivery_files SET status = %(status)s, error_description = %(description)s %(stat)s "
               "WHERE id = %(id)s")
        stat = ""
        if status == self.STATUS_SENT:
            stat = ", progress = 100, finish_time = NOW()"
        elif status == self.STATUS_SENDING:
            stat = ", start_time = NOW()"
        args = {'status': status, 'description': description, 'stat': stat, 'id': self.file_id}
        responce = db.update(sql, args)
        if status == self.STATUS_SENT:
            self.__update_delivery_transfer_status(status)
            
        return responce
    
    def progress(self, bytes_sent, speed):
        """
        Updatea el progreso del delivery files
        :param bytes_sent: long con la cantidad de bytes enviados
        :type bytes_sent: long
        :param speed: long la velocidad en bytes por segundo
        :type speed: long
        """
        progress = 0
        if self.file_size > 0:
            progress = bytes_sent * 100 / self.file_size
        if progress > 100:
            return
        self.delivery_file_logger.debug("File: {}, Progress: {}, Speed: {}".format(self.file_id, progress, speed))
        sql = "UPDATE delivery_files SET progress = %(prog)s WHERE id = %(id)s"
        args = {'prog': progress, 'id': self.file_id}
        db.update(sql, args)
        return        
                    
    def __update_delivery_transfer_status(self, description=""):
        """
        Updatea el estado del delivery según el estado de los delivery files
        :param description: string con una descripción, por si ocurrió un error (default "")
        :type description: str
        """
        sql = ("SELECT df.status "
               "FROM delivery_files df "
               "WHERE df.status IN ('queued', 'sending', 'error', 'restart', 'canceled', 'waiting', 'waiting_file') "
               "AND df.delivery_transfer = %(id)s").format(self.delivery_transfer_id)
        args = {'id': self.delivery_transfer_id}
        query = db.select(sql, args)
        sql = "UPDATE delivery_transfers SET status = %(status)s, error_description = %(err)s WHERE id = %(id)s"
        if query is None:
            args = {'status': self.STATUS_SENT}
            self.__send_email('transfer', self.delivery_transfer_id, 'sent')
        else:
            args = {'status': self.STATUS_WAITING_FILES}
        args.update({'err': description, 'id': self.delivery_transfer_id})
        db.update(sql, args)
             
    def check_status(self):
        """
        Chequea si la subida del archivo se canceló
        :return: bool
        :rtype: bool
        """
        sql = "SELECT status, speed_limit FROM delivery_files WHERE id = %(id)s"
        args = {'id': self.file_id}
        query = db.select(sql, args)
        if query is not None:
            status = query['status']
            self.new_speed_limit = query['speed_limit']
            if status == self.STATUS_CANCELED:
                return self.STATUS_CANCELED
            if self.new_speed_limit != self.old_speed_limit:
                self.old_speed_limit = self.new_speed_limit
                return self.STATUS_RESTART
        return self.STATUS_SENDING

    @staticmethod
    def __get_date():
        import datetime
        date = datetime.datetime.now()
        return "{}_{}_{}".format(date.year, date.month, date.day)
    
    def __send_email(self, curr_object, curr_id, status):
        try:
            retcode = subprocess.call(['php5', '/oxobox/NewSystem/tools/mail/mailgenerator.php', curr_object,
                                       str(curr_id), status])
            if retcode < 0:
                self.delivery_file_logger.info("Mail child was terminated by signal {}".format(retcode))
            else:
                self.delivery_file_logger.info("Mail child returned {}".format(retcode))
        except OSError as e:
            self.delivery_file_logger.info("Mail execution failed: {}".format(e))
    
    def __str__(self):
        string = ("\nDF ID: {}\nName: {}\nOld Speed Limit: {}\nNew Speed Limit: {}\nAsset ID: {}\nAsset Code: {}"
                  "\nGroup ID: {}\nFile Version ID: {}\nFile Version Label: {}\nFile Version Extension: {}"
                  "\nFile Version FormatID: {}\nDelivery Code: {}\nDelivery Title: {}\nDelivery Transfer ID: {}"
                  "\nRemote Path: {}\nRemote File Name: {}")
        return string.format(self.file_id, self.file_name, self.old_speed_limit, self.new_speed_limit, self.asset_id,
                             self.asset_code, self.group_id, self.file_version_id, self.file_version_label,
                             self.file_version_extension, self.file_version_format_id, self.delivery_code,
                             self.delivery_title, self.delivery_transfer_id, self.remote_path, self.remote_file_name)