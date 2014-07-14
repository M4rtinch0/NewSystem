import os
#import commands
import subprocess

class SingleInstance(object):
    """
    Se encarga de que este corriendo un solo encoder por grupo para cada tipo de archivo.
    Crea un archivo .pid cuando la aplicacion esta corriendo, que se borra cuando se termina la ejecucion de la misma.
    """
    def __init__(self, proc):
        proc = proc.split('/')[-1]
        self.pidPath = '/tmp/' + proc + '.pid'
        #Chequea si existe el archivo .pid, si existe quiere decir que la aplicacion esta corriendo, sino lo crea.
        if os.path.exists(self.pidPath):
            #pid = open(self.pidPath, 'r').read().strip()
            #pidRunning = subprocess.check_output(['ls', '/proc', '|', 'grep', '-e', '^' + pid + '$'])
            #Si existe el archivo pero no esta corriendo la aplicacion lasterror es FALSE.
            #if pidRunning:
            #    self.lasterror = True
            #else:
            #    self.lasterror = False
            self.lasterror = True
        else:
            self.lasterror = False

        if not self.lasterror:
            fp = open(self.pidPath, 'w')
            fp.write(str(os.getpid()))
            fp.close()

    def alreadyRunning(self):
        """ Devuelve si esta corriendo la aplicacions (True) o no (False). """
        return self.lasterror

    def __del__(self):
        """ Borra el archivo .pid cuando el objeto SingleInstance se termina por algun motivo. """
        if not self.lasterror:
            os.unlink(self.pidPath)