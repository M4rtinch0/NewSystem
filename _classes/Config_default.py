# -*- coding: utf-8 -*-
# Name:         Config
# Purpose:      Los datos variables.
#
# Author:       Pela
#
# Created:      11/03/2013
# Notas:        Usamos esto en todos los scripts

# DEFINES

TBL_FILES = 'files'
TBL_ASSETS = 'assets'

# FILES TYPES
VIDEO = 'video'
AUDIO = 'audio'
IMAGE = 'image'
DOCUMENT = 'document'

# DEBUG TYPE
ERROR = 'error'
WARNING = 'warning'
INFO = 'info'
DEBUG = 'debug'
CRITICAL = 'critical'

# FOLDERS
LOG_FOLDER = "/oxobox/logs/new_sysyem/"
ASSET_FOLDER = "/oxobox/assets/"

# MYSQL
MYSQL_USER = ""
MYSQL_PASSWORD = ""
MYSQL_DBNAME = ""

video_encoder = "/oxobox/engine/video.py {}"
audio_encoder = "/oxobox/engine/audio.py {}"
image_encoder = "/oxobox/engine/image.py {}"
document_encoder = "/oxobox/engine/document.py {}"
boto_cmd = ""
destiny_cmd = ""
mail_generator = "/usr/bin/php5 /oxobox/engine/mail/mailgenerator.php {!r} {!r} {!r} {!r}"
file_path = "/oxobox/assets/{}/{}/{}.{}"
thumb_path = "/oxobox/assets/{}/{}/thumbs/"

files_types = {
    'video': ['mkv', 'flv', 'avi', 'mov', 'mpg', 'mpeg', 'mp4', 'vob', 'wmv', '3gp', 'm4v', 'webm', 'dv', 'mxf'],
    'audio': ['wav', 'wma', 'mp3', 'aac', 'aif', 'aiff', 'm4a'],
    'image': ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp', 'tga', 'gif', 'dng', 'psd', 'eps'],
    'document': ['doc', 'docx', 'xls', 'xlsx', 'txt', 'log', 'csv', 'ppt', 'pps', 'pptx', 'htm', 'html', 'dwg', 'pdf',
                 'wps', 'swf', 'rar', 'zip', 'ai']
}

playable_extensions = ['mp4', 'm4v', 'flv', 'mp3', 'jpg']

errors = {'input': "ERR001",            # Error con el INPUT
          'output': "ERR002",           # Error con el OUTPUT
          'stop': "ERR003",             # Se cancelo el encodeo
          'System': "ERR004",           # Error con el encodeo
          'copen': "ERR005",
          'cthumb': "ERR006",
          'eresize': "ERR007",          # Error de Resizeo de imagen
          'noconnect': "ERR008",        # Failed to connect to OpenOffice on port %d
          'nodesktop': "ERR009",        # Failed to create OpenOffice desktop on port %d
          'unsupportedconv': "ERR010",  # unsupported conversion
          'unknowndoc': "ERR011",       # unknown document family
          'commanderr': "ERR012",       # Error en el comando ffmpeg
          'unknowformat': "ERR013",     # Fromato desconocido
          'cantreadfile': "ERR014",     # No se puede leer el archivo
          'notzip': "ERR015",           # No es un ZIP
          'notrar': "ERR016",           # No es un RAR
          'protected_pdf': "ERR017"}    # PDF protegido contra copia