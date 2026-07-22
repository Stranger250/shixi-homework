import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker


MYSQL_USER = "root"
MYSQL_PASSWORD = "279231"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DB = "quotes_db"

Base = declarative_base()


class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, comment="名言内容")
    author = Column(String(100), comment="作者")
    tags = Column(String(200), comment="标签")


# MySQL 连接
engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}",
    echo=False,
)
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
    print("  1. 爬取所有名言（含翻页）")
    print("  2. 按作者搜索名言")
    print("  3. 分页浏览名言")
    print("  4. 清空数据表")
    print("  5. 退出")
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

                # 去重
                exists = session.query(Quote).filter_by(text=text, author=author).first()
                if not exists:
                    session.add(Quote(text=text, author=author, tags=tags))

            total += len(quotes_divs)
            print(f"第{page_num}页爬取完毕，本页 {len(quotes_divs)} 条")

            # 查找"Next"按钮
            next_btn = soup.find("li", class_="next")
            if next_btn and next_btn.find("a"):
                page_url = url.rstrip("/") + next_btn.find("a")["href"]
                page_num += 1
            else:
                page_url = None

        session.commit()
        session.close()
        print("=" * 40)
        print(f"[OK] 共爬取 {page_num} 页，{total} 条名言，已存入 MySQL")

    elif n == 2:
        session = Session()
        print("请输入要搜索的作者：")
        author_name = input()
        quotes = session.query(Quote).filter_by(author=author_name).all()
        if quotes:
            for quote in quotes:
                print("-" * 40)
                print(f"名言：{quote.text}")
                print(f"作者：{quote.author}")
                print(f"标签：{quote.tags}")
        else:
            print(f"没有找到作者为 {author_name} 的名言")
        session.close()

    elif n == 3:
        session = Session()
        # 获取总条数
        total_count = session.query(Quote).count()
        if total_count == 0:
            print("数据库中没有数据，请先爬取！")
            session.close()
            continue

        page_size = int(input(f"每页显示几条？（共 {total_count} 条）："))

        current_page = 1
        total_pages = (total_count + page_size - 1) // page_size  # 向上取整

        while True:
            offset = (current_page - 1) * page_size
            quotes = session.query(Quote).offset(offset).limit(page_size).all()

            print("\n" + "=" * 40)
            print(f"第 {current_page}/{total_pages} 页（共 {total_count} 条）")
            print("=" * 40)

            for quote in quotes:
                print("-" * 40)
                print(f"名言：{quote.text}")
                print(f"作者：{quote.author}")
                print(f"标签：{quote.tags}")

            print("\n" + "-" * 40)
            print("  N: 下一页  |  P: 上一页  |  Q: 返回主菜单")
            print("-" * 40)
            cmd = input().strip().upper()

            if cmd == "N" and current_page < total_pages:
                current_page += 1
            elif cmd == "P" and current_page > 1:
                current_page -= 1
            elif cmd == "Q":
                break
            else:
                print("无效操作或已是首页/末页！")

        session.close()

    elif n == 4:
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

    elif n == 5:
        print("退出程序")
        break
