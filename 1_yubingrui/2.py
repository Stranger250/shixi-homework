import math
#题目：判断101-200之间有多少个素数，并输出所有素数。
def is_prime(num):
    if num == 1:
        return False
    else:
        for i in range(2,int(math.sqrt(num)+1)):
            if num%i == 0:
                return False
        else:
            return True
        
if __name__ == "__main__":
    sum = []
    for i in range(101,201):
        if is_prime(i):
            sum.append(i)
    for i in sum:
        print(i)
                
        