# Agent 最小执行单元
from agents_server.db import db, Base


class AgentUnit(Base):
    id = db.Column(db.Integer, primary_key=True, comment="主键ID")
    name = db.Column(db.String(50), comment="名字")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment="所属用户ID")
    prompt = db.Column(db.Text, comment="提示词")
    tools = db.Column(db.String(200), comment="工具ID")
    category = db.Column(db.String(50), comment="分类")

    llm_config = db.Column(db.String(500), comment="LLM配置")


def GetAgentUnitById(aid):
    return AgentUnit.query.get(aid)
