# -*- coding: utf-8 -*-
# Name:         Destiny
# Purpose:      Objeto Destiny para utilizar con los destinos
#
# Author:       Pela
#
# Created:      11/03/2013
# Copyright:    (c) Pela 2013
import os
import re
import logging
from .AspDeliveryFile import AspDeliveryFile
from .DataBase import db
from subprocess import Popen, PIPE
from shlex import split
from time import sleep
from glob import iglob


class Destiny(object):

    ASPERA_LOG_PATH = "/oxobox/logs/aspera/{}/"
    ASPERA_LOG = "aspera-scp-transfer.log"
    ASPERA = "/opt/aspera/connect/bin/ascp"

    destiny_logger = logging.getLogger('Log.Destiny')
    STATUS_UP = 'up'
    STATUS_DOWN = 'down'
    STATUS_LOGIN_ERROR = 'login_error'
    STATUS_WARNING = 'warning'

    ASPERA_CMD = ("{} -v -QT -DD -k 2 -l 5M -m 5M -L {} "
                  "--file-manifest=text --file-manifest-path={} {} -P {} "
                  "{}@{}:/{}")

    MANIFEST = "aspera-transfer-"
    EXTENSION = ".txt"

    found = False
    pipe = None
    file = None
    aspera_log = None
    uploaded = 0
    started = False

    host = ""
    user = ""
    passwd = ""
    port = 22
    speed_limit = 0

    rstart = re.compile("size=(\d+)\S*\s*start_byte=(\d+)")
    rprog = re.compile("xfer id 1 progress\S*\s*(\d+)$")

    # --Total file transfer failed:           0
    fail_re = re.compile("--Total file transfer failed:\S*\s*(\d+)$")
    # --Total file transfer passed:           1
    complete_re = re.compile("--Total file transfer passed:\S*\s*(\d+)$")
    success_re = re.compile("Transfer success")

    def __init__(self, dest_id):
        self.id = dest_id
        sql = ("SELECT d.id, d.ftp_port, d.ftp_host, d.ftp_user, d.ftp_pass, d.ftp_speed_limit "
               "FROM destinies d "
               "LEFT JOIN delivery_transfers dt ON dt.destiny_id = d.id "
               "LEFT JOIN delivery_files df ON df.delivery_transfer = dt.id "
               "WHERE df.status IN ('queued', 'warning') AND d.type = 'aspera' AND d.id = %(id)s")
        args = {'id': self.id}
        query = db.select(sql, args)
        if query is not None:
            self.found = True
            self.host = query['ftp_host']
            self.user = query['ftp_user']
            self.passwd = query['ftp_pass']
            self.port = query['ftp_port']
            self.speed_limit = query['ftp_speed_limit']
            self.log_path = Destiny.ASPERA_LOG_PATH.format(query['id'])
            self.log_file = "{}{}".format(self.log_path, Destiny.ASPERA_LOG)
            if not os.path.exists(self.log_path):
                try:
                    os.makedirs(self.log_path)
                except Exception as reponce:
                    self.destiny_logger.error(reponce)
                    self.found = False
            self.clear_manifests()

    def clear_manifests(self):
        for file in iglob("{}{}*".format(self.log_path, Destiny.MANIFEST)):
            try:
                os.remove(file)
            except Exception as reponce:
                self.destiny_logger.error(reponce)

    def has_files(self):
        sql = ("SELECT df.id FROM destinies d "
               "LEFT JOIN delivery_transfers dt ON dt.destiny_id = d.id "
               "LEFT JOIN delivery_files df ON df.delivery_transfer = dt.id "
               "WHERE df.status IN ('queued', 'warning') AND d.id = %(id)s")
        args = {'id': self.id}
        query = db.select(sql, args)
        if query is not None:
            return True
        return False

    def update_status(self, status, description=''):
        sql = ("UPDATE destinies SET ftp_status = %(status)s, ftp_status_description = %(desc)s "
               "WHERE id = %(id)s")
        args = {'status': status, 'desc': description, 'id': self.id}
        db.update(sql, args)

    def progress(self):
        try:
            if not self.reload_file_if_changed():
                return False
            line = self.aspera_log.readline()
            m = Destiny.rprog.search(line)
            if m:
                if not self.file.update_progress(int(m.group(1))):
                    return False

        except Exception as responce:
            self.destiny_logger.error("Error {}".format(responce))
            return False
        return True

    def load_file(self):
        try:
            for x in range(30):
                if os.path.isfile(self.log_file):
                    break
                sleep(0.1)
            self.aspera_log = open(self.log_file, 'r')
            self.aspera_log.seek(0, os.SEEK_END)
        except Exception as reponce:
            self.destiny_logger("No se pudo abrir el log file {}".format(reponce))
            return False
        return True

    def reload_file(self):
        self.aspera_log.close()
        return self.load_file()

    def reload_file_if_changed(self):
        # Get the Inode for our current file
        loaded_file_inode = os.fstat(self.aspera_log.fileno()).st_ino

        # Check the inode of the file path that was specified
        current_file = open(self.log_file)
        current_file_inode = os.fstat(current_file.fileno()).st_ino
        current_file.close()

        # Reload if there is a discrepancy
        if loaded_file_inode != current_file_inode:
            self.destiny_logger.debug('Log File Changed, Reloading...')
            if not self.reload_file():
                return False
            self.destiny_logger.debug('Log File Reloaded...')
        return True

    def send_file(self):
        self.file = AspDeliveryFile(self.id)
        if not self.file.found:
            self.destiny_logger.info('No hay archivos para enviar (Dest: {})'.format(self.id))
            return

        cmd = Destiny.ASPERA_CMD.format(Destiny.ASPERA, self.log_path, self.log_path, self.file.path, self.port,
                                        self.user, self.host, self.file.remote_file_name)
        self.destiny_logger.info(cmd)
        self.uploaded = 0
        self.started = False
        self.file.update_status(AspDeliveryFile.STATUS_SENDING)
        self.pipe = Popen(
            split(cmd),
            stdout=PIPE,
            stderr=PIPE
        )

        if not self.load_file():
            self.pipe.terminate()
            self.file.update_status(AspDeliveryFile.STATUS_ERROR)
            return

        while self.pipe.poll() is None:
            if not self.progress():
                self.pipe.terminate()
                break

        if self.complete():
            self.file.update_status(AspDeliveryFile.STATUS_SENT)
        else:
            self.file.update_status(AspDeliveryFile.STATUS_ERROR)

    def complete(self):
        match_complete = None
        match_success = None
        for file in iglob('{}/aspera-transfer-*'.format(self.log_path)):
            extension = os.path.splitext(os.path.basename(file))[1]
            if extension == Destiny.EXTENSION:
                try:
                    with open(file, 'r') as manifest:
                        for line in manifest:
                            if match_complete is None:
                                match_complete = Destiny.complete_re.search(line)
                            if match_success is None:
                                match_success = Destiny.success_re.search(line)
                except Exception as responce:
                    self.destiny_logger.error(responce)

        if match_complete is not None and match_success is not None:
            if int(match_complete.group(1)) > 0:
                return True
        return False

    def __str__(self):
        string = "\nHost: {}\nUser: {}\nPass: {}\nPort: {}\nSpeed Limit: {}"
        return string.format(self.host, self.user, self.passwd, self.port, self.speed_limit)