#题目：利用递归方法求5!。  
#1.程序分析：递归公式：fn=fn_1*4!  

total = 1
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)

if __name__ == "__main__":
    print(factorial(5))
        