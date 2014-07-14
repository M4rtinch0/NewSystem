import subprocess
import os
from string import Template

def my_chown(path, uid, gid):
    os.chown(path, uid, gid)
    for item in os.listdir(path):
        itempath = os.path.join(path, item)
        if os.path.isfile(itempath):
            os.chown(itempath, uid, gid)
        elif os.path.isdir(itempath):
            os.chown(itempath, uid, gid)
            my_chown(itempath, uid, gid)

def seconds(duration):
    duration = str(duration)
    hr, minutes, seg = duration.split(':')
    return float(hr)*3600 + float(minutes)*60 + float(seg)

def get_duration(mfile):
    file_info = subprocess.check_output(['/usr/local/bin/ffmpeg', '-i', mfile]).split()
    try:
        duration = file_info[file_info.index('Duration:')+1][:-1]
    except Exception:
        return 'N/A'
    else:
        return seconds(duration)

def createDebug(path, name):
    import logging
    _l = logging.getLogger(name)
    _l.setLevel(logging.DEBUG)
    _l.propagate = 0
    h = logging.FileHandler(path)
    f = logging.Formatter("%(levelname)s ---> %(message)s")
    h.setFormatter(f)
    _l.addHandler(h)
    return _l

def createLog(path, name):
    import logging
    _l = logging.getLogger(name)
    _l.setLevel(logging.DEBUG)
    _l.propagate = 0
    h = logging.FileHandler(path)
    f = logging.Formatter("%(levelname)-8s %(asctime)s ---> %(message)s", '%a, %d %b %Y %H:%M:%S')
    h.setFormatter(f)
    _l.addHandler(h)
    return _l

MYSQL_USER = "root"
MYSQL_PASS = "4dm1n1str4d0rd3v3l0p"
MYSQL_DB = "oxobox"

AWS_ACCESS_KEY_ID = 'AKIAJRE4LPRZT4XZ2OGA'
AWS_SECRET_ACCESS_KEY = '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'
NEW_ASSET = 'NEW_ASSET_MESSAGE'
ENCODED_FILEVERSION = 'ENCODED_FILEVERSION_MESSAGE'
UPLOADED_CDN = 'FILE_UPLOADED_TO_CDN'

