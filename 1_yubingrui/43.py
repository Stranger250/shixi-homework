#题目：求0—7所能组成的奇数个数。  
#自加条件，数字不能重复

total = 0
# 遍历1~8位数字
for digit in range(1, 9):
    if digit == 1:     #当前位数为digit
        cnt = 4         #1位奇数有4个（0、2、4、6）
    else:
        res = 4     #当前位数剩下的奇数总组合数
        res *= 6    #8个数字除去0和个位数
        available = 6     #当前剩余可选择的数
        for i in range(digit - 2):
            res *= available
            available -= 1
        cnt = res
    total += cnt
    print(f"{digit}位奇数：{cnt} 个")
print(f"\n0-7不重复数字组成的所有奇数总数：{total}")

