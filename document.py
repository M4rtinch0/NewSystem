#!/usr/bin/python -u
# -*- coding: utf-8 -*-
# Name:     image.py
# Purpose:  Encodea las imagenes.
#
# Author:   Pela
#
# Created:  07/03/2014
# Notas:
from distutils.version import LooseVersion
import glob
import os
import subprocess
import sys
import traceback
import time
import shlex
import signal
import logging
import shutil
from _classes.SingleInstance import SingleInstance
from _classes.DataBaseDoc import DataBase
from _classes import Config
# import ZipRar

doctypes = ('document', 'graphics', 'presentation', 'spreadsheet')
error_dict = {
    1: 'SYSTEM_ERROR',
    2: 'UNO_EXCEPTION',
    3: 'IOEXCEPTION',
    4: 'CANNOT_CONVERT',
    5: 'UNO_EXCEPTION',
    6: 'RUNTIME_EXCEPTION',
    7: 'DISPOSED_EXCEPTION',
    8: 'ILLEGAL_ARGUMENT',
    9: 'SOURCE_NOT_AVAILABLE',
    10: 'INPUT_FILE_DOESENT_EXIST',
    11: 'NOT_ZIP',
    12: 'NOT_RAR',
    13: 'OUTPUT_ERROR',
    14: 'CANNOT_MKDIR_THUMB',
    15: 'CANNOT_COPY_ORIG_PDF',
    16: 'CANNOT_CONVERT_INPUT_ERROR',
    17: 'CANNOT_CONVERT_PROTECTED_PDF',
    18: 'NO_DATA',
    19: 'E_DATA_ERROR_CODE'
}


def set_logger():
    global logger
    logger = logging.getLogger('NewDocDebug')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(Config.LOG_FOLDER + 'Debug.log')
    fh.setLevel(logging.DEBUG)
    # ch = logging.StreamHandler()
    #ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(lineno)s]\t %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    #ch.setFormatter(formatter)
    logger.addHandler(fh)
    #logger.addHandler(ch)


def kill_all_soffice():
    logger.info("Checking if soffice or soffice.bin are running")
    proc_res = subprocess.check_output(['ps', '-A'])
    proc_res = proc_res.decode('utf-8')
    proc_res = proc_res.split('\n')
    for line in proc_res:
        if 'soffice' in line or 'soffice.bin' in line:
            logger.info("Founded")
            pid = int(line.split(None, 1)[0])
            logger.info("PID: " + str(pid) + " KILL HIM!")
            os.kill(pid, signal.SIGKILL)


class Office:
    def __init__(self, basepath, urepath, unopath, pyuno, binary, python, pythonhome):
        self.basepath = basepath
        self.urepath = urepath
        self.unopath = unopath
        self.pyuno = pyuno
        self.binary = binary
        self.python = python
        self.pythonhome = pythonhome

    def __str__(self):
        return self.basepath

    def __repr__(self):
        return self.basepath


def realpath(*args):
    """
    Implement a combination of os.path.join(), os.path.abspath() and
    os.path.realpath() in order to normalize path constructions
    """
    ret = ''
    for arg in args:
        ret = os.path.join(ret, arg)
    return os.path.realpath(os.path.abspath(ret))


def find_offices():
    ret = []
    extrapaths = []

    # Try using UNO_PATH first
    if 'UNO_PATH' in os.environ:
        extrapaths += [os.environ['UNO_PATH'], os.path.dirname(os.environ['UNO_PATH']),
                       os.path.dirname(os.path.dirname(os.environ['UNO_PATH']))]
    else:
        extrapaths += "{}{}{}{}{}{}{}{}{}{}".format(
            glob.glob('/usr/lib*/libreoffice*'), glob.glob('/usr/lib*/openoffice*'),
            glob.glob('/usr/lib*/ooo*'), glob.glob('/opt/libreoffice*'),
            glob.glob('/opt/openoffice*'), glob.glob('/opt/ooo*'),
            glob.glob('/usr/local/libreoffice*'), glob.glob('/usr/local/openoffice*'),
            glob.glob('/usr/local/ooo*'), glob.glob('/usr/local/lib/libreoffice*'))

    # Find a working set for python UNO bindings
    for basepath in extrapaths:
        officelibraries = ('pyuno.so',)
        officebinaries = ('soffice.bin',)
        pythonbinaries = ('python.bin', 'python',)
        pythonhomes = ('python-core-*',)

        # Older LibreOffice/OpenOffice and Windows use basis-link/ or basis/
        # libpath = 'error'
        for basis in ('basis-link', 'basis', ''):
            for lib in officelibraries:
                if os.path.isfile(realpath(basepath, basis, 'program', lib)):
                    libpath = realpath(basepath, basis, 'program')
                    officelibrary = realpath(libpath, lib)
                    logger.info("Found %s in %s" % (lib, libpath))
                    # Break the inner loop...
                    break
            # Continue if the inner loop wasn't broken.
            else:
                continue
            # Inner loop was broken, break the outer.
            break
        else:
            continue

        # unopath = 'error'
        for basis in ('basis-link', 'basis', ''):
            for cbin in officebinaries:
                if os.path.isfile(realpath(basepath, basis, 'program', cbin)):
                    unopath = realpath(basepath, basis, 'program')
                    officebinary = realpath(unopath, cbin)
                    logger.info("Found %s in %s" % (cbin, unopath))
                    # Break the inner loop...
                    break
            # Continue if the inner loop wasn't broken.
            else:
                continue
            # Inner loop was broken, break the outer.
            break
        else:
            continue

        urepath = ''
        for basis in ('basis-link', 'basis', ''):
            for ure in ('ure-link', 'ure', 'URE', ''):
                if os.path.isfile(realpath(basepath, basis, ure, 'lib', 'unorc')):
                    urepath = realpath(basepath, basis, ure)
                    logger.info("Found %s in %s" % ('unorc', realpath(urepath, 'lib')))
                    # Break the inner loop...
                    break
            # Continue if the inner loop wasn't broken.
            else:
                continue
            # Inner loop was broken, break the outer.
            break

        pythonhome = None
        for home in pythonhomes:
            if glob.glob(realpath(libpath, home)):
                pythonhome = glob.glob(realpath(libpath, home))[0]
                logger.info("Found %s in %s" % (home, pythonhome))
                break

        for pythonbinary in pythonbinaries:
            if os.path.isfile(realpath(unopath, pythonbinary)):
                logger.info("Found %s in %s" % (pythonbinary, unopath))
                ret.append(
                    Office(basepath, urepath, unopath, officelibrary, officebinary, realpath(unopath, pythonbinary),
                           pythonhome))
        else:
            logger.info("Considering %s" % basepath)
            ret.append(Office(basepath, urepath, unopath, officelibrary, officebinary, sys.executable, None))

    return ret


