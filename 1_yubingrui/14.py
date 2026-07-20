#题目：输入某年某月某日，判断这一天是这一年的第几天？  
#1.程序分析：以3月5日为例，应该先把前两个月的加起来，然后再加上5天即本年的第几天，特殊情况，闰年且输入月份大于3时需考虑多加一天。

def day_of_year(year,month,day):
    #判断是否为闰年
    if year % 4 == 0:
        days = [31,29,31,30,31,30,31,31,30,31,30,31]
        
    else:
        days = [31,28,31,30,31,30,31,31,30,31,30,31]
    for i in range(month-1):
        day += days[i]
    return day

if __name__ == "__main__":
    year = int(input("请输入年份："))
    month = int(input("请输入月份："))
    day = int(input("请输入今天是本月第几天："))
    print(f"{year}年{month}月{day}日是这一年的第{day_of_year(year,month,day)}天")
        
        