#题目：给一个不多于5位的正整数，要求：一、求它是几位数，二、逆序打印出各位数字。  
eve_number = []
def number(n):
    digit = len(str(n))
    for i in range(digit):
        eve_number.append(n % 10)
        n //= 10
    return digit , eve_number

if __name__ == "__main__":
    n = int(input("请输入一个不多于5位的正整数："))
    digit , eve_number = number(n)
    print(f"{n}是{digit}位数 ,逆序打印各位数字为： {eve_number}")
    
