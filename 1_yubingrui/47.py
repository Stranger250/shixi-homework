#题目：读取7个数（1—50）的整数值，每读取一个值，程序打印出该值个数的＊。

def print_star(num):
    for i in num:
        print("*"*i)

if __name__ == "__main__":
    nums = []
    for i in range(7):
        while True:
            val = int(input(f"请输入第{i+1}个整数（1~50）："))
            if 1 <= val <= 50:
                nums.append(val)
                break
            else:
                print("输入超出范围！请输入1到50之间的整数")
    print_star(nums)