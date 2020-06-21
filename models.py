import peewee
from config import *


class BaseModel(peewee.Model):
    class Meta:
        database = DATABASE


class MainMessage(BaseModel):
    chat_id = peewee.BigIntegerField(index=True)
    message_id = peewee.BigIntegerField(index=True)


class SentMessage(BaseModel):
    message_id = peewee.BigIntegerField()
    chat_id = peewee.BigIntegerField()
    main_message = peewee.ForeignKeyField(MainMessage, backref="sent_messages")
