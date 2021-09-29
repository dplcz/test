from peewee import *

db = MySQLDatabase('spider', host='localhost', port=3306, user='root', password='dp20020620')


class Person(Model):
    # 指定表中的栏位名称和类型
    # 设置name为最大长度20，可以为空
    name = CharField(max_length=20, null=True)
    birthday = DateField()

    # primary_key属性设置该栏位是否为主键

    class Meta:
        database = db  # This model uses the "people.db" database.
        # 表名
        table_name = 'users'


# TODO 数据增，删，改，查

if __name__ == '__main__':
    # db.create_tables([Person])
    from datetime import date

    # 生成数据
    # uncle_bob = Person(name='Bob', birthday=date(1960, 1, 15))
    # uncle_bob.save()  # bob is now stored in the database

    # 查询数据(只获取一条数据)     get()方法在没查询到数据时会抛出异常
    # grandma = Person.select().where(Person.name == 'DP').get()
    # # 如果有重名只获取第一条
    # print(grandma.birthday)
    # print(grandma.id)
    # mysql写法:"select * from Person where name='Grandma L.'"
    # 精简写法:
    # grandma = Person.get(Person.name == 'DP')

    # 输出一串数据
    # 输出同名的数据：(未查询到数据不会抛异常)
    # 可以进行切片
    # query = Person.select().where(Person.name == 'Bob')[:2]
    # # query可以当作list处理
    # for pet in query:
    #     print(pet.name, pet.birthday)

    # 修改数据
    # query = Person.select().where(Person.name == 'Bob')
    # for pet in query:
    #     pet.birthday = date(1999, 6, 15)
    #     pet.save()
    #     # save()方法  在不存在数据时新增数据，存在时修改数据

    # 删除数据
    # query = Person.select().where(Person.name == 'Bob')
    # for pet in query:
    #     pet.delete_instance()