def office_environ(coffice):
    # Set PATH so that crash_report is found
    os.environ['PATH'] = ''.join([realpath(coffice.basepath, 'program'), os.pathsep, os.environ['PATH']])
    # Set UNO_PATH so that "officehelper.bootstrap()" can find soffice executable:
    # print(coffice.unopath)
    os.environ['UNO_PATH'] = coffice.unopath

    # Set URE_BOOTSTRAP so that "uno.getComponentContext()" bootstraps a complete
    # UNO environment

    os.environ['HOME'] = '/tmp'

    #print(realpath(coffice.basepath, 'program', 'fundamentalrc'))
    os.environ['URE_BOOTSTRAP'] = ''.join(
        ['vnd.sun.star.pathname:', realpath(coffice.basepath, 'program', 'fundamentalrc')])

    # Set LD_LIBRARY_PATH so that "import pyuno" finds libpyuno.so:
    if 'LD_LIBRARY_PATH' in os.environ:
        os.environ['LD_LIBRARY_PATH'] = ''.join(
            [coffice.unopath, os.pathsep, realpath(coffice.urepath, 'lib'), os.pathsep, os.environ['LD_LIBRARY_PATH']])
    else:
        os.environ['LD_LIBRARY_PATH'] = ''.join([coffice.unopath, os.pathsep, realpath(coffice.urepath, 'lib')])

    #print(coffice.pythonhome)
    if coffice.pythonhome:
        for libpath in (realpath(coffice.pythonhome, 'lib'),
                        realpath(coffice.pythonhome, 'lib', 'lib-dynload'),
                        realpath(coffice.pythonhome, 'lib', 'lib-tk'),
                        realpath(coffice.pythonhome, 'lib', 'site-packages'),
                        coffice.unopath):
            sys.path.insert(0, libpath)
    else:
        # Still needed for system python using LibreOffice UNO bindings
        # Although we prefer to use a system UNO binding in this case
        sys.path.append(coffice.unopath)


def python_switch(coffice):
    if coffice.pythonhome:
        os.environ['PYTHONHOME'] = coffice.pythonhome
        os.environ['PYTHONPATH'] = ''.join([realpath(coffice.pythonhome, 'lib'),
                                            os.pathsep,
                                            realpath(coffice.pythonhome, 'lib', 'lib-dynload'),
                                            os.pathsep,
                                            realpath(coffice.pythonhome, 'lib', 'lib-tk'),
                                            os.pathsep,
                                            realpath(coffice.pythonhome, 'lib', 'site-packages'),
                                            os.pathsep,
                                            coffice.unopath])

    os.environ['UNO_PATH'] = coffice.unopath

    logger.info("-> Switching from %s to %s" % (sys.executable, coffice.python))

    # Set LD_LIBRARY_PATH so that "import pyuno" finds libpyuno.so:
    if 'LD_LIBRARY_PATH' in os.environ:
        os.environ['LD_LIBRARY_PATH'] = ''.join([coffice.unopath,
                                                 os.pathsep,
                                                 realpath(coffice.urepath, 'lib'),
                                                 os.pathsep,
                                                 os.environ['LD_LIBRARY_PATH']])
    else:
        os.environ['LD_LIBRARY_PATH'] = ''.join([coffice.unopath,
                                                 os.pathsep,
                                                 realpath(coffice.urepath, 'lib')])

    try:
        os.execvpe(coffice.python, [coffice.python, ] + sys.argv[0:], os.environ)
    except OSError:
        ret = os.spawnvpe(os.P_WAIT,
                          coffice.python,
                          [coffice.python, ] + sys.argv[0:],
                          os.environ)
        sys.exit(ret)


class Fmt:
    def __init__(self, doctype, name, extension, summary, cfilter):
        self.doctype = doctype
        self.name = name
        self.extension = extension
        self.summary = summary
        self.filter = cfilter

    def __str__(self):
        return "%s [.%s]" % (self.summary, self.extension)

    def __repr__(self):
        return "%s/%s" % (self.name, self.doctype)


class FmtList:
    def __init__(self):
        self.list = []

    def add(self, doctype, name, extension, summary, cfilter):
        self.list.append(Fmt(doctype, name, extension, summary, cfilter))

    def byname(self, name):
        ret = []
        for fmt in self.list:
            if fmt.name == name:
                ret.append(fmt)
        return ret

    def byextension(self, extension):
        ret = []
        for fmt in self.list:
            if os.extsep + fmt.extension == extension:
                ret.append(fmt)
        return ret

    def bydoctype(self, doctype, name):
        ret = []
        for fmt in self.list:
            if fmt.name == name and fmt.doctype == doctype:
                ret.append(fmt)
        return ret


fmts = FmtList()

