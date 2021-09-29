import pymysql.cursors

# Connect to the database
# 新建连接
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='dp20020620',
                             database='spider',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

with connection:
    with connection.cursor() as cursor:
        # Create a new record
        # 将email,password传入users中
        sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
        # .execute(sql,(,元组))   传入数据
        cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    # 执行命令
    connection.commit()

    with connection.cursor() as cursor:
        # Read a single record
        # 查找数据  从email查询id和password
        sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
        cursor.execute(sql, ('webmaster@python.org',))
        result = cursor.fetchone()
        print(result)
