# -*- coding: utf-8 -*-
# Name:         OFtp
# Purpose:      Wrapper del chilkat con funcionalidades agregadas
#
# Author:       Pela
#
# Created:      11/03/2013
# Copyright:    (c) Pela 2013
import time
import logging
from .Destiny import Destiny
from .DeliveryFile import DeliveryFile
import multiprocessing
from chilkat import CkFtp2


class OFtp(multiprocessing.Process):
    
    oftp_logger = logging.getLogger('Log.OFTP')
    RECONNECT_SLEEP = 20
    FILE_SLEEP = 5
    FTP_SLEEP_MS = 1000
    ABORT_SLEEP_MS = 5000
    UNLOCK_CHILKAT_ERROR = 0
    CONNECTION_ERROR = 1
    CHANGE_REMOTE_DIR_ERROR = 2
    MKDIR_ERROR = 3
    UPLOAD_ERROR = 4
    RESUME_ERROR = 5
    UPLOADED = 0
    APPEND = 1
    PUT = 2
    
    def __init__(self, dest_id, cid):
        multiprocessing.Process.__init__(self)
        self.delivery_file = None
        self.id = cid
        self.dest_id = dest_id
        self.destiny = Destiny(self.dest_id)

    def run(self):
        """
        Override del método del class Process
        """
        self.__connect()
        while True:
            self.delivery_file = DeliveryFile(self.dest_id)
            if not self.delivery_file.found:
                if self.destiny.other_files():
                    self.oftp_logger.error('{}: Ya termine, espero a que otros terminen por si aparece algo.'.format(
                        self.name))
                    time.sleep(self.FILE_SLEEP)
                    continue
                break
            else:
                self.__upload()
                time.sleep(self.FILE_SLEEP)
        self.__disconnect()
        return 
    
    def __unlock(self):
        self.ftp = CkFtp2()
        success = self.ftp.UnlockComponent("OXOCOMFTP_CZ0AaKpp9RzG")
        if not success:
            self.__report_error(self.UNLOCK_CHILKAT_ERROR, str(self.ftp.lastErrorText()))
        return success
            
    def __connect(self):
        """
        Connect and login to the FTP server.
        """
        while True:
            if not self.__unlock():
                break

            self.delivery_file = DeliveryFile(self.dest_id)
            if not self.delivery_file.found:
                # Si no hay más archivos para subir entonces retornamos y entre en el otro que es el que va a terminar
                # el proceso
                break

            # Creamos nuevamente el objeto Destiny por si cambio algo en la base de datos.
            self.destiny = Destiny(self.dest_id)        
            self.ftp.put_Hostname(str(self.destiny.ftp_host))
            self.ftp.put_Username(str(self.destiny.ftp_user))
            self.ftp.put_Password(str(self.destiny.ftp_pass))
            self.ftp.put_Port(self.destiny.ftp_port)
            self.ftp.put_BandwidthThrottleUp(self.delivery_file.new_speed_limit)
            success = self.ftp.Connect()
            
            if not success:
                self.oftp_logger.info('{}: Esperamos 20 segs e intentamos reconectar.'.format(self.name))
                self.__report_error(self.CONNECTION_ERROR, str(self.ftp.get_ConnectFailReason()))
                time.sleep(self.RECONNECT_SLEEP)
                continue
            self.destiny.update_status(self.destiny.STATUS_UP)
            break
        return
    
    def __is_connected(self):
        """
        Seguimos conectados?
        :rtype: bool
        """
        responce = self.ftp.get_IsConnected() 
        if not responce:
            self.oftp_logger.info('{}: No estamos conectados al servidor.'.format(self.name))
        return responce 
    
    def __disconnect(self):
        """
        Disconnect FTP. No hay más archivos para subir, salimos...
        """
        self.oftp_logger.info('{}: Desconecto.'.format(self.name))
        self.ftp.Disconnect()
        
    def __get_delivery_file(self):
        """
        Devuelve un objeto file
        """
        self.delivery_file = DeliveryFile(self.dest_id)
        # Si no se pudo actualizar la base de datos, por lo que fuere => PILDORA VENENOOOOSA.
        if self.delivery_file.found:
            response = self.delivery_file.update_status(self.delivery_file.STATUS_SENDING) 
            if not response:
                self.delivery_file.found = False
    
    def __change_remote_dir(self, current_dir):
        """
        Cambia el remote dir
        :param current_dir: string del path
        :type current_dir: str
        :return: bool indica si pudo o no hacerlo
        :rtype: bool
        """
        if not self.__is_connected():
            return False
        success = self.ftp.ChangeRemoteDir(current_dir)
        if not success:
            self.__report_error(self.CHANGE_REMOTE_DIR_ERROR, str(self.ftp.lastErrorText()))
        return success
    
    def __create_folder(self, current_dir):
        """
        Crea una carpeta en el remote dir
        :param current_dir: string del path
        :type current_dir: str
        :return: bool indica si pudo o no hacerlo
        :rtype: bool
        """
        if not self.__is_connected():
            return False
        success = self.ftp.CreateRemoteDir(current_dir)
        if not success:
            self.__report_error(self.MKDIR_ERROR, str(self.ftp.lastErrorText()))
        else:
            self.oftp_logger.debug("{}: Created folder: {}".format(self.name, current_dir))
        return success
    
    def __go_to_root(self):
        """
        Vamos al root del remote
        :rtype: bool
        """
        self.oftp_logger.debug("{}: Going to ROOT DIR.".format(self.name))
        return self.__change_remote_dir('/')
        
    def __folder_exist(self, current_dir):
        """
        Cheque si existe la carpeta en el host
        """
        if self.__change_remote_dir(current_dir):
            self.oftp_logger.debug('{}: Yes, the {} directory exists'.format(self.name, current_dir))
            if self.__change_remote_dir(".."):
                return True
        return False
    
    def __check_file(self):
        """
        Chequea si el archivo existe.
        :return: True for APPEND
        :rtype: bool
        """
        remote_file_size = self.ftp.GetSizeByName(str(self.delivery_file.remote_file_name))
        if remote_file_size > 0:
            if self.delivery_file.file_size > remote_file_size:
                return self.APPEND
            else:
                return self.UPLOADED
        return self.PUT
    
    def __start_async_transfer(self, transfer_type):
        """
        Inicia propiamente dicho una transferencia asincrónica para la subida de los archivos
        :param transfer_type: int con el codigo PUT OR APPEND
        :type transfer_type: int
        :rtype: int
        """
        if not self.__is_connected():
            return 2
        local_file = str(self.delivery_file.get_local_path())
        remote_file = str(self.delivery_file.remote_file_name)
        remote_file_size = 0
        
        if transfer_type == self.APPEND:
            self.ftp.put_RestartNext(True)
            remote_file_size = self.ftp.GetSizeByName(str(self.delivery_file.remote_file_name))
            success = self.ftp.AsyncAppendFileStart(local_file, remote_file)
        else:
            self.ftp.put_RestartNext(False)
            success = self.ftp.AsyncPutFileStart(local_file, remote_file)
                        
        if not success:
            return 0
        
        cont = 0
        while not self.ftp.get_AsyncFinished():
            self.delivery_file.progress(self.ftp.get_AsyncBytesSent() + remote_file_size,
                                        self.ftp.get_UploadTransferRate())
            status = self.delivery_file.check_status()

            if status != self.delivery_file.STATUS_SENDING:
                self.ftp.AsyncAbort()
                self.ftp.SleepMs(self.ABORT_SLEEP_MS)
                if status == self.delivery_file.STATUS_CANCELED:
                    return 2
                if status == self.delivery_file.STATUS_RESTART:
                    self.oftp_logger.debug("Limit to {} bytes per second".format(self.delivery_file.new_speed_limit))
                    self.delivery_file.update_status(self.delivery_file.STATUS_QUEUED, 'SPEED_CHANGE')
                    self.__disconnect()
                    self.__connect()
                    return 2
            cont += 1
            self.ftp.SleepMs(self.FTP_SLEEP_MS)

        #  Did the upload succeed?
        if self.ftp.get_AsyncSuccess():
            return 1
        else:
            return 0
           
    def __upload(self):
        """
        Se encarga de subir el archivo
        """
        if not self.__is_connected():
            self.__connect()
        
        if self.delivery_file.found:
            self.delivery_file.update_status(self.delivery_file.STATUS_SENDING) 
            self.oftp_logger.info('{}: Queremos subir el siguiente archivo {} a {}/{}'.format(
                self.name,
                self.delivery_file.get_local_path(),
                '/'.join(self.delivery_file.remote_path),
                self.delivery_file.remote_file_name))
            for i in range(len(self.delivery_file.remote_path)):
                current_dir = str(self.delivery_file.remote_path[i])
                if not self.__folder_exist(current_dir):
                    if not self.__create_folder(current_dir):
                        return
                if not self.__change_remote_dir(current_dir):
                    return
            success = 0
            file_status = self.__check_file()
            if file_status == self.UPLOADED:
                success = 1
    
            if success != 1 and file_status == self.APPEND:
                success = self.__start_async_transfer(self.APPEND)
                if success == 0:
                    self.__report_error(self.RESUME_ERROR, str(self.ftp.asyncLog()))
                
            if success == 0:
                success = self.__start_async_transfer(self.PUT)

            # Did the upload succeed?
            if success == 1:
                self.oftp_logger.debug("File Uploaded! Sending MD if needed")
                self.__send_md()
                self.delivery_file.update_status(self.delivery_file.STATUS_SENT)
                self.destiny.update_status(self.destiny.STATUS_UP)
            elif success == 0:
                self.__report_error(self.UPLOAD_ERROR, str(self.ftp.asyncLog()))
                time.sleep(self.RECONNECT_SLEEP)

        self.__go_to_root()
        return
    
    def __send_md(self):
        if self.delivery_file.md_file.found:
            success = self.ftp.AsyncPutFileStart(str(self.delivery_file.md_file.tmp_dir),
                                                 str(self.delivery_file.md_file.remote_dir))
            if not success:
                self.oftp_logger.debug("MD Upload Fail!")
                return

            while not self.ftp.get_AsyncFinished():
                self.ftp.SleepMs(self.FTP_SLEEP_MS)

            #  Did the upload succeed?
            if self.ftp.get_AsyncSuccess():
                self.oftp_logger.debug("MD Uploaded!")
            else:
                self.oftp_logger.debug("MD Upload Fail!")
        return

    def __report_error(self, where, error):
        """
        Reporta errores, el estado del destiny y el de los files
        """
        self.oftp_logger.error('%s: [%s] %s' % (self.name, where, error))
        destiny_status = ""
        destiny_description = ""
        if where == self.UPLOAD_ERROR or (where == self.RESUME_ERROR and not self.__is_connected()):
            destiny_status = self.destiny.STATUS_WARNING
            destiny_description = 'WARNING_CANNOT_UPLOAD'
            delivery_file_status = self.delivery_file.STATUS_WARNING
            delivery_file_description = 'CANNOT_UPLOAD_FILE'
            self.delivery_file.update_status(delivery_file_status, delivery_file_description)

        if where == self.CONNECTION_ERROR:
            destiny_status = self.destiny.STATUS_LOGIN_ERROR
            destiny_description = 'ERROR_LOGIN_FAIL'
            delivery_file_status = self.delivery_file.STATUS_WARNING
            delivery_file_description = 'ERROR_LOGIN_FAIL'
            if error != '301':
                destiny_status = self.destiny.STATUS_DOWN
                destiny_description = 'ERROR_SERVER_DOWN'
                delivery_file_description = 'ERROR_SERVER_DOWN'
            self.delivery_file.update_status(delivery_file_status, delivery_file_description)

        if where == self.MKDIR_ERROR:
            destiny_status = self.delivery_file.STATUS_WARNING
            destiny_description = 'WARNING_MKDIR_ERROR'
            delivery_file_status = self.delivery_file.STATUS_WARNING
            delivery_file_description = 'WARNING_MKDIR_ERROR'
            self.delivery_file.update_status(delivery_file_status, delivery_file_description)

        if where == self.RESUME_ERROR:
            # destiny_status = self.destiny.STATUS_WARNING
            destiny_description = 'WARNING_RESUME_ERROR'
            self.oftp_logger.error('{}: [{}] {}'.format(self.name, where, destiny_description))
            return

        self.destiny.update_status(destiny_status, destiny_description)
        return