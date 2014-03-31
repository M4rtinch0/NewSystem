# -*- coding: utf-8 -*-
# Name:         Video
# Purpose:      Toma los datos del archivo, byte sizes, frame sizes, etc...
#
# Author:       Pela
#
# Created:      11/03/2013
# Notas:
from .Tools import split_path, file_exist
import subprocess


class Mediainfo(object):
    MEDIAINFO = subprocess.check_output(['which', 'mediainfo'], stderr=subprocess.STDOUT).split()[0]

    def __init__(self, file_abs_name):
        """
        :rtype : None
        :param file_abs_name: Absolute Path
        """
        self.file_abs_path = file_abs_name
        self.found = file_exist(self.file_abs_path)
        if self.found:
            self.file_type = ''
            self.file_path, self.file_name, self.file_extension = split_path(self.file_abs_path)
            self.info = self.parse_info()

    @staticmethod
    def __set_par(m_dict, index, value):
        if not index in m_dict or m_dict[index] is None or m_dict[index] == '':
            m_dict[index] = value

    def parse_info(self):
        """ Parses media info for filename """
        args = [self.MEDIAINFO, '-f', self.file_abs_path]
        output = subprocess.Popen(args, stdout=subprocess.PIPE).stdout
        data = output.readlines()
        output.close()
        mode = 'none'
        result = {'general_format': '', 'general_codec': '', 'general_size': None, 'general_bitrate': None,
                  'general_duration': None, 'video_format': '', 'video_codec_id': '', 'video_codec': '',
                  'video_bitrate': None, 'video_width': None, 'video_height': None, 'video_displayaspect': None,
                  'video_pixelaspect': None, 'video_scantype': '', 'audio_format': '', 'audio_codec_id': '',
                  'audio_codec': '', 'audio_bitrate': None, 'audio_channels': None, 'audio_samplerate': None,
                  'audio_resolution': None, 'audio_language': ''}
        for line in data:
            line = line.decode("utf-8")
            if ':' not in line:
                if 'General' in line:
                    mode = 'General'
                elif 'Video' in line:
                    mode = 'Video'
                elif 'Audio' in line:
                    mode = 'Audio'
                elif 'Image' in line:
                    mode = 'Image'
                elif 'Text' in line:
                    mode = 'Text'
            else:
                key, sep, value = line.partition(':')
                key = key.strip()
                value = value.strip()
                if mode == 'General':
                    if key == 'Format':
                        Mediainfo.__set_par(result, 'general_format', value)
                    if key == 'Codec':
                        Mediainfo.__set_par(result, 'general_codec', value)
                    if key == 'File size':
                        Mediainfo.__set_par(result, 'general_size', value)
                    if key == 'Overall bit rate':
                        Mediainfo.__set_par(result, 'general_bitrate', value)
                    if key == 'Duration':
                        Mediainfo.__set_par(result, 'general_duration', value)
                if mode == 'Video':
                    if key == 'Format':
                        Mediainfo.__set_par(result, 'video_format', value)
                    if key == 'Codec ID':
                        Mediainfo.__set_par(result, 'video_codec_id', value)
                    if key == 'Codec':
                        Mediainfo.__set_par(result, 'video_codec', value)
                    if key == 'Nominal bit rate':
                        Mediainfo.__set_par(result, 'video_bitrate', value)
                    if key == 'Width':
                        Mediainfo.__set_par(result, 'video_width', value)
                    if key == 'Height':
                        Mediainfo.__set_par(result, 'video_height', value)
                    if key == 'Display aspect ratio':
                        Mediainfo.__set_par(result, 'video_displayaspect', value)
                    if key == 'Pixel Aspect Ratio':
                        Mediainfo.__set_par(result, 'video_pixelaspect', value)
                    if key == 'Scan type':
                        Mediainfo.__set_par(result, 'video_scantype', value)
                if mode == 'Audio':
                    if key == 'Format':
                        Mediainfo.__set_par(result, 'audio_format', value)
                    if key == 'Codec ID':
                        Mediainfo.__set_par(result, 'audio_codec_id', value)
                    if key == 'Codec':
                        Mediainfo.__set_par(result, 'audio_codec', value)
                    if key == 'Bit rate':
                        Mediainfo.__set_par(result, 'audio_bitrate', value)
                    if key == 'Channel(s)':
                        Mediainfo.__set_par(result, 'audio_channels', value)
                    if key == 'Sampling rate':
                        Mediainfo.__set_par(result, 'audio_samplerate', value)
                    if key == 'Resolution':
                        Mediainfo.__set_par(result, 'audio_resolution', value)
                    if key == 'Language':
                        Mediainfo.__set_par(result, 'audio_language', value)
                if mode == 'Image':
                    if key == 'Format':
                        Mediainfo.__set_par(result, 'image_format', value)
                    if key == 'Width':
                        Mediainfo.__set_par(result, 'image_width', value)
                    if key == 'Height':
                        Mediainfo.__set_par(result, 'image_height', value)
                    if key == 'Color space':
                        Mediainfo.__set_par(result, 'image_color_space', value)
        return result

    def __repr__(self):
        """
        :return: String
        """
        general = ("<General general_format='{0}', general_codec='{1}', general_size='{2}', general_bitrate='{3}', "
                   "general_duration='{4}'>").format(self.info['general_format'], self.info['general_codec'],
                                                     self.info['general_size'], self.info['general_bitrate'],
                                                     self.info['general_duration'])
        video = ("<Video video_format='{0}', video_codec_id='{1}', video_codec='{2}', video_bitrate='{3}', "
                 "video_width='{4}', video_height='{5}', video_displayaspect='{6}', "
                 "video_pixelaspect='{7}'>").format(self.info['video_format'], self.info['video_codec_id'],
                                                    self.info['video_codec'], self.info['video_bitrate'],
                                                    self.info['video_width'], self.info['video_height'],
                                                    self.info['video_displayaspect'], self.info['video_pixelaspect'])
        audio = ("<Audio audio_format='{0}', audio_codec_id='{1}', audio_codec='{2}', audio_bitrate='{3}', "
                 "audio_channels='{4}', audio_samplerate='{5}'>").format(self.info['audio_format'],
                                                                         self.info['audio_codec_id'],
                                                                         self.info['audio_codec'],
                                                                         self.info['audio_bitrate'],
                                                                         self.info['audio_channels'],
                                                                         self.info['audio_samplerate'])
        image = ("<Image image_format='{0}', image_width='{1}', image_height='{2}', "
                 "image_color_space='{3}'>").format(self.info['image_format'], self.info['image_width'],
                                                    self.info['image_height'], self.info['image_color_space'])
        return "{}\n{}\n{}\n{}".format(general, video, audio, image)
