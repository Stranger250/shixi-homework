#题目：一个整数，它加上100后是一个完全平方数，再加上168又是一个完全平方数，请问该数是多少？  
#1.程序分析：在10万以内判断，先将该数加上100后再开方，再将该数加上268后再开方，如果开方后的结果满足如下条件，即是结果。请看具体分析：  
import math

count = 0
nums = []
for i in range(-100,100001):
    a = int(math.sqrt(i+100))
    b = int(math.sqrt(i+268))
    if a**2 == i+100 and b**2 == i+268:
        count += 1
        nums.append(i)
if count >= 1:
    print(nums)
else:
    print("没有符合条件的数")
