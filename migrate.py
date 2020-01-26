import peewee
from models import *
from config import DATABASE

DATABASE.create_tables([MainMessage, SentMessage])
