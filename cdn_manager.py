#!/usr/bin/python
# -*- coding: utf-8 -*-
# Name:     cdn_manager.py
# Purpose:  Envia los archivos al CDN
#
# Author:   Pela
#
# Created:  07/03/2014
# Notas:
import sys
import logging
from _classes.Config import LOG_FOLDER
from _classes.BotoS3 import BotoS3
from _classes.InstanceLock import Ilock


def set_logger():
    """
    Setea el sistema de logueo de la aplicación
    """
    global logger
    logger = logging.getLogger('Debug')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOG_FOLDER + 'Debug.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(lineno)04d] %(asctime)s - [%(levelname)s] - %(name)s -|- %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def main(file_version):
    """
    Enviamos el file version especificado al bucket de Amazon S3 que tenga configurado el grupo

    :type file_version: int
    :param file_version:
    """
    logger.info('>>> Starting - [{}]'.format(file_version))
    boto = BotoS3(file_version)

    if boto.found:
        logger.info('>>> Starting - [{}]'.format(boto.fv_id))
        boto.send()
        if boto.error is not None:
            logger.info('>>> Hubo un error - [{}]'.format(boto.fv_id))
        logger.info('>>> Ending - [{}]'.format(boto.fv_id))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('No se pasaron la cantidad correcta de argumentos.')
        sys.exit(0)

    set_logger()
    lock = None
    try:
        lock = Ilock("/tmp/ilock_cdn_{}.lock".format(sys.argv[1])).acquire()
    except Exception as e:
        logger.error(e)

    if lock:
        logger.info("### Ejecuto el CDN manager ({})".format(sys.argv[1]))
        main(*sys.argv[1:])
    else:
        logger.info("### Ya hay un CDN manager ({})".format(sys.argv[1]))

    sys.exit(0)