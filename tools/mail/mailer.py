#!/usr/bin/python -u
# -*- coding: utf-8 -*-
# ___                            _
#|_ _|_ __ ___  _ __   ___  _ __| |_ ___
# | || '_ ` _ \| '_ \ / _ \| '__| __/ __|
# | || | | | | | |_) | (_) | |  | |_\__ \
#|___|_| |_| |_| .__/ \___/|_|   \__|___/
#              |_|
import re
import sys
import smtplib
sys.path.append('/oxobox/engine/tools/mail/_classes')
import Config
import DataBase
import SingleInstance
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
_debugger = Config.createDebug(Config.LOG_FOLDER + 'Mailer.log', 'Mailer')
#  ____ _
# / ___| | __ _ ___  ___  ___
#| |   | |/ _` / __|/ _ \/ __|
#| |___| | (_| \__ \  __/\__ \
# \____|_|\__,_|___/\___||___/
#
class Email:

    _From = "Oxobox <noreply@oxobox.tv>"
    _smtpServer= "localhost"

    def __init__(self):
        self.id = None
        self._textBody  = None
        self._htmlBody  = None
        self._subject   = ""
        self._reEmail   = re.compile("^([\\w \\._]+\\<[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\>|[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)$")
        self.setFrom(self._From)
        self.clearRecipients()

        sql = """SELECT id, `to`, subject, plaintext, html FROM mails m WHERE m.status = 'queue' ORDER BY id LIMIT 1 """

        query = mysql.select(sql)

        if query:
            self.id = query['id']
            subject = query['subject']
            text = query['plaintext']
            html = query['html']
            self.addRecipient(query['to'])
            self.setSubject(subject)
            self.setTextBody(text)
            self.setHtmlBody(html)
        return

    def send(self):
        _debugger.info("Enviando")
        sql = """
                UPDATE
                        mails
                SET
                        status = 'sending'
                WHERE
                        id = %(id)s
        """
        args = {
                'id'            : self.id,
        }
        mysql.update(sql, args)
        if self._textBody is None and self._htmlBody is None:
            _debugger.error("Must specify at least one body type (HTML or Text)")
            sys.exit()
        if len(self._to) == 0:
            _debugger.error("Must specify at least one recipient")
            sys.exit()

        if self._textBody is not None and self._htmlBody is None:
            msg = MIMEText(self._textBody, "plain")
        elif self._textBody is None and self._htmlBody is not None:
            msg = MIMEText(self._htmlBody, "html")
        else:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(self._textBody, "plain"))
            msg.attach(MIMEText(self._htmlBody, "html"))

        msg['Subject'] = self._subject
        msg['From'] = self._from
        msg['To'] = ", ".join(self._to)
        msg.preamble = "You need a MIME enabled mail reader to see this message"
        _debugger.info(msg)
        msg = msg.as_string()
        server = smtplib.SMTP(self._smtpServer)
        server.sendmail(self._from, self._to, msg)
        server.close()
        self.sent()

    def sent(self):
        _debugger.info("Email enviado")
        sql = """
                UPDATE
                        mails
                SET
                        status = 'sent'
                WHERE
                        id = %(id)s
        """
        args = {
                'id'            : self.id,
        }
        mysql.update(sql, args)
        return

    def setSubject(self, subject):
        self._subject = subject

    def setFrom(self, address):
        #if not self.validateEmailAddress(address):
        #       _debugger.error("Invalid email address '%s'" % address)
        #       sys.exit()
        self._from = address

    def clearRecipients(self):
        self._to = []

    def addRecipient(self, address):
        #if not self.validateEmailAddress(address):
        #       _debugger.error("Invalid email address '%s'" % address)
        #       sys.exit()
        self._to.append(address)

    def setTextBody(self, body):
        self._textBody = body

    def setHtmlBody(self, body):
        self._htmlBody = body

    def validateEmailAddress(self, address):
        if self._reEmail.search(address) is None:
            return False
        return True
# __  __       _
#|  \/  | __ _(_)_ __
#| |\/| |/ _` | | '_ \
#| |  | | (_| | | | | |
#|_|  |_|\__,_|_|_| |_|
#
def main():
    global mysql, mail
    myApp = SingleInstance.SingleInstance(Config.mailSender)

    if myApp.already_running():
        _debugger.info("### Ya hay un mailSender")
        sys.exit(0)
    else:
        _debugger.info("### Disparo el mailSender")

    mysql = DataBase.DataBase()

    while True:
        mail = Email()
        _debugger.info("MAIL: %s"%mail.__dict__)

        if not mail.id:
            break

        mail.send()

    sys.exit(0)

if __name__ == '__main__':
    main()

