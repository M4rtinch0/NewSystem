#!/usr/bin/python
# -*- coding: utf-8 -*-
# Name:         DestinyMain
# Purpose:      Main de la app
#
# Author:       Pela
#
# Created:      11/03/2013
# Copyright:    (c) Pela 2013
import sys
import time
import logging
from _classes.OFtp import OFtp
from _classes.Destiny import Destiny
from _classes.InstanceLock import Ilock

LOG_FOLDER = "/oxobox/logs/destinies/"
PID_FILE = "/tmp/ctrl_destiny_%s"


def set_logger(dest_id):
    """
    Setea el sistema de logueo de la aplicación
    :param dest_id: Id del destino.
    :type dest_id: int
    """
    global logger
    logger = logging.getLogger('NewDeliveries')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOG_FOLDER + 'Dest-%s.log' % dest_id)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(lineno)04d] %(asctime)s - [%(levelname)s] - %(name)s -|- %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def main(dest_id):
    """
    Functión principal.
    :param dest_id: Id del destino
    :type dest_id: int
    """
    destiny = Destiny(dest_id)
    if not destiny.found:
        # Si el destino no existe o no tiene files salimos.
        logger.critical('No hay mas files o el destino no existe.')
        sys.exit()

    # Según el destino y los uploads simultaneos que se pueden hacer
    logger.info('Creando %d conecciones FTP para upload simultaneo' % destiny.ftp_simult_uploads)
    # Este tipo de sentencia se llama generators, lo que hacemos es crear una lista con
    # dicts de 2 dimensiones que tienen el objeto OFtp y su estado, que para comenzar esta en alive.
    ftps = [{'oftp': OFtp(destiny.id, i), 'alive': True} for i in range(destiny.ftp_simult_uploads)]
    ftps_len = len(ftps)

    for f in ftps:
        # Starteamos las conexiones ftp
        f['oftp'].start()
        time.sleep(2)
    
    # Esperamos a que todos los files hayan sido enviados
    deads = 0
    while deads < ftps_len:
        # Si hay algún objeto OFtp vivo seguimos mandando.
        for i in range(ftps_len):
            # Recorremos todos los objetos OFtp
            # El join es porque OFtp extiende a multiproccess, hacemos esto con un timeout de 1 segundo
            # para saber si estan vivos los procesos.
            ftps[i]['oftp'].join(1)
            if not ftps[i]['oftp'].is_alive() and ftps[i]['alive']:
                logger.debug("%d Proceso muerto" % i)
                deads += 1
                ftps[i]['alive'] = False
            # Chequeo si hay algun otro archivo para subir. Y si no esta vivo el OFtp tengo que dispararlo de
            # nuevo para poder mandarlo.
            if destiny.other_files() and not ftps[i]['alive']:
                logger.debug("%d Revivo uno, hay mas para mandar" % i)
                deads -= 1
                ftps[i] = {'oftp': OFtp(destiny.id, i), 'alive': True}
                ftps[i]['oftp'].start()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('No se pasaron la cantidad correcta de argumentos.')
        sys.exit()

    set_logger(sys.argv[1])
    lock = None
    try:
        lock = Ilock(PID_FILE % sys.argv[1]).acquire()
    except Exception as e:
        logger.error(e)        
    
    if lock:
        logger.info("### Ejecuto el Destiny (%s)" % (sys.argv[1]))
        main(*sys.argv[1:])
    
    logger.info("### Ya hay un Destiny ejecutado (%s)" % (sys.argv[1]))
    sys.exit(0)