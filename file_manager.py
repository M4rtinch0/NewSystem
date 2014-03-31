#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Name:     file_manager.py
# Purpose:  Manejar el archivo que ingresa por ftp.
#
# Author:   Pela
#
# Created:  07/03/2014
# Notas:    Group manager es ejecutado por p_exec.sh cuando una tranferencia bia FTP se completa.
#           Luego crea (guarda en la base de datos) el asset, con su archivo y versiónes del mismo.
#           Crea la carpeta contenedora del asset y ejecuta el System que corresponde según el archivo subido.
import sys
import time
import shlex
import shutil
import logging
from subprocess import Popen
from _classes.Config import (LOG_FOLDER, TBL_ASSETS, TBL_FILES, video_encoder, image_encoder,
                             audio_encoder, document_encoder)
from _classes.Tools import is_file, is_inbox, get_inbox_name, get_file_name
from _classes.Asset import Asset
from _classes.User import User
from _classes.Inbox import Inbox
from _classes.File import File
from _classes.DataBase import db


def set_logger():
    """
    Setea el sistema de logueo de la aplicación
    defile una variable global 'logger'
    """
    global logger
    logger = logging.getLogger('Debug')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOG_FOLDER + 'Debug.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(lineno)04d] %(asctime)s - [%(levelname)s] - %(name)s -|- %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def dump():
    """
    Maneja los archivos que no van a ser encodeados, o se subieron a una estructura de carpeta erronea y los
    mueve a la raiz del FTP.
    """
    try:
        logger.info("mv {} {}".format(user.ftp_upload_dir, user.homedir))
        shutil.move(user.ftp_upload_dir, user.homedir)
    except Exception as responce:
        logger.error("DUMP ERROR: {}".format(responce))


def encode():
    """
    Comienza el encodeo del archivo.
    """
    command = None
    if c_file.type == 'video':
        command = video_encoder
    if c_file.type == 'audio':
        command = audio_encoder
    if c_file.type == 'image':
        command = image_encoder
    if c_file.type == 'document':
        command = document_encoder

    if command is not None:
        Popen(shlex.split(command.format(user.group)))


def create_asset():
    """
    Crea el asset a partir del usuario que subió el archivo.
    """
    global c_asset
    c_asset = Asset()
    c_asset.title = get_file_name(user.ftp_upload_dir)
    c_asset.code = db.gen_code(TBL_ASSETS)
    c_asset.owner = user.id
    c_asset.inbox_id = c_inbox.id
    c_asset.privacy = c_inbox.def_asset_privacy
    c_asset.comments = c_inbox.def_asset_comments
    c_asset.externalembed = c_inbox.def_asset_external_embed
    c_asset.status = None
    c_asset.player_template = c_inbox.def_player_template
    c_asset.advertising = c_inbox.def_advertising
    c_asset.rating = c_inbox.def_rating
    c_asset.interstice = c_inbox.def_interstice
    c_asset.cat_ids = c_inbox.get_categories()
    c_asset.updated = time.strftime('%Y-%m-%d %H:%M:%S')
    c_asset.save()


def create_file():
    """
    Crea el file a partir del usuario que subió el archivo.
    """
    global c_file
    c_file = File()
    c_file.set_upload_path(user.ftp_upload_dir)
    c_file.code = db.gen_code(TBL_FILES)
    c_file.asset_id = c_asset.id
    c_file.owner = user.id
    c_file.save()


def main(user_name, path):
    """
    Este el main Doh...

    :type user_name: str
    :param user_name: Nombre de usuario que subió el archivo, este viene del log FIFO del proftpd y el bash script
        que se encarga de ejecutar este file_manager.py

    :type path: str
    :param path: Path de donde se subió el archivo, se va a chequear que sea un inbox.

    :rtype: bool
    :return: Devuelve un bool, si esta todo OK es True, sino False, así luego el programa se encarga del archivo
        subido con dump()
    """
    global user, c_inbox, c_asset, c_file
    # Creamos user que es del Class User pasándole los parámetros, chequea si es desde un inbox que se subió.

    if not is_file(path):
        logger.info("No es un archivo {}".format(path))
        return True

    user = User(user_name, path)
    # Si se subió desde un inbox entramos.
    if user.found:
        if not is_inbox(user.ftp_upload_dir):
            logger.error("No es un inbox")
            return True

        inbox_name = get_inbox_name(user.ftp_upload_dir)
        c_inbox = Inbox(inbox_name, user.group)
        if not c_inbox.found:
            logger.error("No existe el inbox ({})".format(inbox_name))
            return False

        if not user.check_inbox(c_inbox.id):
            logger.error("El usuario '{}' no es uploader del inbox '{}'".format(user.id, c_inbox.id))
            return False

        if not user.check_asset_space():
            logger.error("No puede generar el asset, el grupo ({}) del usuario ({}) no tiene espacio".format(
                user.group, user.id))
            return False

        # Agregar lo del ingestor masivo

        create_asset()

        if c_asset.found:
            c_asset.set_defaults(c_inbox.id)

            create_file()
            if c_file.found:
                source_version = c_file.create_source_versions(c_inbox.id)
                logger.debug("TODO OK")
                return True
                if source_version.found:
                    for c_format in c_inbox.get_formats(c_file.type):
                        c_format.create_version(c_file.id, user.id)
                    if source_version.move():
                        encode()
                    else:
                        logger.info("No se pudo crear el file version del source")
                        return False
                else:
                    logger.info("No se pudo crear el file version del source")
                    return False
            else:
                logger.info("No se pudo crear el asset con el archivo {}".format(path))
                return False
        else:
            logger.info("No se pudo crear el asset con el archivo {}".format(path))
            return False
    else:
        logger.info("El usuario {} no existe".format(user_name))
        return False

    return True


if __name__ == '__main__':
    # Ejecutamos el filemanager pasandole 2 argumentos, el usuario que subio por FTP y el path en donde se subio.
    # Ejemplo: ./filemanager martin /ftp/oxobox/1/1/inbox
    set_logger()
    if len(sys.argv) != 3:
        logger.info("Cantidad incorrecta de argumentos: ./file_manager martin /ftp/oxobox/1/1/inbox")
        sys.exit()

    if not main(*sys.argv[1:]):
        # Nos encargamos del archivo enviado.
        dump()
    else:
        sys.exit(0)