# TextDocument
fmts.add('document', 'bib', 'bib', 'BibTeX', 'BibTeX_Writer')  # 22
fmts.add('document', 'doc', 'doc', 'Microsoft Word 97/2000/XP', 'MS Word 97')  # 29
fmts.add('document', 'doc6', 'doc', 'Microsoft Word 6.0', 'MS WinWord 6.0')  # 24
fmts.add('document', 'doc95', 'doc', 'Microsoft Word 95', 'MS Word 95')  # 28
fmts.add('document', 'docbook', 'xml', 'DocBook', 'DocBook File')  # 39
fmts.add('document', 'docx', 'docx', 'Microsoft Office Open XML', 'Office Open XML Text')
fmts.add('document', 'docx7', 'docx', 'Microsoft Office Open XML', 'MS Word 2007 XML')
fmts.add('document', 'fodt', 'fodt', 'OpenDocument Text (Flat XML)', 'OpenDocument Text Flat XML')
fmts.add('document', 'html', 'html', 'HTML Document (OpenOffice.org Writer)', 'HTML (StarWriter)')  # 3
fmts.add('document', 'latex', 'ltx', 'LaTeX 2e', 'LaTeX_Writer')  # 31
fmts.add('document', 'mediawiki', 'txt', 'MediaWiki', 'MediaWiki')
fmts.add('document', 'odt', 'odt', 'ODF Text Document', 'writer8')  # 10
fmts.add('document', 'ooxml', 'xml', 'Microsoft Office Open XML', 'MS Word 2003 XML')  # 11
fmts.add('document', 'ott', 'ott', 'Open Document Text', 'writer8_template')  # 21
fmts.add('document', 'pdb', 'pdb', 'AportisDoc (Palm)', 'AportisDoc Palm DB')
fmts.add('document', 'pdf', 'pdf', 'Portable Document Format', 'writer_pdf_Export')  # 18
fmts.add('document', 'psw', 'psw', 'Pocket Word', 'PocketWord File')
fmts.add('document', 'rtf', 'rtf', 'Rich Text Format', 'Rich Text Format')  # 16
fmts.add('document', 'sdw', 'sdw', 'StarWriter 5.0', 'StarWriter 5.0')  # 23
fmts.add('document', 'sdw4', 'sdw', 'StarWriter 4.0', 'StarWriter 4.0')  # 2
fmts.add('document', 'sdw3', 'sdw', 'StarWriter 3.0', 'StarWriter 3.0')  # 20
fmts.add('document', 'stw', 'stw', 'Open Office.org 1.0 Text Document Template',
         'writer_StarOffice_XML_Writer_Template')  # 9
fmts.add('document', 'sxw', 'sxw', 'Open Office.org 1.0 Text Document', 'StarOffice XML (Writer)')  # 1
fmts.add('document', 'text', 'txt', 'Text Encoded', 'Text (encoded)')  # 26
fmts.add('document', 'txt', 'txt', 'Text', 'Text')  # 34
fmts.add('document', 'uot', 'uot', 'Unified Office Format text', 'UOF text')  # 27
fmts.add('document', 'vor', 'vor', 'StarWriter 5.0 Template', 'StarWriter 5.0 Vorlage/Template')  # 6
fmts.add('document', 'vor4', 'vor', 'StarWriter 4.0 Template', 'StarWriter 4.0 Vorlage/Template')  # 5
fmts.add('document', 'vor3', 'vor', 'StarWriter 3.0 Template', 'StarWriter 3.0 Vorlage/Template')  # 4
fmts.add('document', 'xhtml', 'html', 'XHTML Document', 'XHTML Writer File')  # 33

# WebDocument
fmts.add('web', 'etext', 'txt', 'Text Encoded (OpenOffice.org Writer/Web)', 'Text (encoded) (StarWriter/Web)')  # 14
fmts.add('web', 'html10', 'html', 'OpenOffice.org 1.0 HTML Template',
         'writer_web_StarOffice_XML_Writer_Web_Template')  # 11
fmts.add('web', 'html', 'html', 'HTML Document', 'HTML')  # 2
fmts.add('web', 'html', 'html', 'HTML Document Template', 'writerweb8_writer_template')  # 13
fmts.add('web', 'mediawiki', 'txt', 'MediaWiki', 'MediaWiki_Web')  # 9
fmts.add('web', 'pdf', 'pdf', 'PDF - Portable Document Format', 'writer_web_pdf_Export')  # 10
fmts.add('web', 'sdw3', 'sdw', 'StarWriter 3.0 (OpenOffice.org Writer/Web)', 'StarWriter 3.0 (StarWriter/Web)')  # 3
fmts.add('web', 'sdw4', 'sdw', 'StarWriter 4.0 (OpenOffice.org Writer/Web)', 'StarWriter 4.0 (StarWriter/Web)')  # 4
fmts.add('web', 'sdw', 'sdw', 'StarWriter 5.0 (OpenOffice.org Writer/Web)', 'StarWriter 5.0 (StarWriter/Web)')  # 5
fmts.add('web', 'txt', 'txt', 'OpenOffice.org Text (OpenOffice.org Writer/Web)', 'writerweb8_writer')  # 12
fmts.add('web', 'text10', 'txt', 'OpenOffice.org 1.0 Text Document (OpenOffice.org Writer/Web)',
         'writer_web_StarOffice_XML_Writer')  # 15
fmts.add('web', 'text', 'txt', 'Text (OpenOffice.org Writer/Web)', 'Text (StarWriter/Web)')  # 8
fmts.add('web', 'vor4', 'vor', 'StarWriter/Web 4.0 Template', 'StarWriter/Web 4.0 Vorlage/Template')  # 6
fmts.add('web', 'vor', 'vor', 'StarWriter/Web 5.0 Template', 'StarWriter/Web 5.0 Vorlage/Template')  # 7

# Spreadsheet
fmts.add('spreadsheet', 'csv', 'csv', 'Text CSV', 'Text - txt - csv (StarCalc)')  # 16
fmts.add('spreadsheet', 'dbf', 'dbf', 'dBASE', 'dBase')  # 22
fmts.add('spreadsheet', 'dif', 'dif', 'Data Interchange Format', 'DIF')  # 5
fmts.add('spreadsheet', 'fods', 'fods', 'OpenDocument Spreadsheet (Flat XML)', 'OpenDocument Spreadsheet Flat XML')
fmts.add('spreadsheet', 'html', 'html', 'HTML Document (OpenOffice.org Calc)', 'HTML (StarCalc)')  # 7
fmts.add('spreadsheet', 'ods', 'ods', 'ODF Spreadsheet', 'calc8')  # 15
fmts.add('spreadsheet', 'ooxml', 'xml', 'Microsoft Excel 2003 XML', 'MS Excel 2003 XML')  # 23
fmts.add('spreadsheet', 'ots', 'ots', 'ODF Spreadsheet Template', 'calc8_template')  # 14
fmts.add('spreadsheet', 'pdf', 'pdf', 'Portable Document Format', 'calc_pdf_Export')  # 34
fmts.add('spreadsheet', 'pxl', 'pxl', 'Pocket Excel', 'Pocket Excel')
fmts.add('spreadsheet', 'sdc', 'sdc', 'StarCalc 5.0', 'StarCalc 5.0')  # 31
fmts.add('spreadsheet', 'sdc4', 'sdc', 'StarCalc 4.0', 'StarCalc 4.0')  # 11
fmts.add('spreadsheet', 'sdc3', 'sdc', 'StarCalc 3.0', 'StarCalc 3.0')  # 29
fmts.add('spreadsheet', 'slk', 'slk', 'SYLK', 'SYLK')  # 35
fmts.add('spreadsheet', 'stc', 'stc', 'OpenOffice.org 1.0 Spreadsheet Template',
         'calc_StarOffice_XML_Calc_Template')  # 2
