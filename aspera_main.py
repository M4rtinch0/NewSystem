#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Name:         DestinyMain
# Purpose:      Main de la app
#
# Author:       Pela
#
# Created:      11/03/2013
# Copyright:    (c) Pela 2013
import sys
import signal
import logging
from _classes.AspDestiny import Destiny
from _classes.InstanceLock import Ilock
from _classes.AspDeliveryFile import AspDeliveryFile

LOG_FOLDER = "/oxobox/logs/aspera/"
PID_FILE = "/tmp/ctrl_aspera_%s"


def set_logger():
    """
    Setea el sistema de logueo de la aplicación
    """
    global logger
    logger = logging.getLogger('Log')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOG_FOLDER + 'Aspera.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(lineno)04d] %(asctime)s - [%(levelname)s] - %(name)s -|- %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def signal_term_handler(sig, frame):
    logger.critical("CANCELADO {} - {}".format(sig, frame))
    try:
        if destiny.pipe.poll() is None:
            destiny.pipe.terminate()
    except Exception as responce:
        logger.error("{}".format(responce))
    finally:
        sys.exit(0)


def main(dest_id):
    """
    Functión principal.
    :param dest_id: Id del destino
    """
    global destiny
    destiny = Destiny(dest_id)
    if not destiny.found:
        logger.critical("No existe el destino {}".format(destiny.id))
        return
    while True:
        if destiny.has_files():
            try:
                destiny.send_file()
            except KeyboardInterrupt:
                if destiny.pipe.poll() is None:
                    destiny.pipe.terminate()
                    destiny.file.update_status(AspDeliveryFile.STATUS_CANCELED)
                    logger.critical("CANCELADO")
        else:
            break

if __name__ == '__main__':
    set_logger()

    if len(sys.argv) != 2:
        print('No se pasaron la cantidad correcta de argumentos.')
        sys.exit()

    lock = None
    try:
        lock = Ilock(PID_FILE % sys.argv[1]).acquire()
    except Exception as e:
        logger.error(e)        
    
    if lock:
        logger.info("### Ejecuto el Aspera (%s)" % (sys.argv[1]))
        signal.signal(signal.SIGTERM, signal_term_handler)
        main(*sys.argv[1:])
    else:
        logger.info("### Ya hay un Aspera ejecutado (%s)" % (sys.argv[1]))
    sys.exit(0)