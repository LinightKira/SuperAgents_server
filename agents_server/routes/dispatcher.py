# dispatcher相关路由
from http import HTTPStatus

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from agents_server import db
from agents_server.models.agent import Agent
from agents_server.models.dispatch_unit import DispatchUnit
from agents_server.models.dispatcher import Dispatcher
from agents_server.routes.dispatch_unit import create_dispatch_unit_in_data, update_dispatch_unit_in_data
from agents_server.vaildate.vaildate_dispatcher import validate_dispatcher_data

dispatcher_bp = Blueprint('dispatcher', __name__)


@dispatcher_bp.route('/dispatcher', methods=['POST'])
@jwt_required()
def create_dispatcher():
    try:
        data = request.get_json()
        # 参数校验
        err = validate_dispatcher_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})
        else:
            # # 检查字典中是否存在 'dispatch_units' 键
            # if 'dispatch_units' in data:
            #     # 如果存在，删除该键(不然有Bug)
            #     data.pop('dispatch_units')
            dispatcher = Dispatcher(**data)
            agent = Agent.query.get(data['agent_id'])
            if not agent or agent.status == 0:
                return jsonify({"code": HTTPStatus.NOT_FOUND, "msg": "agent not found."})
            uid = get_jwt_identity()
            if agent.user_id != uid:
                return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "forbidden."})

            dispatcher.user_id = uid
            dispatcher.create()

            return jsonify({"code": HTTPStatus.OK, "msg": "success"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@dispatcher_bp.route('/dispatcher/<int:did>', methods=['GET'])
@jwt_required()
def get_dispatcher(did):
    try:
        dispatcher = Dispatcher.query.get(did)

        if not dispatcher or dispatcher.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "dispatcher not found."
            })

        uid = get_jwt_identity()
        if dispatcher.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "forbidden."})

        data = dispatcher.to_dict()

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


@dispatcher_bp.route('/dispatcher', methods=['PUT'])
@jwt_required()
def update_dispatcher():
    try:
        data = request.get_json()
        print('data:', data)

        # Exclude create_time and update_time from the update
        data.pop("create_time", None)
        data.pop("update_time", None)

        dispatch_units = data.pop('dispatch_units', None)

        aid = data.get('id')
        dispatcher = Dispatcher.query.get(aid)

        if not dispatcher or dispatcher.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "dispatcher not found."
            })

        err = ""
        uid = get_jwt_identity()
        if uid != dispatcher.user_id:
            err = "uid error."

        if uid != data.get('user_id'):
            err = "user_id error"

        if len(err) != 0:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # 必填校验
        err = validate_dispatcher_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        dispatcher.query.filter_by(id=data.pop("id")).update(data)
        db.session.commit()

        # 更新dispatch_units
        if dispatch_units:
            for dispatch_unit_data in dispatch_units:
                dispatch_unit_data.pop('create_time', None)
                dispatch_unit_data.pop('update_time', None)
                dispatch_unit_data.pop('agent_unit')
                if dispatch_unit_data.get('id') == 0:
                    res = create_dispatch_unit_in_data(dispatch_unit_data)
                else:
                    res = update_dispatch_unit_in_data(dispatch_unit_data)

                if res["code"] != HTTPStatus.OK:
                    return jsonify(res)

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@dispatcher_bp.route('/dispatcher/set_start', methods=['PUT'])
@jwt_required()
def update_dispatcher_set_start():
    try:
        data = request.get_json()
        did = data.get('id')
        dispatcher = Dispatcher.query.get(did)

        if not dispatcher or dispatcher.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "dispatcher not found."
            })

        uid = get_jwt_identity()
        if uid != dispatcher.user_id:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "forbidden."})

        # 将dispatcher.agent_id下的所有is_Start设置为False
        dispatcher.query.filter_by(agent_id=dispatcher.agent_id, is_Start=True).update({"is_Start": False})
        # 将is_Start设置为True
        dispatcher.query.filter_by(id=did).update({"is_Start": True})
        db.session.commit()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@dispatcher_bp.route('/dispatcher', methods=['DELETE'])
@jwt_required()
def delete_dispatcher():
    try:
        data = request.get_json()
        aid = data.get('id')
        dispatcher = Dispatcher.query.get(aid)
        uid = get_jwt_identity()
        if not dispatcher or dispatcher.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "Permission denied"})

        # 逻辑删除角色
        dispatcher.status = 0
        db.session.commit()

        return jsonify({'code': HTTPStatus.OK, 'msg': 'dispatcher deleted'})

    except Exception as e:

        db.session.rollback()

        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


# AgentID下的全部调度
@dispatcher_bp.route('/dispatchers/<int:aid>', methods=['GET'])
@jwt_required()
def get_dispatchers(aid):
    try:
        uid = get_jwt_identity()
        agent = Agent.query.get(aid)
        if not agent:
            return jsonify({"code": HTTPStatus.NOT_FOUND, "msg": "agent not found."})

        if agent.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "Permission denied"})

            # 查询条件应始终过滤状态
        query = Dispatcher.query.filter(Dispatcher.agent_id == aid, Dispatcher.status > 0)

        # 设置排序方式为从起始节点开始
        query = query.order_by(desc(Dispatcher.is_Start))

        dispatchers = query.all()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": {
                'dispatchers': [c.to_dict() for c in dispatchers],
            }
        })
    except Exception as e:
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})
