from flask import Flask, request, jsonify, session
from datetime import datetime
import secrets
from functools import wraps
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

#数据库准备操作
Base = declarative_base()

class Quote(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100),comment = "新闻标题")
    content = Column(Text,comment = "新闻内容")
    category = Column(String(100),comment = "新闻分类")
    publish_time = Column(String(100),comment = "发布时间")

engine = create_engine("sqlite:///cms.db", echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def news_to_dice(news):
    return {
        'id': news.id,
        'title': news.title,
        'content': news.content,
        'category': news.category,
        'publish_time': news.publish_time,
    }

#管理员账号预设
ADMIN_USER = "admin"
ADMIN_PWD = "admin123"

jianjie ={
    'name': '阿里九九',
    'description': '一家根据童话故事制作动画片的工厂',
    'history': '始创于1976年',
    'address': '阿里九九国阿里九九城99号',
    'email': 'ali@ali.com',
    'phone': '13899999999',
}


#============“前台展示接口============”
#获取公司简介+最新的三条新闻
@app.route('/api/home', methods=['GET'])
def get_introduction():
    db_session = Session()
    # 按发布时间倒序，取最新3条
    news_rows = db_session.query(Quote).order_by(Quote.publish_time.desc()).limit(3).all()
    news_list = [news_to_dice(item) for item in news_rows]
    db_session.close()
    return jsonify({"code": 200, "msg": "获取成功", "data": {"jianjie": jianjie, "news_list": news_list}})

#获取新闻列表:按发布时间顺序从新到旧排列
@app.route('/api/news', methods=['GET'])
def get_news():
    db_session = Session()
    news_rows = db_session.query(Quote).order_by(Quote.publish_time.desc()).all()
    sorted_news = [news_to_dice(item) for item in news_rows]
    db_session.close()
    return jsonify({"code": 200, "msg": "获取成功", "data": sorted_news})


#获取新闻详情
@app.route('/api/news/<int:id>', methods=['GET'])
def get_new_detail(id):
    db_session = Session()
    news = db_session.query(Quote).filter_by(id=id).first()
    db_session.close()
    if news:
        return jsonify({"code": 200, "msg": "获取成功", "data": news_to_dice(news)})
    else:
        return jsonify({"code": 404, "msg": "新闻不存在"}), 404


#============“后台管理接口============”
#登录校验装饰器
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return jsonify({"code": 403, "msg": "Forbidden"}), 403
        return f(*args, **kwargs)
    return decorated

#管理员登录
@app.route('/admin/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({"code": 400, "msg": "用户名和密码不能为空"}), 400
    if data['username'] != ADMIN_USER or data['password'] != ADMIN_PWD:
        return jsonify({"code": 401, "msg": "非管理员不得登录"}), 400
    session['username'] = data['username']
    return jsonify({"code": 200, "msg": "登录成功"}), 200


#发布新闻
@app.route('/admin/news', methods=['POST'])
@login_required
def post_news():
    data = request.get_json()
    if not data.get('title') or not data.get('content') or not data.get('category'):
        return jsonify({"code": 400, "msg": "标题、内容和分类不能为空"}), 400
    db_session = Session()
    news = Quote(
        title=data['title'],
        content=data['content'],
        category=data['category'],
        publish_time=datetime.now().isoformat()
    )
    db_session.add(news)
    db_session.commit()
    result = news_to_dice(news)
    db_session.close()
    return jsonify({"code": 200, "msg": "发布成功", "data": result})


#删除指定新闻
@app.route('/admin/news/<int:id>', methods=['DELETE'])
@login_required
def delete_news(id):
    db_session = Session()
    news = db_session.query(Quote).filter_by(id=id).first()
    if news:
        db_session.delete(news)
        db_session.commit()
        db_session.close()
        return jsonify({"code": 200, "msg": "删除成功"}), 200
    else:
        db_session.close()
        return jsonify({"code": 404, "msg": "新闻不存在"}), 404




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
