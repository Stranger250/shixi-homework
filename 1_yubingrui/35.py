#题目：输入数组，最大的与第一个元素交换，最小的与最后一个元素交换，输出数组。  

def swap(lists):
    n = len(lists)
    max_index = 0
    min_index = 0
    for i in range( n):
        if lists[i] > lists[max_index]:
            max_index = i
    lists[0], lists[max_index] = lists[max_index], lists[0]
    for i in range( n):
        if lists[i] < lists[min_index]:
            min_index = i
    lists[n-1], lists[min_index] = lists[min_index], lists[n-1]
    return lists

if __name__ == "__main__":
    n = int(input("请输入要输入的数组中数字的个数："))
    lists = []
    for i in range(n):
        lists.append(int(input(f"请输入第{i+1}个数字：")))
    lists = swap(lists)
    print(lists)