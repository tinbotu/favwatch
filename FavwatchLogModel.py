# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 sts=4 ff=unix ft=python expandtab

import datetime
from peewee import *

favwatch_log = Proxy()


class BaseModel(Model):
    class Meta:
        database = favwatch_log


class FavLog(BaseModel):
    fav_by_screen_name = TextField()
    fav_rough_seen = DateTimeField(default=datetime.datetime.now)

    screen_name = TextField(null=True)
    name = TextField(null=True)
    id_str = TextField(null=False, index=True)
    text = TextField(null=True)
    fav_created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'log'
        indexes = (
            (('screen_name', 'id_str'), False),
        )
