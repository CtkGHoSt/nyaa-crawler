# -*- coding:utf-8 -*-

from peewee import *
import datetime

db = SqliteDatabase('nyaa.db')
db.connect()

class nyaa_magnet(Model):
    magnet = CharField(primary_key=True)
    title = CharField()
    size = CharField()
    upload_time = DateTimeField()
    seeders = IntegerField()
    downloaders = IntegerField(null=True)
    comleted = IntegerField(null=True)
    download = BooleanField(default=False)
    gentime = DateTimeField(default=datetime.datetime.now())
    
    class Meta:
        database = db

class task_by_crawler(Model):
    magnet = ForeignKeyField(nyaa_magnet)
    gentime = DateTimeField(default=datetime.datetime.now())
    status = CharField(default='waiting')# 任务状态 active | waiting | paused | error | complete | removed
    gid = CharField()# 下载任务的gid
    class Meta:
        database = db

if __name__ == '__main__':
    db.create_tables([nyaa_magnet, task_by_crawler])