FTP_FOLDER = "/ftp/oxobox"
LOG_FOLDER = "/oxobox/logs/"
ffmpegBin = "/usr/bin/ffmpeg"
ffmbcBin = "/opt/ffmbc/bin/ffmbc"
phpBin = "/usr/bin/php5 "
convertBin = "/usr/bin/convert"
mogrifyBin = "/usr/bin/mogrify"
pdf2swfBin = "/opt/swftools/bin/pdf2swf"
assetFolder = "/oxobox/assets/%s/%s/"
thumbGen = "/oxobox/engine/_classes/ThumbGen.py %s"
thumbs = "thumbs/%s.jpg"
videoThumbs = "thumbs/%s"
videoThumbsN = "thumbs/%s/pic%04d.tga"
swf = "thumbs/%s.swf"
compressedToTxt = "/oxobox/engine/_classes/ZipRar.py %s"
videoConverter = "/oxobox/engine/video.py %s"
audioConverter = "/oxobox/engine/audio.py %s"
imageConverter = "/oxobox/engine/image.py %s"
docConverter = "/opt/libreoffice4.0/program/python /oxobox/engine/doc.py"
thumbGenerator = "/oxobox/engine/thumb.py %s"
mailSender = "/oxobox/engine/tools/mail/mailer.py"
waterPath = "/oxobox/web/watermarks/%s.png"
waveFormWav = "/oxobox/engine/tools/waveform/%s.wav"
waveFormGenerator = "/oxobox/engine/tools/waveform/waveformgenerator.php %s"
mailGenerator = "/oxobox/engine/tools/mail/mailgenerator.php %s %s %s %s"
waveFormJpg = "/oxobox/engine/waveform/%s.jpg"
temp_folder = "/tmp/"
ingestor = "/oxobox/engine/ingestor.py"
execDestiny = "/oxobox/engine/deliveries/Destiny %s &"
switchExten = {'flv': 'flv',
               'mp4': 'mp4',
               'h264mov': 'mov',
               'iphone': 'm4v',
               'dv-pal': 'dv',
               'dv-ntsc': 'dv',
               'mpeg2-pal': 'mpg',
               'mpeg2-ntsc': 'mpg',
               'mp3': 'mp3',
               'vmp3': 'mp3',
               'jpg': 'jpg',
               'pdf': 'pdf',
               'swf': 'swf',
               'bberry': 'avi',
               'imx30-pal-mov': 'mov',
               'imx40-pal-mov': 'mov',
               'imx50-pal-mov': 'mov',
               'imx30-pal-mxf': 'mxf',
               'imx40-pal-mxf': 'mxf',
               'imx50-pal-mxf': 'mxf',
               'imx30-ntsc-mov': 'mov',
               'imx40-ntsc-mov': 'mov',
               'imx50-ntsc-mov': 'mov',
               'imx30-ntsc-mxf': 'mxf',
               'imx40-ntsc-mxf': 'mxf',
               'imx50-ntsc-mxf': 'mxf',
               'imx50-1080-mxf': 'mxf',
               'dv-pal-avi': 'avi',
               'dv-pal-mov': 'mov',
               'dv-ntsc-avi': 'avi',
               'dv-ntsc-mov': 'mov',
               'dvcpro50': 'mov',
               'dvcproHD': 'mov',
               'mpeg-pal': 'mpg',
               'mpeg-ntsc': 'mpg',
               'mpeg-pal-avi': 'avi',
               'mpeg-ntsc-avi': 'avi',
               'mpeg-50-pal': 'mpg',
               'mpeg-25-hd': 'mpg',
               'netflix80': 'mpg',
               'netflix50': 'mpg',
               'mpeg-8-pal': 'mpg',
               'uncompressed-ntsc': 'mov',
               'avi-uncompressed-pal': 'avi',
               'mpeg-15-pal': 'mpg',
               'mpeg-25-pal': 'mpg',
               'mpeg': 'mpg',
               'xdcamhd422': 'mxf',
               'mxfop1abvtyc': 'mxf',
               'prores-sd': 'mov',
               'prores-hd': 'mov',
               'xdcamdtv': 'mxf',
               'xdcam-mov-1080i-50': 'mov',
               'dvcam-gxf': 'gxf'}

formateable = ['video',
               'audio',
               'image',
               'document']

videoTypes = ['mkv',
              'flv',
              'avi',
              'mov',
              'mpg',
              'mpeg',
              'mp4',
              'vob',
              'wmv',
              '3gp',
              'm4v',
              'webm',
              'dv',
              'mxf',
              'gxf']
audioTypes = ['wav',
              'wma',
              'mp3',
              'aac',
              'aif',
              'aiff',
              'm4a']
imageTypes = ['jpg',
              'jpeg',
              'png',
              'tiff',
              'tif',
              'bmp',
              'tga',
              'gif',
              'dng',
              'psd',
              'eps']
documentTypes = ['doc',
                 'docx',
                 'xls',
                 'xlsx',
                 'txt',
                 'log',
                 'csv',
                 'ppt',
                 'pps',
                 'pptx',
                 'htm',
                 'html',
                 'dwg',
                 'pdf',
                 'wps',
                 'swf',
                 'rar',
                 'zip',
                 'ai']
importTypes = ['xml', 'oxo']
extPlayables = ['mp4',
                'm4v',
                'flv',
                'mp3',
                'jpg',
                'png',
                'avi']
formatsPlayables = ['h264',
                    'vp6f',
                    'vp6',
                    'flv',
                    'mp3',
                    'mpeg4']
