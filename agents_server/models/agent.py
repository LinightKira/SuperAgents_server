# Agent

from agents_server.db import db, Base


class Agent(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment="所属用户ID")
    name = db.Column(db.String(50), comment="Agent名字")
    description = db.Column(db.String(200), comment="Agent说明")

    avatar = db.Column(db.String(255), comment="头像")

    memory_config = db.Column(db.String(500), comment="记忆设置")
    dataset_config = db.Column(db.String(500), comment="资料库设置")

    # dispatchers = db.relationship("dispatcher", back_populates="agent")


def Get_agent_byId(agent_id):
    return Agent.query.get(agent_id)
