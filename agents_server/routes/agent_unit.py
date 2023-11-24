# Agent相关路由
import json
from datetime import datetime
from http import HTTPStatus

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from agents_server import db
from agents_server.actions.run_agent_unit import RunAgentUnit
from agents_server.models.agent_unit import AgentUnit
from agents_server.vaildate.vaildate_agent_unit import validate_agent_unit_data

agent_unit_bp = Blueprint('agent_unit', __name__)


@agent_unit_bp.route('/agent_unit', methods=['POST'])
@jwt_required()
def create_agent_unit():
    try:
        data = request.get_json()
        # 参数校验
        err = validate_agent_unit_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})
        else:
            agent_unit = AgentUnit(**data)
            uid = get_jwt_identity()
            agent_unit.user_id = uid

            agent_unit.llm_config = json.dumps(agent_unit.llm_config)
            # print("agent_unit_llm_config:", type(agent_unit.llm_config))
            # print("agent_unit:", agent_unit.to_dict())
            agent_unit.create()
            return jsonify({"code": HTTPStatus.OK, "msg": "success"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@agent_unit_bp.route('/agent_unit/<int:aid>', methods=['GET'])
@jwt_required()
def get_agent_unit(aid):
    try:
        agent_unit = AgentUnit.query.get(aid)

        if not agent_unit or agent_unit.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "agent not found."
            })
        uid = get_jwt_identity()
        if agent_unit.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "forbidden."})

        data = agent_unit.to_dict()

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


@agent_unit_bp.route('/agent_unit', methods=['PUT'])
@jwt_required()
def update_agent_unit():
    try:
        data = request.get_json()

        aid = data.get('id')
        agent_unit = AgentUnit.query.get(aid)

        if not agent_unit or agent_unit.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "agent not found."
            })

        err = ""
        uid = get_jwt_identity()
        if uid != agent_unit.user_id:
            err = "uid error."

        if uid != data.get('user_id'):
            err = "user_id error"

        if len(err) != 0:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # 必填校验
        err = validate_agent_unit_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # Exclude create_time and update_time from the update
        data.pop("create_time", None)
        data.pop("update_time", None)

        agent_unit.query.filter_by(id=data.pop("id")).update(data)
        db.session.commit()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@agent_unit_bp.route('/agent_unit/<int:aid>', methods=['DELETE'])
@jwt_required()
def delete_agent_unit(aid):
    try:
        agent_unit = AgentUnit.query.get(aid)
        uid = get_jwt_identity()
        if not agent_unit or agent_unit.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "Permission denied"})

        # 逻辑删除角色
        agent_unit.status = 0
        db.session.commit()

        return jsonify({'code': HTTPStatus.OK, 'msg': 'agent deleted'})

    except Exception as e:

        db.session.rollback()

        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@agent_unit_bp.route('/agent_units', methods=['GET'])
@jwt_required()
def get_agent_units():
    try:
        uid = get_jwt_identity()
        last_id = request.args.get('last_id')
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category')

        # 查询条件应始终过滤状态
        query = AgentUnit.query.filter(AgentUnit.user_id == uid, AgentUnit.status > 0)

        # 设置排序方式为id降序
        query = query.order_by(desc(AgentUnit.id))
        # 分类查询
        if category:
            query = query.filter(AgentUnit.category == category)

        if last_id:
            # 根据last_id分页
            query = query.filter(AgentUnit.id < last_id)
            # 分页
        pagination = query.paginate(page=page, per_page=50)

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


# 运行一个Agent单元_测试用
@agent_unit_bp.route('/agent_unit/run', methods=['POST'])
@jwt_required()
def run_agent_unit():
    try:
        data = request.get_json()
        agentUnit_data = data.get('agentUnit')
        print('data:', data)
        # 参数校验
        err = validate_agent_unit_data(agentUnit_data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})
        else:
            agent_unit = AgentUnit(**agentUnit_data)
            uid = get_jwt_identity()
            if uid != agent_unit.user_id:
                return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "Permission denied"})

            # print('agent_unit.llm_config', agent_unit.llm_config)
            # print(type(agent_unit.llm_config))
        input_data = data.get('input_data')

        # 将时间格式化为字符串，例如：20230715143018
        task_id = 'agent_unit_test'
        # 创建AgentUnit运行实例
        runAU = RunAgentUnit(task_id, agent_unit, '', '', input_data)

        # 运行AgentUnit
        res, tokens = runAU.run()

        return jsonify({"code": HTTPStatus.OK, "msg": "success", "datas": {'res': res, 'tokens': tokens}})

    except Exception as e:

        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})