errors = {'input': "ERR001",            # Error con el INPUT
          'output': "ERR002",           # Error con el OUTPUT
          'stop': "ERR003",             # Se cancelo el encodeo
          'encoder': "ERR004",          # Error con el encodeo
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
imagesQ = {'Very poor': 10,
           'Poor': 30,
           'Good': 50,
           'Very good': 70,
           'Excelent': 90}
#
#VIDEO
#
waterMark = Template(
    '-vf "movie=${wm} [wm];[in] scale=${out_width}:-1,[wm] overlay=${width}:${height} [out]"'
)

h264MovCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -threads 0 -ss ${startTime} ${pad} -vcodec libx264 -b:v ${vBitrate} -bt ${vBitrate} \
    -acodec libfaac -b:a ${aBitrate} -ar ${aRate} -ac 2 -x264opts partitions="p8x8,b8x8,i8x8,i4x4":direct="auto":me="umh":trellis=1:merange=16:keyint=250:min-keyint=16:scenecut=40:b-pyramid:ref=6:qpmin=10:qpmax=51:qpstep=4:ipratio=0.71:subme=7 \
    %(watermark)s -vf scale=${width}:${height} -pix_fmt yuv420p "%(output_file)s"'
)

mp4Cmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -threads 0 -ss ${startTime} ${pad} -vcodec libx264 -b:v ${vBitrate} -bt ${vBitrate} \
    -acodec libfaac -b:a ${aBitrate} -ar ${aRate} -ac 2 -x264opts partitions="p8x8,b8x8,i8x8,i4x4":direct="auto":me="umh":trellis=1:merange=16:keyint=250:min-keyint=16:scenecut=40:b-pyramid:ref=6:qpmin=10:qpmax=51:qpstep=4:ipratio=0.71:subme=7 \
    %(watermark)s -vf scale=${width}:${height} -pix_fmt yuv420p "%(output_file)s"'
)

mp41PassCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -threads 0 -ss ${startTime} -s ${size} -vcodec libx264 -b ${vBitrate} -bt ${vBitrate} \
    -acodec libfaac -ab ${aBitrate} -ar ${aRate} -ac 2 -map_chapters -1,0 -flags +loop -deblockalpha 0 -deblockbeta 0 -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 \
    -flags2 +dct8x8+wpred+bpyramid+mixed_refs -directpred auto -me_method umh -subq 5 -trellis 1 -refs 2 -bf 1 -coder 1 -me_range 16 -g 300 -keyint_min 25 \
    -sc_threshold 40 -i_qfactor 0.71 -rc_eq "blurCplx^(1-qComp)" -qcomp 0.6 -qmin 10 -qmax 51 -qdiff 4 %(watermark)s "%(output_file)s"'
)

mp42PassCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -threads 0 -ss ${startTime} -s ${size} -vcodec libx264 -b ${vBitrate} -bt ${vBitrate} \
    -acodec libfaac -ab ${aBitrate} -ar ${aRate} -ac 2 -map_chapters -1,0 -flags +loop -deblockalpha 0 -deblockbeta 0 -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 \
    -flags2 +dct8x8+wpred+bpyramid+mixed_refs -directpred auto -me_method umh -subq 5 -trellis 1 -refs 2 -bf 1 -coder 1 -me_range 16 -g 300 -keyint_min 25 \
    -sc_threshold 40 -i_qfactor 0.71 -rc_eq "blurCplx^(1-qComp)" -qcomp 0.6 -qmin 10 -qmax 51 -qdiff 4 %(watermark)s "%(output_file)s"'
)

flvCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} ${pad} -s ${size} -f flv -vcodec flv -b:v ${vBitrate} -bt ${vBitrate} \
    -acodec libmp3lame -b:a ${aBitrate} -ar ${aRate} -ac 2 %(watermark)s "%(output_file)s"'
)

iphoneCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -threads 0 -ss ${startTime} -vf scale=640:-1 -vcodec libx264 -b:v 512k -bt 512k\
    -acodec libfaac -b:a 96k -ar 44100 -ac 2 -x264opts partitions="p8x8,b8x8,i8x8,i4x4":me="hex":trellis=1:merange=16:keyint=250:min-keyint=16:scenecut=40:b-pyramid:ref=6:qpmin=10:qpmax=51:qpstep=4:ipratio=0.71:subme=7 \
    %(watermark)s "%(output_file)s"'
)

bBerryCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -s ${size} -vcodec mpeg4 -b:v 400k -bt 400k \
    -acodec libmp3lame -ab 128k -ar 44100 -ac 2 %(watermark)s "%(output_file)s"'
)

mpeg2PalCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -threads 4 -ss ${startTime} -vcodec mpeg2video -b ${vBitrate} -minrate ${vBitrate} -maxrate ${vBitrate} -b ${vBitrate} \
    -bufsize 2000000 -rc_init_occupancy 2000000 -rc_buf_aggressivity 0.25 -qscale 1 -qmin 1 -async 1 -mbd 2 -bf 2 -trellis 2 -cmp 2 -subcmp 2 -g 45 -r pal -s pal \
    -pix_fmt ${pFmt} -acodec ${aCodec} -ab ${aBitrate} -ar ${aRate} -f mpegts %(watermark)s "%(output_file)s"'
)

mpeg2NtscCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -threads 4 -ss ${startTime} -vcodec mpeg2video -b ${vBitrate} -minrate ${vBitrate} -maxrate ${vBitrate} -b ${vBitrate} \
    -bufsize 2000000 -rc_init_occupancy 2000000 -rc_buf_aggressivity 0.25 -qscale 1 -qmin 1 -async 1 -mbd 2 -bf 2 -trellis 2 -cmp 2 -subcmp 2 -g 45 -r ntsc -s ntsc \
    -pix_fmt ${pFmt} -acodec ${aCodec} -ab ${aBitrate} -ar ${aRate} -f mpegts %(watermark)s "%(output_file)s"'
)

dvPalCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -target pal-dv -f dv %(watermark)s "%(output_file)s"'
)

dvNtscCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -target ntsc-dv -f dv %(watermark)s "%(output_file)s"'
)

