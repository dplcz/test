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


class Goods(BaseModel):
    id = BigIntegerField(primary_key=True)
    name = CharField(max_length=500)
    # content = TextField(default='')
    price = FloatField(verbose_name='价格')
    # 供应商
    supplier = CharField(max_length=500, verbose_name='供应商')
    # verbose_name可以理解为注释
    size_box = TextField(default='', verbose_name='规格和包装')
    image_list = TextField(default='', verbose_name='商品轮播图')

    comment_num = CharField(default=0, verbose_name='评论数')
    image_comment_num = CharField(default=0, verbose_name='晒图数')
    video_comment_num = CharField(default=0, verbose_name='视频数')
    add_comment_num = CharField(default=0, verbose_name='追评数')
    good_comment_num = CharField(default=0, verbose_name='好评数')
    mid_comment_num = CharField(default=0, verbose_name='中评数')
    bad_comment_num = CharField(default=0, verbose_name='差评数')


class GoodsEvaluate(BaseModel):
    id = IntegerField(primary_key=True)
    # 外键
    goods = ForeignKeyField(Goods, verbose_name='商品')
    user_head_url = CharField(verbose_name='用户头像')
    user_name = CharField(verbose_name='用户名')
    good_info = CharField(max_length=500, verbose_name='购买商品信息')
    evaluate_time = DateTimeField(verbose_name='评论时间')
    content = TextField(default='', verbose_name='评论内容')
    star = IntegerField(default=0, verbose_name='评分')
    comment_num = IntegerField(default=0, verbose_name='评论数')
    press_num = IntegerField(default=0, verbose_name='点赞数')
    image_list = TextField(default='', verbose_name='图片')
    video_list = TextField(default='', verbose_name='视频')


class GoodsEvaluateSummary(BaseModel):
    tag_id = CharField(primary_key=True)
    goods = ForeignKeyField(Goods, verbose_name='商品')
    tag = CharField(max_length=20, verbose_name='标签')
    num = IntegerField(default=0, verbose_name='数量')


if __name__ == '__main__':
    db.create_tables([Goods, GoodsEvaluate, GoodsEvaluateSummary])