fmts.add('spreadsheet', 'sxc', 'sxc', 'OpenOffice.org 1.0 Spreadsheet', 'StarOffice XML (Calc)')  # 3
fmts.add('spreadsheet', 'uos', 'uos', 'Unified Office Format spreadsheet', 'UOF spreadsheet')  # 9
fmts.add('spreadsheet', 'vor3', 'vor', 'StarCalc 3.0 Template', 'StarCalc 3.0 Vorlage/Template')  # 18
fmts.add('spreadsheet', 'vor4', 'vor', 'StarCalc 4.0 Template', 'StarCalc 4.0 Vorlage/Template')  # 19
fmts.add('spreadsheet', 'vor', 'vor', 'StarCalc 5.0 Template', 'StarCalc 5.0 Vorlage/Template')  # 20
fmts.add('spreadsheet', 'xhtml', 'xhtml', 'XHTML', 'XHTML Calc File')  # 26
fmts.add('spreadsheet', 'xls', 'xls', 'Microsoft Excel 97/2000/XP', 'MS Excel 97')  # 12
fmts.add('spreadsheet', 'xls5', 'xls', 'Microsoft Excel 5.0', 'MS Excel 5.0/95')  # 8
fmts.add('spreadsheet', 'xls95', 'xls', 'Microsoft Excel 95', 'MS Excel 95')  # 10
fmts.add('spreadsheet', 'xlt', 'xlt', 'Microsoft Excel 97/2000/XP Template', 'MS Excel 97 Vorlage/Template')  # 6
fmts.add('spreadsheet', 'xlt5', 'xlt', 'Microsoft Excel 5.0 Template', 'MS Excel 5.0/95 Vorlage/Template')  # 28
fmts.add('spreadsheet', 'xlt95', 'xlt', 'Microsoft Excel 95 Template', 'MS Excel 95 Vorlage/Template')  # 21

# Graphics
fmts.add('graphics', 'bmp', 'bmp', 'Windows Bitmap', 'draw_bmp_Export')  # 21
fmts.add('graphics', 'emf', 'emf', 'Enhanced Metafile', 'draw_emf_Export')  # 15
fmts.add('graphics', 'eps', 'eps', 'Encapsulated PostScript', 'draw_eps_Export')  # 48
fmts.add('graphics', 'fodg', 'fodg', 'OpenDocument Drawing (Flat XML)', 'OpenDocument Drawing Flat XML')
fmts.add('graphics', 'gif', 'gif', 'Graphics Interchange Format', 'draw_gif_Export')  # 30
fmts.add('graphics', 'html', 'html', 'HTML Document (OpenOffice.org Draw)', 'draw_html_Export')  # 37
fmts.add('graphics', 'jpg', 'jpg', 'Joint Photographic Experts Group', 'draw_jpg_Export')  # 3
fmts.add('graphics', 'met', 'met', 'OS/2 Metafile', 'draw_met_Export')  # 43
fmts.add('graphics', 'odd', 'odd', 'OpenDocument Drawing', 'draw8')  # 6
fmts.add('graphics', 'otg', 'otg', 'OpenDocument Drawing Template', 'draw8_template')  # 20
fmts.add('graphics', 'pbm', 'pbm', 'Portable Bitmap', 'draw_pbm_Export')  # 14
fmts.add('graphics', 'pct', 'pct', 'Mac Pict', 'draw_pct_Export')  # 41
fmts.add('graphics', 'pdf', 'pdf', 'Portable Document Format', 'draw_pdf_Export')  # 28
fmts.add('graphics', 'pgm', 'pgm', 'Portable Graymap', 'draw_pgm_Export')  # 11
fmts.add('graphics', 'png', 'png', 'Portable Network Graphic', 'draw_png_Export')  # 2
fmts.add('graphics', 'ppm', 'ppm', 'Portable Pixelmap', 'draw_ppm_Export')  # 5
fmts.add('graphics', 'ras', 'ras', 'Sun Raster Image', 'draw_ras_Export')  # # 31
fmts.add('graphics', 'std', 'std', 'OpenOffice.org 1.0 Drawing Template', 'draw_StarOffice_XML_Draw_Template')  # 53
fmts.add('graphics', 'svg', 'svg', 'Scalable Vector Graphics', 'draw_svg_Export')  # 50
fmts.add('graphics', 'svm', 'svm', 'StarView Metafile', 'draw_svm_Export')  # 55
fmts.add('graphics', 'swf', 'swf', 'Macromedia Flash (SWF)', 'draw_flash_Export')  # 23
fmts.add('graphics', 'sxd', 'sxd', 'OpenOffice.org 1.0 Drawing', 'StarOffice XML (Draw)')  # 26
fmts.add('graphics', 'sxd3', 'sxd', 'StarDraw 3.0', 'StarDraw 3.0')  # 40
fmts.add('graphics', 'sxd5', 'sxd', 'StarDraw 5.0', 'StarDraw 5.0')  # 44
fmts.add('graphics', 'sxw', 'sxw', 'StarOffice XML (Draw)', 'StarOffice XML (Draw)')
fmts.add('graphics', 'tiff', 'tiff', 'Tagged Image File Format', 'draw_tif_Export')  # 13
fmts.add('graphics', 'vor', 'vor', 'StarDraw 5.0 Template', 'StarDraw 5.0 Vorlage')  # 36
fmts.add('graphics', 'vor3', 'vor', 'StarDraw 3.0 Template', 'StarDraw 3.0 Vorlage')  # 35
fmts.add('graphics', 'wmf', 'wmf', 'Windows Metafile', 'draw_wmf_Export')  # 8
fmts.add('graphics', 'xhtml', 'xhtml', 'XHTML', 'XHTML Draw File')  # 45
fmts.add('graphics', 'xpm', 'xpm', 'X PixMap', 'draw_xpm_Export')  # 19

