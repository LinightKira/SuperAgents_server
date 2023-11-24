# 智能调度
from datetime import datetime

from sqlalchemy import desc

from agents_server.db import db, Base


class Dispatcher(Base):
    id = db.Column(db.Integer, primary_key=True, comment="主键ID")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment="所属用户ID")
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), comment="Agent ID")
    name = db.Column(db.String(50), comment="名字")
    description = db.Column(db.String(200), comment="说明")

    is_Start = db.Column(db.Boolean, comment="是否是起始节点", default=False)
    # input_config = db.Column(db.String(500), comment="输入配置")  # 实现多个输入源的设置 未实现

    # 单向一对多引用
    dispatch_units = db.relationship("DispatchUnit")

    def __repr__(self):
        return f"<Dispatcher {self.id}, {self.name}>"

    def __str__(self):
        return f"<Dispatcher {self.id}, {self.name}>"

    def to_dict(self):
        base_dict = Base.to_dict(self)
        data = {
            **base_dict
        }
        if self.dispatch_units:
            data['dispatch_units'] = [du.to_dict() for du in self.dispatch_units if du.status == 1]
        else:
            data['dispatch_units'] = []
        return data


def Get_start_dispatcher(agent_id):
    query = Dispatcher.query.filter(Dispatcher.agent_id == agent_id,
                                    Dispatcher.is_Start == 1,
                                    Dispatcher.status == 1)
    query = query.order_by(desc(Dispatcher.id))
    return query.first()


def Get_dispatcher_by_id(dispatcher_id):
    return Dispatcher.query.get(dispatcher_id)
