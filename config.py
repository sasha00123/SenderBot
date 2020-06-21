import os
from playhouse.db_url import connect


TOKEN = os.environ.get('TOKEN', '')
TOKEN2 = os.environ.get('TOKEN_MAIN', '')

USE_SENDLIST = bool(int(os.environ.get('USE_SENDLIST', '0')))
USE_WEBHOOK = bool(int(os.environ.get('USE_WEBHOOK', '0')))

PORT = int(os.environ.get('PORT', '8443'))
SEND_LIST_URL = os.environ.get('SEND_LIST_URL')

ADMINS = list(map(int, os.environ.get('ADMINS', '').split(',')))
DATABASE = connect(os.environ.get('DATABASE_URL'), autocommit=True, autorollback=True)

APPLICATION_NAME = os.environ.get('HEROKU_APP_NAME')