# Presentation
fmts.add('presentation', 'bmp', 'bmp', 'Windows Bitmap', 'impress_bmp_Export')  # 15
fmts.add('presentation', 'emf', 'emf', 'Enhanced Metafile', 'impress_emf_Export')  # 16
fmts.add('presentation', 'eps', 'eps', 'Encapsulated PostScript', 'impress_eps_Export')  # 17
fmts.add('presentation', 'fodp', 'fodp', 'OpenDocument Presentation (Flat XML)', 'OpenDocument Presentation Flat XML')
fmts.add('presentation', 'gif', 'gif', 'Graphics Interchange Format', 'impress_gif_Export')  # 18
fmts.add('presentation', 'html', 'html', 'HTML Document (OpenOffice.org Impress)', 'impress_html_Export')  # 43
fmts.add('presentation', 'jpg', 'jpg', 'Joint Photographic Experts Group', 'impress_jpg_Export')  # 19
fmts.add('presentation', 'met', 'met', 'OS/2 Metafile', 'impress_met_Export')  # 20
fmts.add('presentation', 'odg', 'odg', 'ODF Drawing (Impress)', 'impress8_draw')  # 29
fmts.add('presentation', 'odp', 'odp', 'ODF Presentation', 'impress8')  # 9
fmts.add('presentation', 'otp', 'otp', 'ODF Presentation Template', 'impress8_template')  # 38
fmts.add('presentation', 'pbm', 'pbm', 'Portable Bitmap', 'impress_pbm_Export')  # 21
fmts.add('presentation', 'pct', 'pct', 'Mac Pict', 'impress_pct_Export')  # 22
fmts.add('presentation', 'pdf', 'pdf', 'Portable Document Format', 'impress_pdf_Export')  # 23
fmts.add('presentation', 'pgm', 'pgm', 'Portable Graymap', 'impress_pgm_Export')  # 24
fmts.add('presentation', 'png', 'png', 'Portable Network Graphic', 'impress_png_Export')  # 25
fmts.add('presentation', 'potm', 'potm', 'Microsoft PowerPoint 2007/2010 XML Template',
         'Impress MS PowerPoint 2007 XML Template')
fmts.add('presentation', 'pot', 'pot', 'Microsoft PowerPoint 97/2000/XP Template', 'MS PowerPoint 97 Vorlage')  # 3
fmts.add('presentation', 'ppm', 'ppm', 'Portable Pixelmap', 'impress_ppm_Export')  # 26
fmts.add('presentation', 'pptx', 'pptx', 'Microsoft PowerPoint 2007/2010 XML', 'Impress MS PowerPoint 2007 XML')  # 36
fmts.add('presentation', 'pps', 'pps', 'Microsoft PowerPoint 97/2000/XP (Autoplay)',
         'MS PowerPoint 97 Autoplay')  # 36
fmts.add('presentation', 'ppt', 'ppt', 'Microsoft PowerPoint 97/2000/XP', 'MS PowerPoint 97')  # 36
fmts.add('presentation', 'pwp', 'pwp', 'PlaceWare', 'placeware_Export')  # 30
fmts.add('presentation', 'ras', 'ras', 'Sun Raster Image', 'impress_ras_Export')  # 27
fmts.add('presentation', 'sda', 'sda', 'StarDraw 5.0 (OpenOffice.org Impress)', 'StarDraw 5.0 (StarImpress)')  # 8
fmts.add('presentation', 'sdd', 'sdd', 'StarImpress 5.0', 'StarImpress 5.0')  # 6
fmts.add('presentation', 'sdd3', 'sdd', 'StarDraw 3.0 (OpenOffice.org Impress)', 'StarDraw 3.0 (StarImpress)')  # 42
fmts.add('presentation', 'sdd4', 'sdd', 'StarImpress 4.0', 'StarImpress 4.0')  # 37
fmts.add('presentation', 'sxd', 'sxd', 'OpenOffice.org 1.0 Drawing (OpenOffice.org Impress)',
         'impress_StarOffice_XML_Draw')  # 31
fmts.add('presentation', 'sti', 'sti', 'OpenOffice.org 1.0 Presentation Template',
         'impress_StarOffice_XML_Impress_Template')  # 5
fmts.add('presentation', 'svg', 'svg', 'Scalable Vector Graphics', 'impress_svg_Export')  # 14
fmts.add('presentation', 'svm', 'svm', 'StarView Metafile', 'impress_svm_Export')  # 13
fmts.add('presentation', 'swf', 'swf', 'Macromedia Flash (SWF)', 'impress_flash_Export')  # 34
fmts.add('presentation', 'sxi', 'sxi', 'OpenOffice.org 1.0 Presentation', 'StarOffice XML (Impress)')  # 41
fmts.add('presentation', 'tiff', 'tiff', 'Tagged Image File Format', 'impress_tif_Export')  # 12
fmts.add('presentation', 'uop', 'uop', 'Unified Office Format presentation', 'UOF presentation')  # 4
fmts.add('presentation', 'vor', 'vor', 'StarImpress 5.0 Template', 'StarImpress 5.0 Vorlage')  # 40
fmts.add('presentation', 'vor3', 'vor', 'StarDraw 3.0 Template (OpenOffice.org Impress)',
         'StarDraw 3.0 Vorlage (StarImpress)')  # 1
fmts.add('presentation', 'vor4', 'vor', 'StarImpress 4.0 Template', 'StarImpress 4.0 Vorlage')  # 39
fmts.add('presentation', 'vor5', 'vor', 'StarDraw 5.0 Template (OpenOffice.org Impress)',
         'StarDraw 5.0 Vorlage (StarImpress)')  # 2
fmts.add('presentation', 'wmf', 'wmf', 'Windows Metafile', 'impress_wmf_Export')  # 11
fmts.add('presentation', 'xhtml', 'xml', 'XHTML', 'XHTML Impress File')  # 33
fmts.add('presentation', 'xpm', 'xpm', 'X PixMap', 'impress_xpm_Export')  # 10


class Options:
    def __init__(self):
        self.port = '8100'
        self.server = '127.0.0.1'
        self.connection = "socket,host=%s,port=%s;urp;StarOffice.ComponentContext" % (self.server, self.port)
        self.format = 'pdf'
        self.timeout = 15


