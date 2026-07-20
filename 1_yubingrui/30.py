#题目：有一个已经排好序的数组。现输入一个数，要求按原来的规律将它插入数组中。  
#1.   程序分析：首先判断此数是否大于最后一个数，然后再考虑插入中间的数的情况，插入后此元素之后的数，依次后移一个位置。  

def insert(numbers,num):
    n = len(numbers)
    if numbers[0] > numbers[1]:
        print("原数组是按从大到小排序的")
        for i in range(n):
            if num > numbers[i]:
                numbers.insert(i,num)
                break
    else:
        print("原数组是按从小到大排序的")
        for i in range(n):
            if num < numbers[i]:
                numbers.insert(i,num)
                break
    return numbers

if __name__ == "__main__":
    print("请输入10个数：")
    numbers = [int(input()) for i in range(10)]
    num = int(input("请输入要插入的数："))
    numbers = insert(numbers,num)
    print(numbers)
