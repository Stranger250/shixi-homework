#题目：求100之内的素数
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
    for i in range(1,101):
        if is_prime(i):
            print(i)
        else:
            pass
