# -*- coding: utf-8 -*-
# Name:         Destiny
# Purpose:      Objeto Destiny para utilizar con los destinos
#
# Author:       Pela
#
# Created:      11/03/2013
# Copyright:    (c) Pela 2013
import logging
from .DataBase import db


class Destiny(object):

    destiny_logger = logging.getLogger('NewDeliveries.Destiny')
    STATUS_UP = 'up'
    STATUS_DOWN = 'down'
    STATUS_LOGIN_ERROR = 'login_error'
    STATUS_WARNING = 'warning'

    def __init__(self, dest_id):
        self.id = dest_id
        self.found = False
        sql = ("SELECT d.ftp_port, d.ftp_host, d.ftp_user, d.ftp_pass, d.ftp_speed_limit, "
               "d.ftp_simult_uploads, d.data_type "
               "FROM destinies d "
               "LEFT JOIN delivery_transfers dt ON dt.destiny_id = d.id "
               "LEFT JOIN delivery_files df ON df.delivery_transfer = dt.id "
               "WHERE df.status IN ('queued', 'warning') AND d.type = 'ftp' AND dt.status != 'waiting' "
               "AND d.id = %(id)s")
        args = {'id': self.id}
        query = db.select(sql, args)
        if query is not None:
            self.found = True
            self.data_type = query['data_type']
            self.ftp_host = query['ftp_host']
            self.ftp_user = query['ftp_user']
            self.ftp_pass = query['ftp_pass']
            self.ftp_port = query['ftp_port']
            self.ftp_speed_limit = query['ftp_speed_limit']
            self.ftp_simult_uploads = query['ftp_simult_uploads']

    def update_status(self, status, description=''):
        sql = ("UPDATE destinies SET ftp_status = %(status)s, ftp_status_description = %(desc)s "
               "WHERE id = %(id)s")
        args = {'status': status, 'desc': description, 'id': self.id}
        db.update(sql, args)

    def other_files(self):
        select_q = ("SELECT df.id FROM destinies d "
                    "LEFT JOIN delivery_transfers dt ON dt.destiny_id = d.id "
                    "LEFT JOIN delivery_files df ON df.delivery_transfer = dt.id "
                    "LEFT JOIN files_versions fv ON fv.id = df.file_version "
                    "LEFT JOIN files f ON f.id = fv.file_id "
                    "LEFT JOIN assets a ON a.id = f.asset_id "
                    "LEFT JOIN deliveries de ON de.id = dt.delivery_id "
                    "LEFT JOIN users u ON u.id = a.owner "
                    "WHERE df.status = 'sending' AND d.id = %(id)s")
        sql = select_q.format('sending', self.id)
        query = db.select(sql)
        if query is not None:
            return True
        return False

    def __str__(self):
        string = ("\nData Type: {}\nFtp Host: {}\nFtp User: {}\nFtp Pass: {}\nFtp Port: {}\nFtp Speed Limit: {}"
                  "\nFtp Simult Uploads: {}")
        return string.format(self.data_type, self.ftp_host, self.ftp_user, self.ftp_pass, self.ftp_port,
                             self.ftp_speed_limit, self.ftp_simult_uploads)