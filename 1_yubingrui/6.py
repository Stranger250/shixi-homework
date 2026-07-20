#题目：输入两个正整数m和n，求其最大公约数和最小公倍数。  
#1.程序分析：利用辗除法。  

#最大公约数
def gcd(m,n):
    while n != 0:
        m, n = n, m % n
    return m

#最小公倍数: m * n // gcd(m,n)
def lcm(m,n):
    if m > n:
        max = m
        min = n
    else:
        max = n
        min = m
    for i in range(1,min+1):
        if max * i % min == 0:
            return max * i
        
if __name__ == "__main__":
    m = int(input("请输入第一个正整数："))
    n = int(input("请输入第二个正整数："))
    print(f"{m}和{n}的最大公约数为：{gcd(m,n)}")
    print(f"{m}和{n}的最小公倍数为：{lcm(m,n)}")
    
   
    