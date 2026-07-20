#题目：一球从100米高度自由落下，每次落地后反跳回原高度的一半；再落下，求它在   第10次落地时，共经过多少米？第10次反弹多高？  

def ball(height, n):
    heights = 0
    if n == 1:
        heights = height
    else:
        heights = height
        for i in range(1, n):
            heights += height * 0.5**(i) * 2
    return heights

if __name__ == "__main__":
    height = int(input("请输入高度："))
    n = int(input("请输入反弹次数："))
    print(ball(height, n))

        