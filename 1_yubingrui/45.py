#题目：判断一个素数能被几个9整除  

#任何素数都不能被9整除
import math

def is_prime(num):
    if num == 1:
        return False
    else:
        for i in range(2,int(math.sqrt(num)+1)):
            if num%i == 0:
                return False
        else:
            return True

if __name__ == "__main__":
    while True:
        num = int(input("请输入一个整数："))
        if num == 0:
            break
        if is_prime(num):
            if num%9 == 0:
                print(f"素数{num}能被9整除")
            else:
                print(f"素数{num}不能被9整除")
        else:
            print(f"{num}不是素数,请重新输入一个整数")
