#题目：有n个整数，使其前面各数顺序向后移m个位置，最后m个数变成最前面的m个数  

def shift(lists, m):
    n = len(lists)
    m = m % n
    for _ in range(m):
        last = lists.pop()
        lists.insert(0, last)
    return lists

if __name__ == "__main__":
    n = int(input("请输入要输入整数的个数："))
    lists = []
    for i in range(n):
        lists.append(int(input(f"请输入第{i+1}个整数：")))
    m = int(input("请输入要向后移的个数："))
    lists = shift(lists, m)
    print(lists)
    