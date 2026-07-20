#题目：一个偶数总能表示为两个素数之和。
import math

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def goldbach(n):
    if n % 2 != 0:
        print("输入的数字不是偶数！")
        return False
    has_pair = False
    for i in range(2, n // 2 + 1):
        j = n - i
        if is_prime(i) and is_prime(j):
            print(f"{n} = {i} + {j}")
            has_pair = True
    return has_pair

if __name__ == "__main__":
    n = int(input("请输入一个偶数："))
    result = goldbach(n)
    if result:
        print(f"{n} 可以表示为两个素数之和")
    else:
        print(f"{n} 不能表示为两个素数之和")