import boto
import logging
from .DataBase import db
from boto.s3.key import Key
from .Config import file_path
from .Tools import file_exist, get_file_name


class BotoS3:
    logger = logging.getLogger('Debug.BotoS3')

    def __init__(self, data=None):
        """ Crea el MySQL guarda el fileversion y toma los datos necesarios para enviar a AMAZON. """
        self.found = False
        self.error = False
        self.connection = None
        self.bucket = None
        self.key = None
        print(data)
        if data is not None:
            if type(data) is int or type(data) is str:
                sql = ("SELECT fv.id as fv_id, fv.extension, fv.upload_to_s3, fv.s3_status, "
                       "a.id as asset_id, a.code, i.group, g.s3_bucket, g.s3_access_key, "
                       "g.s3_secret_key, u.id as user_id "
                       "FROM files_versions fv "
                       "LEFT JOIN files f ON f.id = fv.file_id "
                       "LEFT JOIN assets a ON a.id = f.asset_id "
                       "LEFT JOIN users u ON u.id = a.owner "
                       "LEFT JOIN inboxes i ON i.id = a.inbox "
                       "LEFT JOIN groups g ON g.id = i.group "
                       "WHERE fv.id = {} AND fv.s3_status = 'queue'")
                query = db.select(sql.format(data))
                print(query)
                if query is None:
                    return
                data = query

            if data is not None:
                self.fv_id = data['fv_id']
                self.extension = data['extension']
                self.upload_to_s3 = data['upload_to_s3']
                self.s3_status = data['s3_status']
                self.asset_id = data['asset_id']
                self.asset_code = data['code']
                self.group = data['group']
                self.s3_bucket = data['s3_bucket']
                self.s3_access_key = data['s3_access_key']
                self.s3_secret_key = data['s3_secret_key']
                self.user_id = data['user_id']
                self.source = file_path.format(self.group, self.asset_code, self.fv_id, self.extension)

    def connect(self):
        try:
            #Nos conectamos a S3
            self.connection = boto.connect_s3(self.s3_access_key, self.s3_secret_key)
            self.bucket = self.connection.get_bucket(self.s3_bucket)
            if not file_exist(self.source):
                self.logger.error("Source {!r} is not found.".format(self.source))
                self.error = 'error'
                return

            tail = get_file_name(self.source)
            self.key = self.asset_code + "/" + tail
            self.logger.debug("{} | Source {} | Key {}".format(self.bucket, self.source, self.key))
        except Exception as responce:
            self.logger.error("BosoS3 Error: ".format(responce))
            self.error = 'error'

    def start(self):
        self.update_s3_status('uploading')
        if self.upload_to_s3 == 'yes':
            try:
                k = Key(self.bucket)
                k.key = self.key
                k.set_contents_from_filename(
                    self.source,
                    cb=self.progress_callback,
                    num_cb=100,
                )
                k.make_public()
            except Exception as responce:
                self.logger.error("BosoS3 Error: {}".format(responce))
                self.error = 'error'

    def progress_callback(self, current, total):
        try:
            perc = current * 100 / float(total)
            self.logger("BotoS3 Progress ({}): {0:.2f}%".format(self.fv_id, perc))
        except Exception as responce:
            self.logger("BotoS3 Progress Error: {}%".format(responce))

    def complete(self):
        if self.error is not None:
            status = 'error'
        else:
            status = 'complete'
        self.update_s3_status(status)

    def send(self):
        """
        Maneja el envio al repositorio.
        """
        self.connect()
        if self.error is None:
            self.start()
        self.complete()
        #self.logger.info('>>> Completed exiting: [{}]', self.fv_id)

    def update_s3_status(self, status):
        """
        Actualiza el estado de s3_status del FileVersion.

        :type status: string
        :param status: Estado en el que se encuentra el envio al S3
        """
        sql = "UPDATE files_versions SET s3_status = {!r} WHERE id = {}"
        db.update(sql.format(status, self.fv_id))