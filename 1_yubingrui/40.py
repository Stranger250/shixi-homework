#题目：字符串排序。  
def sort_str(s):
    return ''.join(sorted(s))

if __name__ == "__main__":
    s = input("请输入一个字符串：")
    print(f"排序后的字符串为：{sort_str(s)}")