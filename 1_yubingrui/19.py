#题目：用*打印出菱形

def print_line(spaces,star):
    space = int(spaces) // 2
    star = int(star)
    for i in range(space):
        print(" ",end="")
    for i in range(star):
        print("*",end="")
    for i in range(space):
        print(" ",end="")

longest = int(input("请输入菱形最长的一行的长度："))
n = longest // 2
for i in range(n+1):
    star_num = i * 2 + 1
    print_line(longest-star_num,star_num)
    print()
for i in range(n,0,-1):
    star_num = i * 2 - 1
    print_line(longest-star_num,star_num)
    print()