class Convertor:
    ai_input = None
    _swf_output = None

    def __init__(self):
        global ooproc, office, product
        self.id = None
        self.errors = None
        self.group_id = 0
        self.canceled = 'no'
        self.format_id = ""
        self.file_id = ""
        self.source_id = ""
        self.source_ext = ""
        self.extension = ""
        self.code = ""
        self.asset_id = ""
        self.owner = ""
        self.input = ""
        self.output = ""

        unocontext = None
        # Do the LibreOffice component dance
        self.context = uno.getComponentContext()
        self.svcmgr = self.context.ServiceManager
        resolver = self.svcmgr.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", self.context)

        # Test for an existing connection
        # logger.info('Connection type: %s' % op.connection)
        try:
            unocontext = resolver.resolve("uno:%s" % op.connection)
        except NoConnectException as err:
            logger.info("Existing listener not found.")

            # Start our own OpenOffice instance
            logger.info("Launching our own listener using %s." % office.binary)
            try:
                prod = self.svcmgr.createInstance("com.sun.star.configuration.ConfigurationProvider")
                product = prod.createInstanceWithArguments("com.sun.star.configuration.ConfigurationAccess",
                                                           UnoProps(nodepath="/org.openoffice.Setup/Product"))
                if product.ooName != "LibreOffice" or LooseVersion(product.ooSetupVersion) <= LooseVersion('3.3'):
                    ooproc = subprocess.Popen([office.binary,
                                               "-headless",
                                               "-invisible",
                                               "-nocrashreport",
                                               "-nodefault",
                                               "-nofirststartwizard",
                                               "-nologo",
                                               "-norestore",
                                               "-accept=%s" % op.connection],
                                              env=os.environ)
                else:
                    ooproc = subprocess.Popen([office.binary,
                                               "--headless",
                                               "--invisible",
                                               "--nocrashreport",
                                               "--nodefault",
                                               "--nofirststartwizard",
                                               "--nologo",
                                               "--norestore",
                                               "--accept=%s" % op.connection],
                                              env=os.environ)

                logger.info('%s listener successfully started. (pid=%s)' % (product.ooName, ooproc.pid))

                # Try connection to it for op.timeout seconds (flakky OpenOffice)
                timeout = 0
                while timeout <= op.timeout:
                    # Is it already/still running ?
                    retcode = ooproc.poll()
                    if retcode is not None:
                        logger.info("Process %s (pid=%s) exited with %s." % (office.binary, ooproc.pid, retcode))
                        break
                    try:
                        unocontext = resolver.resolve("uno:%s" % op.connection)
                        break
                    except NoConnectException:
                        time.sleep(0.5)
                        timeout += 0.5
                    except:
                        raise
                else:
                    logger.error("Failed to connect to %s (pid=%s) in %d seconds.\n%s" % (
                        office.binary, ooproc.pid, op.timeout, err))
            except Exception as err:
                logger.error("Launch of %s failed.\n%s" % (office.binary, err))
                raise

        if not unocontext:
            die(251, "Unable to connect or start own listener. Aborting.")

        # And some more LibreOffice magic
        unosvcmgr = unocontext.ServiceManager
        self.desktop = unosvcmgr.createInstanceWithContext("com.sun.star.frame.Desktop", unocontext)
        self.cwd = unohelper.systemPathToFileUrl(os.getcwd())

        if not self.get_fv_data():
            logger.info('GETTING_DATA_EC_' + str(int(exitcode / 10000)))
            return

    def get_fv_data(self):
        global exitcode
        sql = """
            SELECT
                fv.*,
                fv2.id as source_id,
                fv2.extension as source_ext,
                fo.id as formatid,
                a.code,
                a.id as asset_id,
                a.owner,
                u.group
            FROM
                files_versions fv
            LEFT JOIN
                files_versions fv2 ON fv2.file_id = fv.file_id AND fv2.source = 'yes' AND fv2.status = 'available'
            LEFT JOIN
                files f ON f.id = fv.file_id
            LEFT JOIN
                assets a ON a.id = f.asset_id
            LEFT JOIN
                users u ON u.id = a.owner
            LEFT JOIN
                formats fo ON fo.id = fv.format_id
            WHERE
                f.type = 'document'
                AND
                fv.engine = 'oxobox'
                AND
                fv.status = 'queued'
            ORDER BY
                fv2.size ASC,
                play_default ASC,
                fv.id ASC
        """
        query = db.select(sql)

        if query:
            if query['source_id'] is None:
                exitcode = 90635
                return False

            self.source_id = query['source_id']
            self.source_ext = query['source_ext']
            self.id = query['id']
            self.format_id = query['formatid']
            self.file_id = query['file_id']
            self.extension = query['extension']
            self.code = query['code']
            self.asset_id = query['asset_id']
            self.owner = query['owner']
            self.group_id = query['group']
            self.input = Config.ASSET_FOLDER % (self.group_id, self.code)
            self.output = Config.ASSET_FOLDER % (self.group_id, self.code)

            if self.source_ext == 'ai':
                self.input += str(self.source_id) + '.pdf'
                self.ai_input = Config.ASSET_FOLDER % (self.group_id, self.code) + str(
                    self.source_id) + '.' + self.source_ext
                shutil.copy(self.ai_input, self.input)
            else:
                self.input += str(self.source_id) + '.' + self.source_ext

            if self.extension == 'swf':
                self.output += 'encoding-' + str(self.id) + '.pdf'
                self._swf_output = Config.ASSET_FOLDER % (self.group_id, self.code) + "%s.swf" % str(self.id)
            else:
                self.output += str(self.id) + '.' + self.extension

            if not os.path.exists(self.input):
                exitcode = 10665
                return False

            # if self.source_ext == 'zip':
            # self.input = ZipRar.zip_to_txt(self.input)
            #     if self.input == 'notzip':
            #         exitcode = 110671
            #         return False

            # if self.source_ext == 'rar':
            #     self.input = ZipRar.rar_to_txt(self.input)
            #     if self.input == 'notrar':
            #         exitcode = 120677
            #         return False

            logger.info(self.output)

            return True

        exitcode = 180684
        return False

    def get_format(self):
        doctype = None

        outputfmt = fmts.byname(op.format)

        if not outputfmt:
            outputfmt = fmts.byextension(os.extsep + op.format)

        if outputfmt:
            inputext = os.path.splitext(self.input)[1]
            inputfmt = fmts.byextension(inputext)
            if inputfmt:
                for fmt in outputfmt:
                    if inputfmt[0].doctype == fmt.doctype:
                        doctype = inputfmt[0].doctype
                        outputfmt = fmt
                        break
                else:
                    outputfmt = outputfmt[0]
            else:
                outputfmt = outputfmt[0]

        if not outputfmt:
            if doctype:
                logger.error('DocEncoder: format [{}] is not known to DocEncoder.'.format(op.format))
            else:
                logger.error('DocEncoder: format [{}] is not known to DocEncoder.'.format(op.format))
            die(1)

        return outputfmt

    def convert(self):
        global exitcode
        logger.info("Start Encoding")
        self.update_status('encoding')
        outputfmt = self.get_format()
        logger.info('Input file: ' + self.input)
        if self.source_ext != 'pdf':
            try:
                # Import phase
                # phase = "import"
                # Load inputfile
                inputprops = UnoProps(Hidden=True, ReadOnly=True, UpdateDocMode=QUIET_UPDATE)
                inputurl = unohelper.systemPathToFileUrl(self.input)
                document = self.desktop.loadComponentFromURL(inputurl, "_blank", 0, inputprops)

                if not document:
                    raise UnoException("The document '%s' could not be opened." % inputurl, None)

                # Update document links
                #phase = "update-links"
                try:
                    document.updateLinks()
                except AttributeError:
                    # the document doesn't implement the XLinkUpdate interface
                    pass

                # Update document indexes
                #phase = "update-indexes"
                try:
                    document.refresh()
                    indexes = document.getDocumentIndexes()
                except AttributeError:
                    # the document doesn't implement the XRefreshable and/or
                    # XDocumentIndexesSupplier interfaces
                    pass
                else:
                    for i in range(0, indexes.getCount()):
                        indexes.getByIndex(i).update()

                logger.info("Selected output format: %s" % outputfmt)
                logger.info("Selected office filter: %s" % outputfmt.filter)
                logger.info("Used doctype: %s" % outputfmt.doctype)

                # Export phase
                #phase = "export"
                outputprops = UnoProps(FilterName=outputfmt.filter, OutputStream=OutputStream(), Overwrite=True)

                if outputfmt.filter == 'Text (encoded)':
                    outputprops += UnoProps(FilterOptions="76,LF")
                elif outputfmt.filter == 'Text':
                    outputprops += UnoProps(FilterOptions="76")
                elif outputfmt.filter == 'Text - txt - csv (StarCalc)':
                    outputprops += UnoProps(FilterOptions="44,34,76")

                ##OUTPUT
                outputurl = unohelper.systemPathToFileUrl(self.output)
                logger.info("Output file: %s" % self.output)
                try:
                    document.storeToURL(outputurl, tuple(outputprops))
                except IOException as err:
                    raise UnoException("Unable to store document to %s (ErrCode %d)\n\nProperties: %s" % (outputurl,
                                                                                                          err.ErrCode,
                                                                                                          outputprops),
                                       None)
                #phase = "dispose"
                document.dispose()
                document.close(True)
            except SystemError:
                exitcode = 10804
            except RuntimeException:
                exitcode = 60807
            except DisposedException:
                exitcode = 70810
            except IllegalArgumentException:
                exitcode = 80813
            except IOException:
                exitcode = 30816
            except CannotConvertException:
                exitcode = 40819
            except UnoException as err:
                print("ERRORRRRR: ", err)
                if hasattr(err, 'ErrCode'):
                    exitcode = 190824
                    pass
                if hasattr(err, 'Message'):
                    logger.error(err)
                    exitcode = 50828
                else:
                    exitcode = 20830
                    pass
        else:
            try:
                shutil.copy(self.input, self.output)
            except Exception as err:
                logger.error(err)
                exitcode = 150837
                pass

        if self.extension == 'swf':
            self.gen_swf()

        if exitcode == 0:
            self.file_exist()

        return

    def file_exist(self):
        global exitcode
        if exitcode == 0:
            if self.extension == 'swf':
                output = self._swf_output
            else:
                output = self.output
                if not os.path.exists(output):
                    exitcode = 130856
            if not os.path.exists(output):
                exitcode = 130858
        return

    def encoding_complete(self):
        logger.info("Encoding Completed")
        if self.extension == 'swf':
            output = self._swf_output
        else:
            output = self.output
        try:
            size = os.stat(output)[6]
        except:
            size = 0
        sql = ("UPDATE files_versions SET status = 'available', progress = 100, size = %(size)s, encode_end = NOW() "
               "WHERE id = %(id)s")
        args = {'id': self.id, 'size': size}
        db.update(sql, args)
        self.update_delivery_files()
        self.gen_thumb()
        return

    def gen_swf(self):
        global exitcode
        cmd = Config.pdf2swf_bin + " -s insertstop -s poly2bitmap -T9 %(input)s %(output)s"
        args = {'input': self.output, 'output': self._swf_output}
        command = shlex.split(cmd % args)
        logger.info(command)
        try:
            swf_creation = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = swf_creation.stdout.readlines()
            last_line = lines[len(lines) - 1]
            logger.info(lines)

            if 'ERROR' in last_line:
                exitcode = 100906

            if 'FATAL' in last_line:
                if 'PDF disallows copying':
                    exitcode = 160910
        except Exception as err:
            logger.error(err)
            exitcode = 100913
        return

    def gen_thumb(self):
        global exitcode
        self.update_thumb_status('generating')
        thumb_path = ''.join([Config.ASSET_FOLDER % (self.group_id, self.code), "thumbs/%s" % str(self.id)])
        try:
            os.makedirs(thumb_path)
        except:
            exitcode = 140927
            pass
        else:
            output = thumb_path + "/pic%04d.jpg"
            cmd = ''.join([Config.ASSET_FOLDER, " %(input)s %(output)s"])
            args = {'input': self.output, 'output': output}
            logger.info(cmd % args)
            command = shlex.split(cmd % args)
            thumb_creation = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = thumb_creation.stdout.readlines()
            if (len(lines) - 1) > 0:
                last_line = lines[len(lines) - 1]
            else:
                last_line = ""
            if 'error' in last_line:
                self.update_thumb_status('error')
                exitcode = 140945
            else:
                self.update_thumb_status('done')
        if self.extension == 'swf':
            os.remove(self.output)
        return

    def update_delivery_files(self):
        sql = ("SELECT df.id as dfid, dest.id as destid, dest.type FROM delivery_files df "
               "LEFT JOIN delivery_transfers dlt ON dlt.id = df.delivery_transfer "
               "LEFT JOIN destinies dest ON dest.id = dlt.destiny_id "
               "WHERE df.file_version = %(id)s")
        args = {'id': self.id}
        query = db.select(sql, args, fetch='all')
        if query:
            sql = "UPDATE delivery_files SET status = %(stat)s WHERE id = %(id)s"
            for q in query:
                args2 = {'stat': 'queued', 'id': q['dfid']}
                if q['type'] == 'web':
                    args2['stat'] = 'ready'
                db.update(sql, args2)
                try:
                    os.system(Config.exec_destiny % q['destid'])
                except:
                    pass

    def update_thumb_status(self, status):
        sql = "UPDATE files_versions SET thumb = %(status)s WHERE id = %(id)s"
        args = {'status': status, 'id': self.id}
        db.update(sql, args)

    def update_status(self, status, description=""):
        sql = """
            UPDATE
                files_versions
            SET
                status = %(status)s,
                error_description = %(error)s
            WHERE
                id = %(id)s
        """
        args = {'status': status, 'error': description, 'id': self.id}
        db.update(sql, args)
        return

    def report_errors(self):
        ec = int(exitcode / 10000)
        ln = exitcode % 10000
        if ec == 9:
            logger.error('[{}] {}'.format(ln, error_dict[ec]))
        else:
            logger.error("[{}] [{}] [{}] [{}] - {}".format(ln, self.group_id, self.id, self.code, error_dict[ec]))
        if ec != 18:
            self.update_status('error', error_dict[ec])
        return

    def __str__(self):
        return 'Encoder:\n\tId: {self.id}\n\tErrors: {self.errors}\n\tCanceled: {self.canceled}\n\t' \
               'Format_Id: {self.format_id}\n\tFile_Id: {self.file_id}\n\tSource_Id: {self.source_id}\n\t' \
               'Source_Ext: {self.source_ext}\n\tExt: {self.extension}\n\tCode: {self.code}\n\t' \
               'Asset_Id: {self.asset_id}\n\tOwner: {self.owner}\n\tInput: {self.input}\n\t' \
               'Output: {self.output}'.format(self=self)


