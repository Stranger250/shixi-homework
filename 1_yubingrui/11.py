#题目：有1、2、3、4个数字，能组成多少个互不相同且无重复数字的三位数？都是多少？  
#1.程序分析：可填在百位、十位、个位的数字都是1、2、3、4。组成所有的排列后再去   掉不满足条件的排列。 

def count_three_digit_numbers():
    numbers = []
    for i in range(1, 5):
        for j in range(1, 5):
            for k in range(1, 5):
               numbers.append(i*100 + j*10 + k)
    numbers = list(set(numbers))
    lefts = []
    for n in numbers:
        a = str(n)
        if len(set(a)) == 3:
            lefts.append(n)
    count = len(lefts)
    return count, lefts

if __name__ == "__main__":
    count, lefts = count_three_digit_numbers()
    print(f"能组成{count}个互不相同且无重复数字的三位数，分别是：{lefts}")

