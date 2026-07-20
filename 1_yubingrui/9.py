#题目：一个数如果恰好等于它的因子之和，这个数就称为 "完数 "。例如6=1＋2＋3.编程   找出1000以内的所有完数。  

def is_perfect(n):
    perfect = []
    for i in range(1, n+1):
        yinshus = []
        for j in range(1, i):
            if i % j == 0:
                yinshus.append(j)
        if sum(yinshus) == i:
            perfect.append(i)
    return perfect

if __name__ == "__main__":
    n = int(input("请输入一个数字："))
    print(is_perfect(n))
    
            
