#题目：计算字符串中子串出现的次数

def count_substring(string, sub):
    len_str = len(string)
    len_sub = len(sub)
    count = 0
    i = 0
    while i <= len_str - len_sub:
        if string[i:i+len_sub] == sub:
            count += 1
            i += len_sub  # 匹配成功，跳过整个子串，不重叠
        else:
            i += 1
    return count

if __name__ == "__main__":
    string = input("请输入字符串：")
    sub = input("请输入子串：")
    count = count_substring(string, sub)
    print(f"子串{sub}在字符串{string}中出现了{count}次")