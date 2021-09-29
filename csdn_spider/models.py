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
    title = CharField()
    # TextField允许任意长度字符串
    # 若获取不到，则返回''
    content = TextField(default='')
    id = IntegerField(primary_key=True)
    author = CharField()
    creat_time = DateTimeField()
    # 若获取不到，则返回0
    answer_num = IntegerField(default=0)
    click_num = IntegerField(default=0)
    # 采纳率
    cnl = FloatField(default=0.0)
    # 报酬
    score = IntegerField(default=0)
    status = CharField()


class Answer(BaseModel):
    topic_id = IntegerField()
    author = CharField()
    content = TextField(default='')
    created_time = DateTimeField()
    # 点赞数
    parised_num = IntegerField(default=0)


class Author(BaseModel):
    name = CharField()
    id = CharField(primary_key=True)
    click_num = IntegerField(default=0)
    # 原创数
    original_num = IntegerField(default=0)
    # 排名
    rate = IntegerField(default=-1)
    # 评论数
    answer_num = IntegerField(default=0)
    # 获赞数
    parised_num = IntegerField(default=0)
    # 个人介绍
    industry = CharField(null=True)
    # 粉丝数
    follower_num = IntegerField(default=0)
    # 关注数
    following_num = IntegerField(default=0)


if __name__ == '__main__':
    db.create_tables([Topic, Answer, Author])
