#!/usr/bin/python -u
# -*- coding: utf-8 -*-
# Name:     image.py
# Purpose:  Encodea las imagenes.
#
# Author:   Pela
#
# Created:  07/03/2014
# Notas:
import sys
import logging
from _classes.Config import LOG_FOLDER
from _classes.Tools import send_to_cdn, update_delivery_files
from _classes.InstanceLock import Ilock
from _classes.EImage import EImage


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


def main(group_id):
    while True:
        eimage = EImage(group_id)
        if eimage.found:
            if not eimage.format.found:
                logger.error("No se encontro el formato requerido ({})".format(eimage.version.format_id))
                return

            if not eimage.parse_command():
                logger.error("No se pudo parsear el comando del formato ({})".format(eimage.version.format_id))
                return

            if not eimage.source_file.found:
                logger.error("La version source del File no fue encontrado en la base de datos ({})".format(
                    eimage.version.id))
                return

            eimage.encode()

            if eimage.error is None:
                send_to_cdn(eimage.version.id)
                update_delivery_files(eimage.version.id)
        else:
            logger.info("No hay nada para encodear.")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('No se pasaron la cantidad correcta de argumentos.')
        sys.exit()

    set_logger()
    lock = None
    try:
        lock = Ilock("/tmp/ilock_image_{}.lock".format(sys.argv[1])).acquire()
    except Exception as e:
        logger.error(e)

    if lock:
        logger.info("### Ejecuto el encoder de Imagenes ({})".format(sys.argv[1]))
        main(*sys.argv[1:])
    else:
        logger.info("### Ya hay un encoder de Imagenes ({})".format(sys.argv[1]))

    sys.exit(0)