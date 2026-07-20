#题目：有五个学生，每个学生有3门课的成绩，从键盘输入以上数据（包括学生号，姓名，三门课成绩），计算出平均成绩，况原有的数据和计算出的平均分数存放在磁盘文件 "stud "中。

student_list = []

for num in range(5):
    print(f"请输入第{num+1}位学生信息:")
    sid = input("学生学号：")
    name = input("学生姓名：")
    s1 = float(input("课程1成绩："))
    s2 = float(input("课程2成绩："))
    s3 = float(input("课程3成绩："))
    avg = (s1 + s2 + s3) / 3    #平均分
    student_list.append([sid, name, s1, s2, s3, avg])

with open("stud", "w", encoding="utf-8") as f:
    f.write("学号\t姓名\t课程1\t课程2\t课程3\t平均分\n")
    for stu in student_list:
        line = f"{stu[0]}\t{stu[1]}\t{stu[2]}\t{stu[3]}\t{stu[4]}\t{stu[5]:.2f}\n"
        f.write(line)

print("数据已全部保存到文件 stud 中！")