imx30PalMovCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:576,pad=720:608:0:32 -r 25 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries bt470bg -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 30000k -maxrate 30000k -b 30000k -bufsize 1200000 -tff -rc_init_occupancy 1200000 -dc 10 -intra -vbsf imxdump -vtag mx3p \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx40PalMovCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:576,pad=720:608:0:32 -r 25 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries bt470bg -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 40000k -maxrate 40000k -b 40000k -bufsize 1600000 -tff -rc_init_occupancy 1600000 -dc 10 -intra -vbsf imxdump -vtag mx4p \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx50PalMovCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:576,pad=720:608:0:32 -r 25 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries bt470bg -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 50000k -maxrate 50000k -b 50000k -bufsize 2000000 -tff -rc_init_occupancy 2000000 -dc 10 -intra -vbsf imxdump -vtag mx5p \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx30PalMxfCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:576,pad=720:608:0:32 -r 25 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries bt470bg -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 30000k -maxrate 30000k -b 30000k -bufsize 1200000 -tff -rc_init_occupancy 1200000 -dc 10 -intra -f mxf_d10 \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx40PalMxfCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:576,pad=720:608:0:32 -r 25 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries bt470bg -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 40000k -maxrate 40000k -b 40000k -bufsize 1600000 -tff -rc_init_occupancy 1600000 -dc 10 -intra -f mxf_d10 \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx50PalMxfCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:576,pad=720:608:0:32 -r 25 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries bt470bg -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 50000k -maxrate 50000k -b 50000k -bufsize 2000000 -tff -rc_init_occupancy 2000000 -dc 10 -intra -f mxf_d10 \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx30NtscMovCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:486,pad=720:512:0:26 -r 30000/1001 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries smpte170m -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 30000k -maxrate 30000k -b 30000k -bufsize 1001000 -tff -rc_init_occupancy 1001000 -dc 10 -intra -vbsf imxdump -vtag mx3n \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx40NtscMovCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:486,pad=720:512:0:26 -r 30000/1001 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries smpte170m -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 40000k -maxrate 40000k -b 40000k -bufsize 1334667 -tff -rc_init_occupancy 1334667 -dc 10 -intra -vbsf imxdump -vtag mx4n \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx50NtscMovCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:486,pad=720:512:0:26 -r 30000/1001 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries smpte170m -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 50000k -maxrate 50000k -b 50000k -bufsize 1668334 -tff -rc_init_occupancy 1668334 -dc 10 -intra -vbsf imxdump -vtag mx5n \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx30NtscMxfCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:486,pad=720:512:0:26 -r 30000/1001 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries smpte170m -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 30000k -maxrate 30000k -b 30000k -bufsize 1001000 -tff -rc_init_occupancy 1001000 -dc 10 -intra -f mxf_d10 \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx40NtscMxfCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:486,pad=720:512:0:26 -r 30000/1001 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries smpte170m -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 40000k -maxrate 40000k -b 40000k -bufsize 1334667 -tff -rc_init_occupancy 1334667 -dc 10 -intra -f mxf_d10 \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx50NtscMxfCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:486,pad=720:512:0:26 -r 30000/1001 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries smpte170m -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 50000k -maxrate 50000k -b 50000k -bufsize 1668334 -tff -rc_init_occupancy 1668334 -dc 10 -intra -f mxf_d10 \
    -acodec pcm_s16le -ar 48000 "%(output_file)s"'
)

imx501080MxfCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=1920:1080 -r 25 -g 1 -vcodec mpeg2video -flags2 +ivlc+non_linear_q \
    -qscale 1 -ps 1 -qmin 1 -rc_max_vbv_use 1 -color_primaries smpte170m -color_transfer bt709 -color_matrix smpte170m -flags +ildct+low_delay -rc_min_vbv_use 1 \
    -pix_fmt yuv422p -minrate 50000k -maxrate 50000k -b 50000k -bufsize 8000k -tff -rc_init_occupancy 8000k -dc 10 -intra \
    -acodec pcm_s16be -ar 48000 "%(output_file)s"'
)

dvPalAviCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -y -vcodec dvvideo -vtag dvsd -s 720x576 -pix_fmt yuv420p -r pal -acodec pcm_s16le \
    -ar 48000 -ac 2 "%(output_file)s"'
)

dvPalMovCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -y -vcodec dvvideo -s 720x576 -pix_fmt yuv420p -r pal -acodec pcm_s16le \
    -ar 48000 -ac 2 "%(output_file)s"'
)

dvNtscAviCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -y -vcodec dvvideo -vtag dvsd -s 720x480 -pix_fmt yuv411p -r ntsc -acodec pcm_s16le \
    -ar 48000 -ac 2 "%(output_file)s"'
)

dvNtscMovCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -y -vcodec dvvideo -s 720x480 -pix_fmt yuv411p -r ntsc -acodec pcm_s16le \
    -ar 48000 -ac 2 "%(output_file)s"'
)

dvcpro50Cmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -target dvcpro50 -acodec pcm_s16le "%(output_file)s"'
)

dvcproHDCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -target dvcprohd -vf "fieldorder=tff" -acodec pcm_s16le "%(output_file)s"'
)

mpegNtscCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -vcodec mpeg2video -b:v 25M -minrate 25M -maxrate 25M -bufsize 1600000 -rc_init_occupancy 1600000 \
    -rc_buf_aggressivity 0.25 -flags +ilme+ildct -top 1 -q:v 1 -qmin 1 -async 1 -mbd 2 -bf 2 -trellis 2 -cmp 2 -subcmp 2 -g 45 -r ntsc -s ntsc -pix_fmt yuv422p \
    -acodec mp2 -ab 384k -ar 48000 -f mpegts "%(output_file)s"'
)

mpegPalAviCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -vcodec mpeg2video -b:v 25M -minrate 25M -maxrate 25M -bufsize 1600000 -rc_init_occupancy 1600000 \
    -rc_buf_aggressivity 0.25 -flags +ilme+ildct -top 1 -q:v 1 -qmin 1 -async 1 -mbd 2 -bf 2 -trellis 2 -cmp 2 -subcmp 2 -g 45 -r pal -s pal -pix_fmt yuv422p \
    -acodec mp2 -ab 384k -ar 48000 "%(output_file)s"'
)

mpegNtscAviCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -vcodec mpeg2video -b:v 25M -minrate 25M -maxrate 25M -bufsize 1600000 -rc_init_occupancy 1600000 \
    -rc_buf_aggressivity 0.25 -flags +ilme+ildct -top 1 -q:v 1 -qmin 1 -async 1 -mbd 2 -bf 2 -trellis 2 -cmp 2 -subcmp 2 -g 45 -r ntsc -s ntsc -pix_fmt yuv422p \
    -acodec mp2 -ab 384k -ar 48000 "%(output_file)s"'
)

mpeg50PalCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -vcodec mpeg2video -b:v 50M -minrate 50M -maxrate 50M -bufsize 2000000 -rc_init_occupancy 2000000 \
    -rc_buf_aggressivity 0.25 -flags +ilme+ildct -top 1 -q:v 1 -qmin 1 -async 1 -mbd 2 -bf 2 -trellis 2 -cmp 2 -subcmp 2 -g 45 -r pal -s pal -pix_fmt yuv422p \
    -acodec mp2 -ab 384k -ar 48000 -f mpegts "%(output_file)s"'
)

netflix80 = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -vcodec mpeg2video -flags +ilme -vf setfield=auto,scale=interl=-1 -b:v 80M -minrate 80M -maxrate 80M -bufsize 4000000 \
    -rc_init_occupancy 4000000 -g 1 -q:v 1 -qmin 1 -pix_fmt yuv422p -f mpegts -acodec mp2 -ar 48000 -b:a 384k "%(output_file)s"'
)

netflix50 = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -vcodec mpeg2video \
    -flags +ilme -vf setfield=auto,scale=interl=-1 -b:v 50M -minrate 50M -maxrate 50M -bufsize 2000000 \
    -rc_init_occupancy 2000000 -g 1 -q:v 1 -qmin 1 -pix_fmt yuv422p -f mpegts -acodec mp2 -ar 48000 \
    -b:a 384k "%(output_file)s"'
)

mpeg8PalCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -vcodec mpeg2video -b:v 8M \
    -minrate 8M -maxrate 8M -bufsize 800000 -rc_init_occupancy 800000 -rc_buf_aggressivity 0.25 -flags +ilme+ildct -top 1 \
    -q:v 1 -qmin 1 -async 1 -mbd 2 -bf 2 -trellis 2 -cmp 2 -subcmp 2 -g 45 -r pal -s pal -pix_fmt yuv422p \
    -acodec mp2 -ab 384k -ar 48000 -f mpegts "%(output_file)s"'
)

uncompressedNtscCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:486 -threads 4 \
    -vcodec rawvideo -pix_fmt uyvy422 -vtag 2vuy -acodec pcm_s16le "%(output_file)s"'
)

aviUncompressedPalCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:576 -threads 4 \
    -vcodec rawvideo -pix_fmt uyvy422 -vtag 2vuy -acodec pcm_s16le "%(output_file)s"'
)

