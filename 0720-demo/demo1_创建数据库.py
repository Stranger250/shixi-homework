import pymysql

# 连接时直接指定已创建好的school数据库
conn = pymysql.connect(
    host='localhost', 
    user='root', 
    password='279231', # 替换成你自己的MySQL密码
    port=3306,
    database="school", # 关键：提前绑定目标库
    charset='utf8mb4'
)

cursor = conn.cursor()

# IF NOT EXISTS 防止重复创建报错
sql1 = 'create database if not exists school default charset utf8mb4'
cursor.execute(sql1)
print('数据库school创建成功')

# 完整带字段的建表语句
sql2 = """
create table if not exists student(
    id int primary key auto_increment comment '学生编号',
    name varchar(20) not null comment '学生姓名',
    age tinyint comment '年龄'
) default charset utf8mb4
"""
cursor.execute(sql2)
print('表student创建成功')

cursor.close()
conn.close()