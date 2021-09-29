from peewee import *

db = MySQLDatabase('spider', host='localhost', port=3306, user='root', password='dp20020620')


class BaseModel(Model):
    class Meta:
        database = db


'''
TIPS:

CharField需要设置长度
TextField允许任意长度
设计表时，经量对采集到的数据进行格式化处理
default和null是否为True
'''


class Topic(BaseModel):
    url = TextField(default='')
    title = CharField(default='')


class Passage(BaseModel):
    id = CharField(primary_key=True)
    url = TextField(default='')
    content = TextField(default='')
    author = CharField()
    answer_num = IntegerField(default=0)
    latest_time = DateTimeField()


if __name__ == '__main__':
    db.create_tables([Topic, Passage])