def die(ret, msg=None):
    global convertor, ooproc

    if msg:
        logger.error('Error: %s' % msg)

    # Did we start our own listener instance ?
    if ooproc is not None:
        # If there is no GUI attached to the instance, terminate instance
        logger.info('Terminating LOffice instance.')
        if convertor is not None:
            try:
                convertor.desktop.terminate()
            except DisposedException:
                logger.info('LOffice instance unsuccessfully closed, sending TERM signal.')

        # LibreOffice processes may get stuck and we have to kill them
        # Is it still running ?
        if ooproc.poll() is None:
            logger.info('LOffice instance triying to terminate it, sending KILL signal.')
            try:
                ooproc.kill()
            except AttributeError:
                os.kill(ooproc.pid, signal.SIGKILL)
            logger.info('Waiting for LOffice with pid {} to disappear.'.format(ooproc.pid))
            ooproc.wait()

    # allow Python GC to garbage collect pyuno object *before* exit call
    # which avoids random segmentation faults --vpa
    convertor = None

    sys.exit(ret)


def main():
    global convertor, exitcode
    convertor = None
    try:
        while True:
            exitcode = 0
            convertor = Convertor()
            logger.info(convertor.__str__())

            if not convertor.id or exitcode != 0:
                convertor.report_errors()
                break

            if exitcode == 0:
                convertor.convert()

            if exitcode == 0:
                convertor.encoding_complete()
            else:
                if convertor.extension == 'swf':
                    try:
                        os.remove(convertor.output)
                    except:
                        pass

                convertor.report_errors()

            if convertor.extension == 'ai':
                logger.info("REMOVE: " + convertor.input)

    except NoConnectException as err:
        logger.error("DocEncoder: could not find an existing connection to LibreOffice at %s:%s. (%s)" % (op.server,
                                                                                                          op.port,
                                                                                                          err))
    except OSError:
        logger.error("Warning: failed to launch Office suite. Aborting.")
    except Exception as err:
        logger.error(err)


