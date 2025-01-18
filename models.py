from flask_login import UserMixin
from mongoengine import *


class User(Document, UserMixin):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    admin = BooleanField(required=True, default=False)

    # `UserMixin` provides the required attributes and methods:
    # is_authenticated
    # is_active
    # is_anonymous
    # get_id()


class ProcessedFile(Document):
    filename = StringField(required=True, unique=True)


class Log(Document):
    record_type = StringField(required=True)
    call_type = StringField(required=False, default=' ')
    emergency = StringField(required=False)
    calling_id = IntField(required=True)
    called_id = IntField(required=True)
    date = DateField(required=True)
    talk_time = StringField(required=False, default=' ')
    cause = StringField(required=False)
    direction = StringField(required=False, default=' ')
    channel = StringField(required=False)
    site = IntField(required=True)
    time = StringField(required=True)
