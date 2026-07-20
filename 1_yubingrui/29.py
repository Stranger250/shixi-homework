#题目：求一个3*3矩阵对角线元素之和  
#1.程序分析：利用双重for循环控制输入二维数组，再将a累加后输出。  
shuzu = []
for i in range(3):
    a = []
    for j in range(3):
        a.append(int(input(f"请输入二维数组第{i+1}行第{j+1}列的元素：")))
    shuzu.append(a)

total = 0
for i in range(3):
    total += shuzu[i][i]
    total += shuzu[i][2-i]
total -= shuzu[1][1]
    
print(f"对角线元素之和为{total}")
