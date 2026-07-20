#题目：古典问题：有一对兔子，从出生后第3个月起每个月都生一对兔子，小兔子长到第三个月后每个月又生一对兔子，假如兔子都不死，问每个月的兔子总数为多少？
import math

def rabbit_num(month):
    if month == 1 or month ==2:
        num = 2
    else:
        for i in range(3,month + 1):
            num = rabbit_num(i - 1) + rabbit_num(i - 2)
    return num

if __name__ == "__main__":
    month = int(input("请输入月份："))
    print(rabbit_num(month))
    

