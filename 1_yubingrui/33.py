#题目：打印出杨辉三角形（要求打印出10行如下图）  

# 打印10行杨辉三角
n = 10
# 存储杨辉三角
triangle = []
for i in range(n):
    row = [1] * (i + 1)  # 每行先全部填充1
    # 处理中间元素，跳过首尾
    for j in range(1, i):
        row[j] = triangle[i-1][j-1] + triangle[i-1][j]
    triangle.append(row)
    # 打印当前行，居中对齐
    print(" ".join(map(str, row)).center(60))
    #"".join()  将括号中的元素用""中的字符分隔开
    #map(str,row)  将row中的每个元素转换为字符串
    #center(60)  居中对齐，宽度为60