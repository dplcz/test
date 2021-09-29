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


class Data(BaseModel):
    id = IntegerField(primary_key=True)
    url = TextField(default='')
    content = TextField(default='')
    primary = TextField(default='')
    needs = TextField(default='')
    place = TextField(default='')
    company = TextField(default='')
    welfare = TextField(default='')


if __name__ == '__main__':
    db.create_tables([Data])
