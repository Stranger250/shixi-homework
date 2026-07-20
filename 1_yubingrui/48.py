#题目：某个公司采用公用电话传递数据，数据是四位的整数，在传递过程中是加密的，加密规则如下：每位数字都加上5,然后用和除以10的余数代替该数字，再将第一位和第四位交换，第二位和第三位交换。  

def encrypt(num):
    a = num // 1000
    b = num // 100 % 10
    c = num // 10 % 10
    d = num % 10

    a1 = (a + 5) % 10
    b1 = (b + 5) % 10
    c1 = (c + 5) % 10
    d1 = (d + 5) % 10
    
    new_num = d1 * 1000 + c1 * 100 + b1 * 10 + a1
    return new_num

if __name__ == "__main__":
    num = int(input("请输入四位四位数："))
    encrypted = encrypt(num)
    print(f"加密后的四位数为：{encrypted}")
