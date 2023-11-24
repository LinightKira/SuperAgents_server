from agents_server.db import db, Base


class DispatchUnit(Base):
    id = db.Column(db.Integer, primary_key=True, comment="主键ID")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment="所属用户ID")
    dispatcher_id = db.Column(db.Integer, db.ForeignKey('dispatcher.id'), comment="调度员ID")
    agent_unit_id = db.Column(db.Integer, db.ForeignKey('agent_unit.id'), comment="代理单元ID")
    settings = db.Column(db.Text, comment="调度设置")
    prompt = db.Column(db.Text, comment="提示词")
    next_action = db.Column(db.String(500), comment="下一步动作")
    auto_next = db.Column(db.Boolean, comment="是否自动执行下一步", default=False)

    # 单向引用
    agent_unit = db.relationship("AgentUnit")

    def __str__(self):
        return f"<DispatchUnit {self.id}>"

    def to_dict(self):
        base_dict = Base.to_dict(self)
        return {
            **base_dict,
            'agent_unit': self.agent_unit.to_dict() if self.agent_unit and self.agent_unit.status == 1 else None
        }


def GetAllDispatchUnitsByDispatcherId(did, status=1):
    return DispatchUnit.query.filter_by(dispatcher_id=did, status=status).all()
