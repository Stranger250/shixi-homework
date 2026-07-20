#题目：一个5位数，判断它是不是回文数。即12321是回文数，个位与万位相同，十位与千位相同。  

eve_number = []
def number(n):
    for i in range(5):
        eve_number.append(n % 10)
        n //= 10
    if eve_number[0] == eve_number[4] and eve_number[1] == eve_number[3]:
        return True
    else:
        return False

if __name__ == "__main__":
    n = int(input("请输入一个5位数："))
    if number(n):
        print(f"{n}是回文数")
    else:
        print(f"{n}不是回文数")
    
