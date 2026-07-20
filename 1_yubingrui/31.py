#题目：将一个数组逆序输出。  
#1.程序分析：用第一个与最后一个交换。  

def reverse(numbers):
    n = len(numbers)
    for i in range(n//2):
        numbers[i],numbers[n-i-1] = numbers[n-i-1],numbers[i]
    return numbers

if __name__ == "__main__":
    print("请输入10个数：")
    numbers = [int(input()) for i in range(10)]
    numbers = reverse(numbers)
    print(numbers)