mpeg15PalCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -vcodec mpeg2video -b:v 15M -minrate 15M -maxrate 15M -bufsize 1500000 -rc_init_occupancy 1500000 \
    -rc_buf_aggressivity 0.25 -flags +ilme+ildct -top 1 -q:v 1 -qmin 1 -async 1 -mbd 2 -bf 2 -trellis 2 -cmp 2 -subcmp 2 -g 45 -r pal -s pal -pix_fmt yuv422p \
    -acodec mp2 -ab 384k -ar 48000 -f mpegts "%(output_file)s"'
)

mpegCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -vcodec mpeg2video \
    -b:v ${vBitrate} -minrate ${vBitrate} -maxrate ${vBitrate} -bufsize 2500000 -rc_init_occupancy 2500000 \
    -rc_buf_aggressivity 0.25 -flags +ilme+ildct -top 1 -q:v 1 -qmin 1 -async 1 -mbd 2 -bf 2 -trellis 2 -cmp 2 -subcmp 2 \
    -g 45 -pix_fmt yuv422p -acodec mp2 -ab 384k -ar 48000 -f mpegts -vf scale=${width}:${height} "%(output_file)s"'
)

mpeg25PalCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -vcodec mpeg2video \
    -b:v 25M -minrate 25M -maxrate 25M -bufsize 2500000 -rc_init_occupancy 2500000 -rc_buf_aggressivity 0.25 \
    -flags +ilme+ildct -top 1 -q:v 1 -qmin 1 -async 1 -mbd 2 -bf 2 -trellis 2 -cmp 2 -subcmp 2 -g 45 -r pal -s pal \
    -pix_fmt yuv422p -acodec mp2 -ab 384k -ar 48000 -f mpegts "%(output_file)s"'
)

mpeg25HdCmd = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -ss ${startTime} -threads 4 -vcodec mpeg2video -b:v 25M -minrate 25M -maxrate 25M -bufsize 2500000 -rc_init_occupancy 2500000 \
    -rc_buf_aggressivity 0.25 -flags +ilme+ildct -top 1 -q:v 1 -qmin 1 -async 1 -mbd 2 -bf 2 -trellis 2 -cmp 2 -subcmp 2 -g 45 -vf scale="1920:1080" -pix_fmt yuv422p \
    -acodec mp2 -ab 384k -ar 48000 -f mpegts "%(output_file)s"'
)

xdCamHD422Cmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -tff -target xdcamhd422 -an "%(output_file)s" -ss ${startTime} -vol -205 -acodec pcm_s24le -ar 48000 -newaudio -acodec pcm_s24le \
    -ar 48000 -newaudio -acodec pcm_s24le -ar 48000 -newaudio -acodec pcm_s24le -ar 48000 -newaudio -map_audio_channel 0:1:0:0:1:0 -map_audio_channel 0:1:1:0:2:0 \
    -map_audio_channel 0:1:0:0:3:0 -map_audio_channel 0:1:1:0:4:0'
)

mxfOP1aDVTYC = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -bff -vf scale=540:576,pad=720:576:90:0 -r 25 -target dvcam -an "%(output_file)s" -ss ${startTime} -vol -205 -acodec pcm_s24le -ar 48000 -newaudio -acodec pcm_s24le \
    -ar 48000 -newaudio -acodec pcm_s24le -ar 48000 -newaudio -acodec pcm_s24le -ar 48000 -newaudio -map_audio_channel 0:1:0:0:1:0 -map_audio_channel 0:1:1:0:2:0 \
    -map_audio_channel 0:1:0:0:3:0 -map_audio_channel 0:1:1:0:4:0'
)

xdCamDTVCmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -tff -target xdcamhd422 -an "%(output_file)s" -ss ${startTime}  -acodec pcm_s24le -ar 48000 -newaudio -acodec pcm_s24le -ar 48000 -newaudio \
    -map_audio_channel 0:1:0:0:1:0 -map_audio_channel 0:1:1:0:2:0'
)

