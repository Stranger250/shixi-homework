import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text,comment = "名言内容")
    author = Column(String(100),comment = "作者")
    tags = Column(String(200),comment = "标签")

engine = create_engine("sqlite:///quotes.db", echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

url = "http://quotes.toscrape.com/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 15; Pixel 9) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Mobile Safari/537.36"
    )
}


while True:
    print("\n" + "=" * 40)
    print("  1. 爬取首页名言")
    print("  2. 按作者搜索名言")
    print("  3. 清空数据表")
    print("  4. 退出")
    print("=" * 40)
    n = int(input("请选择要进行什么操作："))
    if n == 1:  
        page_url = url
        page_num = 1
        total = 0
        session = Session()

        while page_url:
            try:
                response = requests.get(page_url, headers=headers, timeout=5)
                print(f"第{page_num}页 状态码：{response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] 请求失败：{e}")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            quotes_divs = soup.find_all("div", class_="quote")

            for div in quotes_divs:
                text = div.find("span", class_="text").get_text(strip=True)
                author = div.find("small", class_="author").get_text(strip=True)
                tag_elems = div.find_all("a", class_="tag")
                tags = ", ".join(t.get_text(strip=True) for t in tag_elems)

                print("-" * 40)
                print(f"名言：{text}")
                print(f"作者：{author}")
                print(f"标签：{tags}")

                exists = session.query(Quote).filter_by(text=text, author=author).first()
                if not exists:
                    session.add(Quote(text=text, author=author, tags=tags))

            total += len(quotes_divs)
            print(f"第{page_num}页爬取完毕，本页 {len(quotes_divs)} 条")

            # 查找"Next"按钮，获取下一页 URL
            next_btn = soup.find("li", class_="next")
            if next_btn and next_btn.find("a"):
                page_url = url.rstrip("/") + next_btn.find("a")["href"]
                page_num += 1
            else:
                page_url = None

        session.commit()
        session.close()
        print("=" * 40)
        print(f"共爬取 {page_num} 页，{total} 条名言，已存入 quotes.db")

    elif n == 2:
        session = Session()
        print("请输入要搜索的作者：")
        author_name = input()
        quotes = session.query(Quote).filter_by(author=author_name).all()
        if quotes:
            for quote in quotes:
                print(f"名言：{quote.text}")
                print(f"作者：{quote.author}")
                print(f"标签：{quote.tags}")
        else:
            print(f"没有找到作者为 {author_name} 的名言")

    elif n == 3:
        confirm = input("确认清空数据表？输入 yes 确认：")
        if confirm.lower() == "yes":
            session = Session()
            count = session.query(Quote).count()
            session.query(Quote).delete()
            session.commit()
            session.close()
            print(f"已清空 {count} 条数据")
        else:
            print("已取消")

    elif n == 4:
        break

