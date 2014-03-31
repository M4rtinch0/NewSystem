# -*- coding: utf-8 -*-
# Name:     Tools.py
# Purpose:  Obj Inbox
#
# Author:   Pela
#
# Created:  07/03/2014
# Notas:    Recopilacion de funciones de ayuda
import os
import shlex
import logging
from .DataBase import db
from subprocess import check_output, Popen
from .Config import files_types, playable_extensions, mail_generator, boto_cmd, destiny_cmd

logger = logging.getLogger('Debug.Tools')


def get_file_type(ext):
    """
    Determina que tipo de archivo es el SOURCE

    :type ext: str
    :param ext: Extensión del archivo

    :rtype : str
    :return: Retorna el tipo de archivo de que es.
    """
    if ext in files_types['video']:
        return 'video'
    if ext in files_types['audio']:
        return 'audio'
    if ext in files_types['image']:
        return 'image'
    if ext in files_types['document']:
        return 'document'
    else:
        return 'unknown'


def is_file(path):
    """
    Chequea que lo que se subió sea un archivo

    :type path: str
    :param path: El path absoluto del archivo

    :rtype: boot
    :return: True si se encuentra
    """
    return os.path.isfile(path)


def is_inbox(path):
    """
    Devuelve si en el path del archivo subido se encuentra la carpeta inbox, sino no se subió a un inbox.
    /ftp/GROUP_ID/USER_ID/inboxes/INBOX/FILE
    -------------------------^--------------

    :type path: str
    :param path: El path absoluto del archivo

    :rtype: boot
    :return: True si se encuentra
    """
    if "inboxes" in path:
        return True
    return False


def get_inbox_name(path):
    """
    Devuelve el nombre de la carpeta para chequear que sea un inbox
    /ftp/GROUP_ID/USER_ID/inboxes/INBOX/FILE
    --------------------------------^-------

    :type path: str
    :param path: El path absoluto del archivo

    :rtype: str
    :return: Nombre del inbox
    """
    m_dir, file_name, extension = split_path(path)
    return m_dir[-1]


def get_file_name(path):
    """
    Devuelve el nombre del archvo

    :type: str
    :param path: El path absoluto del archivo

    :rtype : str
    :return: Nombre del archivo
    """
    m_dir, file_name, extension = split_path(path)
    return file_name


def get_extension(path):
    """
    Devuelve la extensión del archivo

    :type: str
    :param path: El path absoluto del archivo

    :rtype : str
    :return: Extensión del archivo
    """
    m_dir, file_name, extension = split_path(path)
    return extension


def split_path(path):
    """
    Divide el string con el path en las carpetas, el archivo y la extensión

    :type: str
    :param path: El path absoluto del archivo

    :rtype: list
    :return: Lista con las carpetas, el nombre del archivo y la extension del archivo
    """
    file = os.path.basename(path)
    file_name = os.path.splitext(file)[0]
    extension = os.path.splitext(file)[1]
    extension = extension.lstrip('.')
    extension = extension.lower()
    m_dir = os.path.split(path)[0].split('/')
    return m_dir, file_name, extension


def file_exist(path):
    """
    El archivo existe?

    :type path: str
    :param path: El path absoluto del archivo

    :rtype : bool
    :return: True si existe
    """
    return os.path.isfile(path)


def is_playable(extension):
    """
    Devuelve si la extension se puede reproducir en el player

    :type extension: str
    :param extension: Extesión para chequear

    :rtype: str
    :return: 'yes' si se puede reproducir, sino 'no'
    """
    if extension in playable_extensions:
        return 'yes'
    return 'no'


def send_mail(who, cid, event, description=None):
    """
    Enviamos mails a quien corresponda

    :type who:
    :param who:

    :type cid:
    :param cid:

    :type event:
    :param event:

    :type description:
    :param description: (default=None)
    """
    command_output = check_output(mail_generator.format(who, cid, event, description))
    logger.info(command_output)


def send_to_cdn(fv_id):
    """
    Envía el file version al bucket de Amazon S3 que tenga configurado

    :type fv_id: int|str
    :param fv_id: Id del file version
    """
    try:
        Popen(shlex.split(boto_cmd.format(fv_id)))
    except Exception as responce:
        logger.info(responce)


def update_delivery_files(fv_id):
    """
    Actualiza el status del delivery file asociado al file version

    :type fv_id: int|str
    :param fv_id: Id del file version
    """
    sql = ("SELECT df.id as dfid, dest.id as destid, dest.type "
           "FROM delivery_files df "
           "LEFT JOIN delivery_transfers dlt ON dlt.id = df.delivery_transfer "
           "LEFT JOIN destinies dest ON dest.id = dlt.destiny_id "
           "WHERE df.file_version = {}")
    query = db.select(sql.format(fv_id), fetch='all')
    if query:
        sql = "UPDATE delivery_files SET status = {!r} WHERE id = {}"
        for q in query:
            if q['type'] == 'web':
                stat = 'ready'
            else:
                stat = 'queued'
            db.update(sql.format(stat, q['dfid']))
            try:
                Popen(shlex.split(destiny_cmd.fomat(q['destid'])))
            except Exception as responce:
                logger.info(responce)