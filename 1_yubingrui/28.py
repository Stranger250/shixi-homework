#题目：对10个数进行排序  
#1.程序分析：可以利用选择法，即从后9个比较过程中，选择一个最小的与第一个元素交换，   下次类推，即用第二个元素与后8个进行比较，并进行交换。 

def sort(numbers):
    for i in range(10):
        min_num = numbers[i]
        min_index = i
        for j in range(i+1,10):
            if min_num > numbers[j]:
                min_num = numbers[j]
                min_index = j
        numbers[min_index],numbers[i] = numbers[i],numbers[min_index]
    return numbers

if __name__ == "__main__":
    print("请输入10个数：")
    numbers = [int(input()) for i in range(10)]
    numbers = sort(numbers)
    print(numbers)