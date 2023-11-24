# Agent相关路由
from http import HTTPStatus

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from agents_server import db
from agents_server.models.agent import Agent
from agents_server.vaildate.vaildate_agent import validate_agent_data

agent_bp = Blueprint('agent', __name__)


@agent_bp.route('/agents', methods=['POST'])
@jwt_required()
def create_agent():
    try:
        data = request.get_json()

        # 参数校验
        err = validate_agent_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})
        else:
            agent = Agent(**data)
            uid = get_jwt_identity()
            agent.user_id = uid

            agent.create()
            return jsonify({"code": HTTPStatus.OK, "msg": "success", "datas": agent.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@agent_bp.route('/agents/<int:aid>', methods=['GET'])
@jwt_required()
def get_agent(aid):
    try:
        agent = Agent.query.get(aid)

        if not agent or agent.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "agent not found."
            })

        uid = get_jwt_identity()
        if agent.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "forbidden."})

        data = agent.to_dict()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": data
        })

    except Exception as e:
        return jsonify({
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "msg": str(e)
        })


@agent_bp.route('/agents/', methods=['PUT'])
@jwt_required()
def update_agent():
    try:
        data = request.get_json()
        aid = data.get('id')
        agent = Agent.query.get(aid)

        if not agent or agent.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "agent not found."
            })

        err = ""
        uid = get_jwt_identity()
        if uid != agent.user_id:
            err = "uid error."

        if uid != data.get('user_id'):
            err = "user_id error"

        if len(err) != 0:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # 必填校验
        err = validate_agent_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # Exclude create_time and update_time from the update
        data.pop("create_time", None)
        data.pop("update_time", None)

        agent.query.filter_by(id=data.pop("id")).update(data)
        db.session.commit()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@agent_bp.route('/agents/<int:cid>', methods=['DELETE'])
@jwt_required()
def delete_agent(aid):
    try:
        agent = Agent.query.get(aid)
        uid = get_jwt_identity()
        if not agent or agent.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "Permission denied"})

        # 逻辑删除角色
        agent.status = 0
        db.session.commit()

        return jsonify({'code': HTTPStatus.OK, 'msg': 'agent deleted'})

    except Exception as e:

        db.session.rollback()

        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@agent_bp.route('/agents', methods=['GET'])
@jwt_required()
def get_agents():
    try:
        uid = get_jwt_identity()
        last_id = request.args.get('last_id')
        page = request.args.get('page', 1, type=int)

        # 查询条件应始终过滤状态
        query = Agent.query.filter(Agent.user_id == uid, Agent.status > 0)

        # 设置排序方式为id降序
        query = query.order_by(desc(Agent.id))

        if last_id:
            # 根据last_id分页
            query = query.filter(Agent.id < last_id)
            # 分页
        pagination = query.paginate(page=page, per_page=10)

        agents = pagination.items

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": {
                'agents': [c.to_dict() for c in agents],
                'page': page,
                'total': pagination.pages
            }
        })
    except Exception as e:
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})
