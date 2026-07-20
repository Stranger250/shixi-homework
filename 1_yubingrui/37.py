#题目：有n个人围成一圈，顺序排号。从第一个人开始报数（从1到3报数），凡报到3的人退出圈子，问最后留下的是原来第几号的那位。  

def josephus(n):
    people = list(range(1, n+1))
    idx = -1 
    count = 0   # 报数计数器
    while len(people) > 1:
        idx += 1
        # 环形处理，走到末尾回到开头
        if idx >= len(people):
            idx = 0
        count += 1
        if count == 3:
            people.pop(idx)
            count = 0
            idx -= 1
    return people[0]

if __name__ == "__main__":
    n = int(input("请输入人数："))
    print(f"最后留下的是原来第{josephus(n)}号")