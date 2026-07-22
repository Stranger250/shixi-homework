import requests
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# ===================== 1. 数据库模块 =====================
engine = create_engine("sqlite:///gov_news.db", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class GovNews(Base):
    __tablename__ = "gov_news"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500))
    publish_time = Column(String(30))
    link = Column(String(800), unique=True)

Base.metadata.create_all(bind=engine)

# ===================== 2. 请求全局配置（防反爬强制） =====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.gov.cn/"
}
TIMEOUT = 15
SLEEP_MIN = 2
SLEEP_MAX = 4
BASE_DOMAIN = "https://www.gov.cn"

# ===================== 拓展3：XPath解析函数（和BS4对比用） =====================
def parse_by_xpath(html):
    """使用XPath提取新闻列表，返回[(标题,时间,完整链接)]"""
    # lxml 无法直接解析该站 HTML，先用 html.parser 提取内容区，再用 lxml 解析
    soup = BeautifulSoup(html, "html.parser")
    news_box = soup.select_one(".news_box")
    if not news_box:
        return []

    tree = etree.HTML(str(news_box))
    news_items = tree.xpath("//div[contains(@class, 'list')]//li")
    res = []
    for li in news_items:
        title = li.xpath(".//h4/a/text()")
        href = li.xpath(".//h4/a/@href")
        pub_time = li.xpath(".//span[contains(@class, 'date')]/text()")
        if not title or not href or not pub_time:
            continue
        title = title[0].strip()
        pub_time = pub_time[0].strip()
        full_link = BASE_DOMAIN + href[0]
        res.append((title, pub_time, full_link))
    return res

# ===================== 核心抓取函数（BS4为主） =====================
def crawl_page(page_num):
    # gov.cn 真实分页格式：第1页=home.htm，第N页=home_{N-1}.htm
    if page_num == 1:
        url = f"{BASE_DOMAIN}/toutiao/liebiao/home.htm"
    else:
        url = f"{BASE_DOMAIN}/toutiao/liebiao/home_{page_num - 1}.htm"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code == 403:
            print(f"【第{page_num}页】403访问受限，触发反爬，程序退出！")
            exit(1)
        resp.encoding = "utf-8"
        html = resp.text

        # 1. BeautifulSoup 解析（主逻辑）—— 必须用 html.parser，lxml 对该站无效
        soup = BeautifulSoup(html, "html.parser")
        news_list = soup.select(".news_box .list li")
        if not news_list:
            print(f"【第{page_num}页】BS4未匹配到新闻条目")
            return True

        # 2. XPath 解析对比（拓展3）
        xpath_data = parse_by_xpath(html)
        print(f"【第{page_num}页】XPath解析到 {len(xpath_data)} 条数据，BS4解析到 {len(news_list)} 条数据")

        db = SessionLocal()
        try:
            for item in news_list:
                a_tag = item.select_one("h4 a")
                time_tag = item.select_one("span.date")
                # 空值过滤：标题/时间缺失直接跳过
                if not a_tag or not time_tag:
                    continue
                title = a_tag.get_text(strip=True)
                pub_time = time_tag.get_text(strip=True)
                rel_href = a_tag["href"]
                full_link = BASE_DOMAIN + rel_href

                news = GovNews(title=title, publish_time=pub_time, link=full_link)
                db.add(news)
            db.commit()
            print(f"【第{page_num}页】成功入库，共{len(news_list)}条")
        except SQLAlchemyError as e:
            db.rollback()
            print(f"【第{page_num}页】数据库写入异常，已回滚：{str(e)}")
        finally:
            db.close()
        return True

    except Exception as e:
        print(f"【第{page_num}页】页面请求异常：{str(e)}")
        return False

# ===================== 拓展2：数据库导出CSV =====================
def export_db_to_csv():
    db = SessionLocal()
    all_news = db.query(GovNews).all()
    if not all_news:
        print("数据库暂无数据，无法导出CSV")
        db.close()
        return
    data = []
    for item in all_news:
        data.append({
            "id": item.id,
            "title": item.title,
            "publish_time": item.publish_time,
            "link": item.link
        })
    df = pd.DataFrame(data)
    df.to_csv("gov_news.csv", index=False, encoding="utf-8-sig")
    db.close()
    print("数据导出完成，文件：gov_news.csv")

# ===================== 拓展1：交互式菜单 =====================
def show_menu():
    print("\n===== 政府新闻爬虫菜单 =====")
    print("1. 抓取指定单页")
    print("2. 批量抓取1~10页")
    print("3. 将数据库数据导出CSV")
    print("4. 退出程序")
    choice = input("请输入功能序号：").strip()
    return choice

# ===================== 主程序入口 =====================
if __name__ == "__main__":
    while True:
        opt = show_menu()
        if opt == "1":
            page_input = input("请输入要抓取的页码(1-10)：").strip()
            try:
                page = int(page_input)
                if 1 <= page <= 10:
                    crawl_page(page)
                    delay = random.uniform(SLEEP_MIN, SLEEP_MAX)
                    print(f"抓取完成，休眠{delay:.2f}秒\n")
                    time.sleep(delay)
                else:
                    print("页码必须在1~10之间！")
            except ValueError:
                print("输入不是有效数字！")
        elif opt == "2":
            print("开始批量抓取1~10页...")
            for page in range(1, 11):
                crawl_page(page)
                delay = random.uniform(SLEEP_MIN, SLEEP_MAX)
                print(f"休眠{delay:.2f}秒后进入下一页\n")
                time.sleep(delay)
            print("===== 10页全部抓取完毕 =====")
        elif opt == "3":
            export_db_to_csv()
        elif opt == "4":
            print("程序退出")
            break
        else:
            print("输入无效，请重新选择！")