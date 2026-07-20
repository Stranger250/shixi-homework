#题目：输入3个数a,b,c，按大小顺序输出。  
#1.程序分析：利用指针方法。  

#python无指针
def swap(x, y):
    return y, x

if __name__ == "__main__":
    a = int(input("请输入第一个数："))
    b = int(input("请输入第二个数："))
    c = int(input("请输入第三个数："))
    if a < b:
        a, b = swap(a, b)
    if a < c:
        a, c = swap(a, c)
    if b < c:
        b, c = swap(b, c)
    print(f"从大到小排序：{a} {b} {c}")