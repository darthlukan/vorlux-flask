#!/usr/bin/env python

from ConfigParser import SafeConfigParser


secrets = SafeConfigParser()
secrets.read('secrets.ini')

MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 587
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = secrets.get("Mail", "USERNAME")
MAIL_PASSWORD = secrets.get("Mail", "PASSWORD")

ADMINS = ['support@vorluxhosting.com', 'anakin@vorluxhosting.com']
