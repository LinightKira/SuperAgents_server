from datetime import datetime

from agents_server.models.agent import Get_agent_byId
from agents_server.models.agent_task import Get_agentTask_byId


def validate_agent_task_data(data):
    if not data.get('agent_id'):
        return 'agent_id is required'
    if not data.get('name'):
        data["name"] = "task" + datetime.now().strftime("%Y%m%d%H%M%S")
    return None


def validate_agent_task_check_permission(agent_task, uid):
    agent = Get_agent_byId(agent_task.agent_id)
    if agent.user_id != uid:
        return 'uid error'
    return None


def validate_task_user_permission(task_id, uid):
    task = Get_agentTask_byId(task_id)
    if not task:
        return 'task not found'
    if task.user_id != uid:
        return 'uid error'
    return None
