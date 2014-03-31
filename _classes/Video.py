# -*- coding: utf-8 -*-
# Name:     Video
# Purpose:  Encodea los videos
#
# Author:   Pela
#
# Created:  11/03/2013
# Notas:    Ffmpeg writes the data UNFLUSHED tp stderr making it unreadable
#           for stdio. To get the data the stderr file descriptor has to
#           set to NONBLOCK using fcntl
import os
import re
import time
import fcntl
import shlex
import select
import subprocess


class Encoder(object):
    def __init__(self):
        self.cmd = ''
        self.input_file = ''
        self.output_file = ''

    def encode_video(self, filename, callback=None):
        cmd = 'ffmpeg -i "%s" -acodec libfaac -ab 128kb ' + \
              '-vcodec mpeg4 -b 1200kb -mbd 2 -flags +4mv ' + \
              '-trellis 2 -cmp 2 -subcmp 2 -s 320x180 "%s.mp4"'
        pipe = subprocess.Popen(shlex.split(cmd % (filename, os.path.splitext(filename)[0])),
                                stderr=subprocess.PIPE,
                                close_fdse=True)
        fcntl.fcntl(pipe.stderr.fileno(),
                    fcntl.F_SETFL,
                    fcntl.fcntl(pipe.stderr.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK)
        # frame=   29 fps=  0 q=2.6 size=     114kB time=0.79 bitrate=1181.0kbits/s
        reo = re.compile("""\S+\s+(?P<frame>d+)            # frame
                            \s\S+\s+(?P<fps>\d+)           # fps
                            \sq=(?P<q>\S+)                 # q
                            \s\S+\s+(?P<size>\S+)          # size
                            \stime=(?P<time>\S+)           # time
                            \sbitrate=(?P<bitrate>[\d\.]+) # bitrate
                            """, re.X)
        while True:
            readx = select.select([pipe.stderr.fileno()], [], [])[0]
            if readx:
                chunk = pipe.stderr.read()
                if chunk == '':
                    break
                m = reo.match(chunk)
                if m and callback:
                    callback(m.groupdict())
            time.sleep(.1)