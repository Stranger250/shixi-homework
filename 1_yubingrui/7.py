#题目：输入一行字符，分别统计出其中英文字母、空格、数字和其它字符的个数。  
#1.程序分析：利用while语句,条件为输入的字符不为 '\n '.  

def count_chars(chars):
    letters = 0
    spaces = 0
    digits = 0
    others = 0
    for char in chars:
        if char.isalpha():     #isalpha()方法用于判断字符串是否只包含字母字符
            letters += 1
        elif char == ' ':
            spaces += 1
        elif char.isdigit():     #isdigit()方法用于判断字符串是否只包含数字字符
            digits += 1
        else:
            others += 1
    return letters, spaces, digits, others

if __name__ == "__main__":
    chars = input("请输入一行字符：")
    letters, spaces, digits, others = count_chars(chars)
    print(f"英文字母的个数为：{letters}")
    print(f"空格的个数为：{spaces}")
    print(f"数字的个数为：{digits}")
    print(f"其它字符的个数为：{others}")
            
    
   
