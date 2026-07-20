# demo2_sql创建数据表.py
import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="279231",
    port=3306,
    database="school",
    charset="utf8mb4"
)
cursor = conn.cursor()

# 如果旧表存在，直接删除
cursor.execute("DROP TABLE IF EXISTS student;")

# 重建完整5字段表
create_table_sql = """
CREATE TABLE IF NOT EXISTS student (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '学生自增主键ID',
    name VARCHAR(20) NOT NULL COMMENT '学生姓名，不能为空',
    age TINYINT COMMENT '学生年龄',
    class_name VARCHAR(30) COMMENT '所在班级',
    score FLOAT COMMENT '考试分数'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生信息表';
"""
cursor.execute(create_table_sql)
print("数据表 student 重建完成，包含 id/name/age/class_name/score 全部字段")
cursor.close()
conn.close()