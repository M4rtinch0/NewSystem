import sys
import Config
import MySQLdb #@UnresolvedImport
_logging = Config.createLog(Config.LOG_FOLDER + 'Filemanager.log', 'MySQL')
_debugger = Config.createDebug(Config.LOG_FOLDER + 'Debug.log', 'MySQLD')
"""
Clase de Base de datos.
"""
class DataBase:
    def connect_mysql(self):
        """
        Establece la conexion con la base de datos con los parametros MYSQL_USER, MYSQL_PASS y MYSQL_DB que se definen en Config.py
        """
        try:
            self.db = MySQLdb.connect("localhost", Config.MYSQL_USER, Config.MYSQL_PASS, Config.MYSQL_DB)
        except Exception as e:
            _debugger.critical("No puedo acceder a la base de datos.")
            _debugger.critical(e)
            _logging.critical("No puedo acceder a la base de datos.")

            sys.exit()

    def select(self, sql, args=None, fetch='one', cursorType='dict',userId=None):
        """
        Realiza los SELECTS con el query que le pasamos.
            sql                     -- Query a consultar
            args            -- Argumentos para reemplazar en el SQL
            fetch           -- Devolver de a un ROW o todos los ROW juntos
            cursorType      -- Retorna los datos en forma de diccionario o como lista.

        Devuelve la DATA del select
        """
        self.connect_mysql()
        data = None
        if args is not None:
            execute = sql%args
        else:
            execute = sql

        if cursorType == 'dict':
            cursor = self.db.cursor(MySQLdb.cursors.DictCursor)
        else:
            cursor = self.db.cursor()

        try:
            if userId is not None:
                cursor.execute("SET @user_id = " + str(userId))
            cursor.execute(sql,args)
        except Exception as e:
            _logging.error("[%s] %s",e,execute)
            _debugger.error("[%s] %s",e,execute)
            self.db.close()
        else:
            if fetch == 'one':
                data = cursor.fetchone()
            else:
                data = cursor.fetchall()

            self.db.close()

        return data

    def update(self, sql, args=None, userId=None):
        """
        Realiza los UPDATES con el query que le pasamos.
            sql     -- Query a realizar
            args    -- Argumentos para reemplazar en el SQL
        """
        self.connect_mysql()
        cursor = self.db.cursor()
        if args is not None:
            execute = sql%args
            _debugger.info(sql%args)
        else:
            execute = sql
            _debugger.info(sql)
        try:
            if userId is not None:
                cursor.execute("SET @user_id = " + str(userId))
            cursor.execute(sql, args)
        except Exception as e:
            _logging.error("MYSQL UPDATE ERROR: %s (%s)"%(e,execute))
            _debugger.error("MYSQL UPDATE ERROR: %s (%s)"%(e,execute))
            self.db.close()
        else:
            self.db.commit()
            self.db.close()

    def insertInto(self, sql, args, userId=None):
        """
        Realiza los INSERTS con el query que le pasamos.
            sql     -- Query a realizar
            args    -- Argumentos para reemplazar en el SQL

        Devuelve el ID del insert
        """
        self.connect_mysql()
        cursor = self.db.cursor()
        execute = sql%args
        try:
            if userId is not None:
                cursor.execute("SET @user_id = " + str(userId))
            cursor.execute(sql,args)
        except Exception as e:
            _logging.error("MYSQL INSERT ERROR: %s (%s)"%(e,execute))
            _debugger.error("MYSQL INSERT ERROR: %s (%s)"%(e,execute))
            self.db.close()
            return 0
        else:
            id = int(cursor.lastrowid)
            self.db.commit()
            self.db.close()
            return id

    def _checkFileCode(self, code):
        """
        Valida si el codigo ya esta asociado a un asset o se puede utilizar.
        code -- Codigo para chequear
        """
        #Chequeo codigo de asset
        sql = """
            SELECT
                id
            FROM
                files
            WHERE
                code = %(code)s
        """
        args = {'code': code}
        data = self.select(sql, args, 'one', 'normal')
        if data:
            return 1
        return 0

    def _checkCatCode(self, code):
        """
        Valida si el codigo ya esta asociado a un category o se puede utilizar.
            code -- Codigo para chequear
        """
        #Chequeo codigo de asset
        sql = """
            SELECT
                id
            FROM
                categories
            WHERE
                code = %(code)s
        """
        args = {'code': code}
        data = self.select(sql, args, 'one', 'normal')
        if data:
            return 1
        return 0

    def _checkCode(self, code):
        """
        Valida si el codigo ya esta asociado a un asset o se puede utilizar.
            code -- Codigo para chequear

        Devuelve 1 si el codigo ya existe, 0 si no.
        """
        #Chequeo codigo de asset
        sql = """
            SELECT
                id
            FROM
                assets
            WHERE
                code = %(code)s
        """
        args = {'code': code}
        #Chequeo codigo de grupo
        data = self.select(sql, args, 'one', 'normal')
        sql = """
            SELECT
                id
            FROM
                groups
            WHERE
                name = %(code)s
        """
        args = {'code': code}
        data2 = self.select(sql, args, 'one', 'normal')

        if data:
            return 1

        if data2:
            return 1

        return 0

    def restoreTalliesBytes(self, source, user):
        """
        Si el archivo es subido a un inbox, este se mueve de lugar a la carpeta del asset entonces hay que restaurar cuota del FTP restandole el peso del archivo.
            source  -- Objeto FileManager que tiene un atributo que es el peso del archivo SOURCE.
            user    -- Objeto User
        """
        sql = """
            UPDATE
                qtallies
            SET
                bytes_in_used = bytes_in_used - %(size)s
            WHERE
                name = (SELECT `name` FROM `groups` WHERE id = %(gid)s)
        """
        args = {'size': source.size_bytes, 'gid': user.group_id}
        self.update(sql, args)
        sql = """
            SELECT
                bytes_in_used
            FROM
                qtallies
            WHERE
                name LIKE (SELECT `name` FROM `groups` WHERE id = %(gid)s)
        """
        args = {'gid': user.group_id}
        data = self.select(sql, args)

        if data['bytes_in_used'] < 0:
            sql = """
                UPDATE
                    qtallies
                SET
                    bytes_in_used = 0
                WHERE
                    name LIKE (SELECT `name` FROM `groups` WHERE id = %(gid)s)
            """
            args = {'gid': user.group_id}
            self.update(sql, args)

    def report_errors(self, group_id, id, code, errors, canceled='no'):
        """
        Reporta todos los errores que pudiesen ocurrir en el proceso de creacion del asset, file y versiones y el posterior encodeo de las mismas.
            group_id        -- ID del grupo al que pertenece el usuario UPLOADER.
            id                      -- ID de base de datos del file_version
            code            -- Codigo del asset
            errors          -- Codigo de ERROR
            canceled        -- Indica si el encodeo fue cancelado
        """

        _logging.error("[%s] [%s] [%s] - ENCODER ERRORS: %s", group_id, id, code, errors)
        _debugger.error("[%s] [%s] [%s] - ENCODER ERRORS: %s", group_id, id, code, errors)

        if canceled == 'no':
            sql = """
                UPDATE
                    files_versions
                SET
                    status = 'error',
                    error_description = %(error)s
                WHERE
                    id = %(id)s
            """
        else:
            sql = """
                UPDATE
                    files_versions
                SET
                    error_description = %(error)s
                WHERE
                    id = %(id)s
            """
        args = {'error': errors, 'id': id}
        self.update(sql, args)
        return

    def userCanIngest(self, user_id):
        return 1