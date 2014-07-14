# -*- coding: utf-8 -*-
# Name:         MetadataFile
# Purpose:      Objeto MetadataFile para crear el archivo de metadata del 
#               destino
#
# Author:       Pela
#
# Created:      11/03/2013
# Notas:
import os
import json
import logging
import datetime


class MetadataFile(object):

    md_file_logger = logging.getLogger('NewDeliveries.MetadataFile')
    TMP = '/tmp/'

    def __init__(self, md_json):
        self.found = False
        if md_json is not None and md_json != "":
            md_json = self.__adapt(md_json)
            self.data = json.loads(md_json)
            self.ext = self.data['ext']
            self.text = self.data['text']
            self.tmp_dir = self.TMP + self.__get_date_name()
            self.remote_dir = ""
            self.__create_file()

    @staticmethod
    def __adapt(json_data):
        my_json = json_data.replace('\r', '\\r')
        my_json = my_json.replace('\n', '\\n')
        my_json = my_json.replace('\t', '\\t')
        return my_json                

    @staticmethod
    def __get_date_name():
        now = datetime.datetime.now()
        return "%d_%d_%d_%d_%d_%d_%d.tmp" % (now.year, now.month, now.day, now.hour, now.minute, now.second,
                                             now.microsecond)
    
    def __create_file(self):
        try:
            #f = open(self.tmp_dir, 'wb')
            f = open(self.tmp_dir, 'w')
            #f.write(bytes(self.text, 'utf-8'))
            f.write(self.text.encode('utf-8'))
            f.close()
            if os.path.exists(self.tmp_dir):
                self.found = True
                return
        except Exception as e:
            self.md_file_logger.error(e)
        self.found = False
        return
    
    def set_remote_file_name(self, remote_file_name):
        if self.found:
            self.remote_dir = '.'.join((remote_file_name.split('.')[0], self.ext))

    def test(self):
        try:
            f = open(self.tmp_dir, 'r')
            self.md_file_logger.info(f.read())
        except Exception as e:
            self.md_file_logger.info(e)
 
    def __str__(self):
        return "Ext: {}, Text: {}, Dir: {}, RmtDir: {}, Found: {}".format(self.ext, self.text, self.tmp_dir,
                                                                          self.remote_dir, self.found)
    
    def __del__(self):
        if self.found:
            os.unlink(self.tmp_dir)