xdCamMov1080i50Cmd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -target xdcamhd422 -vtag xd5c -ar 48000 -acodec pcm_s24le "%(output_file)s"'
)

proResSd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vcodec prores -profile hq -vf scale=720:486:interl=-1,fieldorder=bff -r 30000/1001 \
    -acodec pcm_s24le -ar 48000 -ac 2 "%(output_file)s"'
)

proResHd = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vcodec prores -profile hq -vf scale=1920:1080:interl=-1,fieldorder=bff -r 30000/1001 \
    -acodec pcm_s24le -ar 48000 -ac 2 "%(output_file)s"'
)

lameMp3 = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -f mp3 -ss ${startTime} -ab ${aBitrate} -ar ${aRate} -ac 2 \
    -acodec libmp3lame %(watermark)s "%(output_file)s"'
)

videoMp3 = Template(
    '%(ffmpeg_bin)s -y -i "%(input_file)s" -f mp3 -ss ${startTime} -ab ${aBitrate} -ar ${aRate} -ac 2 \
    -acodec libmp3lame %(watermark)s "%(output_file)s"'
)

dvCamGxf = Template(
    '%(ffmbc_bin)s -y -i "%(input_file)s" -ss ${startTime} -vf scale=720:480:interl=-1,fieldorder=bff -r 30000/1001 -target dvcam -an -f gxf "%(output_file)s" \
    -acodec pcm_s16le -ar 48000 -newaudio -acodec pcm_s16le -ar 48000 -newaudio -map_audio_channel 0:1:0:0:1:0 -map_audio_channel 0:1:1:0:2:0'
)

flvTool2 = "/usr/bin/flvtool2 -U %s"

exportInterval = 5000
xvfbCmd = "/usr/bin/Xvfb :100 -screen 0 1280x1024x16"
oooCmd = '/usr/bin/openoffice -accept="socket,host=localhost,port=8100;urp;StarOffice.ServiceManager" -norestore \
-nofirstwizard -nologo -headless -invisible -display :100'
DEFAULT_OPENOFFICE_PORT = 8100
FAMILY_TEXT = "Text"
FAMILY_WEB = "Web"
FAMILY_SPREADSHEET = "Spreadsheet"
FAMILY_PRESENTATION = "Presentation"
FAMILY_DRAWING = "Drawing"
IMPORT_FILTER_MAP = {
    "txt": {
        "FilterName": "Text (encoded)",
        "FilterOptions": "utf8"
    },
    "csv": {
        "FilterName": "Text - txt - csv (StarCalc)",
        "FilterOptions": "44,34,0"
    }
}
EXPORT_FILTER_MAP = {
    "pdf": {
        FAMILY_TEXT: {"FilterName": "writer_pdf_Export"},
        FAMILY_WEB: {"FilterName": "writer_web_pdf_Export"},
        FAMILY_SPREADSHEET: {"FilterName": "calc_pdf_Export"},
        FAMILY_PRESENTATION: {"FilterName": "impress_pdf_Export"},
        FAMILY_DRAWING: {"FilterName": "draw_pdf_Export"}
    },
    "html": {
        FAMILY_TEXT: {"FilterName": "HTML (StarWriter)"},
        FAMILY_SPREADSHEET: {"FilterName": "HTML (StarCalc)"},
        FAMILY_PRESENTATION: {"FilterName": "impress_html_Export"}
    },
    "txt": {
        FAMILY_TEXT: {
            "FilterName": "Text",
            "FilterOptions": "utf8"
        }
    },
    "swf": {
        FAMILY_DRAWING: {"FilterName": "draw_flash_Export"},
        FAMILY_PRESENTATION: {"FilterName": "impress_flash_Export"}
    }
}

PAGE_STYLE_OVERRIDE_PROPERTIES = {
    FAMILY_SPREADSHEET: {
        "PageScale": 50,
        "PrintGrid": False,
    }
}