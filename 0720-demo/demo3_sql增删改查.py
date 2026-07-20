# demo3_sql增删改查.py
import pymysql

# 封装连接函数，统一管理连接信息
def get_conn():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="279231", # 这里必须改成你自己的MySQL登录密码
        port=3306,
        database="school", # 固定绑定school库，不会找不到表
        charset="utf8mb4"
    )
    return conn

# 1. 新增学生
def add_student():
    conn = get_conn()
    cursor = conn.cursor()
    # 字段顺序：name,age,class_name,score  和数据表字段完全对应
    insert_sql = "INSERT INTO student(name, age, class_name, score) VALUES(%s, %s, %s, %s)"
    # 单条数据，4个值对应4个字段
    data1 = ("张三", 18, "高三1班", 92.5)
    cursor.execute(insert_sql, data1)
    # 批量多条
    multi_data = [
        ("李四", 17, "高三1班", 88),
        ("王五", 18, "高三2班", 95),
        ("赵六", 17, "高三2班", 76)
    ]
    cursor.executemany(insert_sql, multi_data)
    conn.commit()
    print(f"新增完成，共插入 {cursor.rowcount} 条数据")
    cursor.close()
    conn.close()

# 2. 查询学生
def query_student():
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # 查询全部
    cursor.execute("SELECT * FROM student;")
    all_data = cursor.fetchall()
    print("====全部学生====")
    for item in all_data:
        print(item)
    # 条件查询
    cursor.execute("SELECT name,score FROM student WHERE score > %s", (90,))
    high_score = cursor.fetchall()
    print("\n====90分以上学生====")
    print(high_score)
    cursor.close()
    conn.close()

# 3. 修改学生
def update_student():
    conn = get_conn()
    cursor = conn.cursor()
    update_sql = "UPDATE student SET score=%s WHERE name=%s"
    cursor.execute(update_sql, (98, "张三"))
    conn.commit()
    print(f"修改成功，影响行数：{cursor.rowcount}")
    cursor.close()
    conn.close()

# 4. 删除学生
def delete_student():
    conn = get_conn()
    cursor = conn.cursor()
    delete_sql = "DELETE FROM student WHERE score < %s"
    cursor.execute(delete_sql, (80,))
    conn.commit()
    print(f"删除成功，影响行数：{cursor.rowcount}")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    add_student()
    query_student()
    # update_student()
    # delete_student()