# Agent
import uuid
from datetime import datetime

import shortuuid

from agents_server.db import db, Base


class AgentTask(Base):
    id = db.Column(db.String(50), primary_key=True, unique=True, nullable=False, comment="主键")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment="所属用户ID")
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), comment="Agent ID")
    name = db.Column(db.String(50), comment="任务名字")
    description = db.Column(db.String(200), comment="任务说明")
    start_time = db.Column(db.DateTime, comment="任务开始时间")
    end_time = db.Column(db.DateTime, comment="任务结束时间")
    running_status = db.Column(db.Integer, comment="运行状态", default=0)  # 0:未运行 1:运行中 2:已完成 3:已暂停 4:已终止
    input_data = db.Column(db.Text, comment="输入数据")
    output_data = db.Column(db.Text, comment="输出数据")


# 查询
def Get_agentTask_byId(task_id):
    return AgentTask.query.get(task_id)


def Delete_agentTask_byId(task_id):
    return AgentTask.query.filter_by(id=task_id).set({"status": 0})


# 查询条件
def Find_agentTasks(**filters):
    return AgentTask.query.filter_by(**filters)


# tasks = find_agentTasks(agent_id=123, status=1)

def AgentTasks_Start(task_id):
    return AgentTask.query.filter_by(id=task_id).update({"running_status": 1, "start_time": datetime.now()})


def AgentTasks_End(task_id):
    return AgentTask.query.filter_by(id=task_id).update({"running_status": 2, "end_time": datetime.now()})


def AgentTasks_Pause(task_id):
    return AgentTask.query.filter_by(id=task_id).update({"running_status": 3})


def AgentTasks_Stop(task_id):
    return AgentTask.query.filter_by(id=task_id).update({"running_status": 4})
