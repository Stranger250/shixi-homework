#题目：编写一个函数，输入n为偶数时，调用函数求1/2+1/4+...+1/n,当输入n为奇数时，调用函数1/1+1/3+...+1/n(利用指针函数)  

def result(n):
    if n % 2 ==0:
        total = 0
        for i in range(n//2):
            total += 1/(2*i+2)
    else:
        total = 0
        for i in range((n+1)//2):
            total += 1/(2*i+1)
    return total

if __name__ == "__main__":
    n = int(input("请输入一个整数："))
    print(f"结果为：{result(n)}")