if __name__ == '__main__':
    set_logger()
    myApp = SingleInstance(Config.document_encoder)

    if myApp.already_running():
        logger.info("# Ya hay un docConverter")
        sys.exit(0)
    else:
        logger.info("# Disparo el docConverter")

    kill_all_soffice()

    for of in find_offices():
        if of.python != sys.executable and not sys.executable.startswith(of.basepath):
            python_switch(of)
        office_environ(of)
        try:
            import uno, unohelper
            office = of
            break
        except Exception as e:
            logger.error("Cannot find a suitable pyuno library and python binary combination in %s" % of)
            logger.error("ERROR:" + str(sys.exc_info()[1]))
    else:
        logger.error("Cannot find a suitable office installation on your system.")
        sys.exit(1)

    from com.sun.star.beans import PropertyValue
    from com.sun.star.connection import NoConnectException
    from com.sun.star.document.UpdateDocMode import QUIET_UPDATE
    from com.sun.star.lang import DisposedException, IllegalArgumentException
    from com.sun.star.io import IOException, XOutputStream
    from com.sun.star.script import CannotConvertException
    from com.sun.star.uno import Exception as UnoException
    from com.sun.star.uno import RuntimeException

    class OutputStream(unohelper.Base, XOutputStream):
        def __init__(self):
            self.closed = 0

        def close_output(self):
            self.closed = 1

        @staticmethod
        def write_bytes(seq):
            sys.stdout.write(seq.value)

        def flush(self):
            pass

    def UnoProps(**args):
        props = []
        for key in args:
            prop = PropertyValue()
            prop.Name = key
            prop.Value = args[key]
            props.append(prop)

        return tuple(props)

    op = Options()
    db = DataBase()

    try:
        main()
    except KeyboardInterrupt as e:
        die(6, 'Exiting on user request')
    except Exception as e:
        type_, value_, traceback_ = sys.exc_info()
        logger.info(''.join(traceback.format_tb(traceback_)))
        die(7, 'Existing on ' + e.__str__())
    die(exitcode)