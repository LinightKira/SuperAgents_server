from datetime import datetime

from agents_server.db import Base, db


class User(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    nickname = db.Column(db.String(32), comment="昵称")
    avatar = db.Column(db.String(255), comment="头像")
    unionid = db.Column(db.String(50), comment="unionid")
    openid = db.Column(db.String(50), comment="openid")

    last_active_time = db.Column(db.DateTime, default=datetime.now, comment="最后登录时间")
