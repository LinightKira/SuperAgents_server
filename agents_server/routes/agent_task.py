# Agent相关路由
import uuid
from http import HTTPStatus

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from agents_server import db
from agents_server.actions.run_agent import RunAgent
from agents_server.models.agent import Get_agent_byId
from agents_server.models.agent_task import AgentTask, Get_agentTask_byId, Delete_agentTask_byId, AgentTasks_Start
from agents_server.vaildate.vaildate_agent_task import validate_agent_task_data, validate_agent_task_check_permission

agent_task_bp = Blueprint('agent_task', __name__)


@agent_task_bp.route('/agent_task', methods=['POST'])
@jwt_required()
def create_agent_task():
    try:
        data = request.get_json()
        # 参数校验
        err = validate_agent_task_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})
        else:
            agent_task = AgentTask(**data)
            uid = get_jwt_identity()
            agent_task.user_id = uid
            # 运行权限校验 目前用户只能运行自己的Agent
            err = validate_agent_task_check_permission(agent_task, uid)
            if err is not None:
                return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": err})

            # ID做一次格式转换，因为向量数据库库的Name不支持”-“
            agent_task.id = str(uuid.uuid4())
            agent_task.id = agent_task.id.replace("-", "_")

            agent_task.create()
            return jsonify({"code": HTTPStatus.OK, "msg": "success"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@agent_task_bp.route('/agent_task/<int:aid>', methods=['GET'])
@jwt_required()
def get_agent_task(aid):
    try:
        agent_task = Get_agentTask_byId(aid)

        if not agent_task or agent_task.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "agent not found."
            })
        uid = get_jwt_identity()
        if agent_task.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "forbidden."})

        data = agent_task.to_dict()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "data": data
        })

    except Exception as e:
        return jsonify({
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "msg": str(e)
        })


@agent_task_bp.route('/agent_task', methods=['PUT'])
@jwt_required()
def update_agent_task():
    try:
        data = request.get_json()
        aid = data.get('id')
        agent_task = Get_agentTask_byId(aid)

        if not agent_task or agent_task.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "agent not found."
            })

        err = ""
        uid = get_jwt_identity()
        if uid != agent_task.user_id:
            err = "uid error."

        if uid != data.get('user_id'):
            err = "user_id error"

        if len(err) != 0:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # 必填校验
        err = validate_agent_task_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # 运行权限校验 目前用户只能运行自己的Agent
        err = validate_agent_task_check_permission(agent_task, uid)
        if err is not None:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": err})

        agent_task.query.filter_by(id=data.pop("id")).update(data)
        db.session.commit()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@agent_task_bp.route('/agent_task/<int:aid>', methods=['DELETE'])
@jwt_required()
def delete_agent_task(aid):
    try:
        agent_task = Get_agentTask_byId(aid)
        uid = get_jwt_identity()
        if not agent_task or agent_task.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "Permission denied"})

        # 逻辑删除角色
        Delete_agentTask_byId(aid)

        return jsonify({'code': HTTPStatus.OK, 'msg': 'agent deleted'})

    except Exception as e:

        db.session.rollback()

        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@agent_task_bp.route('/agent_tasks', methods=['GET'])
def get_agent_tasks():
    try:
        uid = request.args.get('uid')
        last_id = request.args.get('last_id')
        page = request.args.get('page', 1, type=int)

        # 查询条件应始终过滤状态
        query = AgentTask.query.filter(AgentTask.user_id == uid, AgentTask.status > 0)

        # 设置排序方式为id降序
        query = query.order_by(desc(AgentTask.id))
        # 状态查询

        if last_id:
            # 根据last_id分页
            query = query.filter(AgentTask.id < last_id)
            # 分页
        pagination = query.paginate(page=page, per_page=20)

        tasks = pagination.items

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": {
                'agents': [c.to_dict() for c in tasks],
                'page': page,
                'total': pagination.pages
            }
        })
    except Exception as e:
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


# 运行一个Agent任务
@agent_task_bp.route('/agent_task/start', methods=['PUT'])
@jwt_required()
def start_agent_task():
    try:
        data = request.get_json()
        aid = data.get('id')
        if aid is None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "agent id required."})
        agent_task = Get_agentTask_byId(aid)

        if not agent_task or agent_task.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "task not found."
            })

        uid = get_jwt_identity()
        if uid != agent_task.user_id:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "forbidden."})

        # 运行Agent 0:未运行 1:运行中 2:已完成 3:已暂停 4:已终止
        if agent_task.running_status == 1:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "agent task is running."})
        elif agent_task.running_status == 2:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "agent task has been completed."})
        elif agent_task.running_status == 3:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "agent task has been paused."})
        elif agent_task.running_status == 4:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "agent task has been terminated."})

        # 启动任务
        # 创建运行实例
        agent = Get_agent_byId(agent_task.agent_id)

        if agent is None or agent.status == 0:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "agent not found."})

        runner = RunAgent(agent_task, agent)
        runner.start()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})
