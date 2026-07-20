#题目：有一分数序列：2/1，3/2，5/3，8/5，13/8，21/13...求出这个数列的前20项之和。  
#1.程序分析：请抓住分子与分母的变化规律。  

def fraction_sum(n):
    total = 0.0
    a, b = 1, 2  # 分母、分子
    for _ in range(n):
        total += b / a
        a, b = b, a + b
    return total

if __name__ == "__main__":
    print(fraction_sum(20))
      
    