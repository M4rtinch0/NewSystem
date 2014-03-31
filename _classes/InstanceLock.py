# -*- coding: utf-8 -*-
# Name:         InstanceLock
# Purpose:      Lockfile para detectar instancias previas de la app
#
# Author:       Pela
#
# Created:      11/03/2013
# Copyright:    (c) Pela 2013
# flock.py
import os
import socket
import logging


class Ilock(object):
    """
    Class to handle creating and removing (pid) lockfiles
    """

    logger = logging.getLogger('Debug.ILock')

    # custom exceptions
    class FileLockAcquisitionError(Exception):
        pass

    class FileLockReleaseError(Exception):
        pass

    # convenience callables for formatting
    addr = lambda self: '{}@{}'.format(self.pid, self.host)
    fddr = lambda self: '<{} {}>'.format(self.path, self.addr())
    pddr = lambda self, lock: '<{} {}@{}>'.format(self.path, lock['pid'], lock['host'])

    def __init__(self, path):
        self.pid = os.getpid()
        self.host = socket.gethostname()
        self.path = path

    def acquire(self):
        """
        Acquire a lock, returning self if successful, False otherwise
        """
        if self.islocked():
            lock = self._readlock()
            self.logger.info('Previous lock detected: %s' % self.pddr(lock))
            return False
        try:
            fh = open(self.path, 'w')
            fh.write(self.addr())
            fh.close()
            self.logger.info('Acquired lock: %s' % self.fddr())
        except:
            if os.path.isfile(self.path):
                try:
                    os.unlink(self.path)
                except:
                    pass
            raise (self.FileLockAcquisitionError, 'Error acquiring lock: %s' % self.fddr())
        return self

    def release(self):
        """
        Release lock, returning self
        """
        if self.ownlock():
            try:
                os.unlink(self.path)
                self.logger.info('Released lock: %s' % self.fddr())
            except:
                raise (self.FileLockReleaseError, 'Error releasing lock: %s' % self.fddr())
        return self

    def _readlock(self):
        """
        Internal method to read lock info
        """
        try:
            lock = {}
            fh = open(self.path)
            data = fh.read().rstrip().split('@')
            fh.close()
            lock['pid'], lock['host'] = data
            return lock
        except:
            return {'pid': 8 ** 10, 'host': ''}

    def islocked(self):
        """
        Check if we already have a lock
        """
        try:
            lock = self._readlock()
            os.kill(int(lock['pid']), 0)
            return lock['host'] == self.host
        except:
            return False

    def ownlock(self):
        """
        Check if we own the lock
        """
        lock = self._readlock()
        return self.fddr() == self.pddr(lock)

    def __del__(self):
        """
        Magic method to clean up lock when program exits
        """
        self.release()