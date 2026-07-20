#题目：求1+2!+3!+...+20!的和  
#1.程序分析：此程序只是把累加变成了累乘。

def factorial(n):
    total = 1
    while n > 0:
        total = n * total
        n -= 1
    return total
    
def sum_factorial(n):
    total = 0
    fact = 1
    for i in range(1, n+1):
        fact *= i
        total += fact
    return total

if __name__ == "__main__":
    print(sum_factorial(20))
        