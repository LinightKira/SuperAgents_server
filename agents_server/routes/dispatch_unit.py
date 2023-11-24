import json
from http import HTTPStatus

from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from agents_server import db
from agents_server.models.dispatch_unit import DispatchUnit
from agents_server.models.dispatcher import Dispatcher
from agents_server.vaildate.validate_dispatch_unit_data import validate_dispatch_unit_data

dispatch_unit_bp = Blueprint('dispatch_unit', __name__)


@dispatch_unit_bp.route('/dispatch_unit', methods=['POST'])
@jwt_required()
def create_dispatch_unit():
    try:
        data = request.get_json()
        return jsonify(create_dispatch_unit_in_data(data))
    except Exception as e:
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


def create_dispatch_unit_in_data(data):
    try:
        # 参数校验
        err = validate_dispatch_unit_data(data)
        # 如果err有内容
        if err is not None:
            return {"code": HTTPStatus.BAD_REQUEST, "msg": err}
        else:
            dispatchUnit = DispatchUnit(**data)
            dispatcher = Dispatcher.query.get(dispatchUnit.dispatcher_id)
            if not dispatcher or dispatcher.status == 0:
                return {"code": HTTPStatus.NOT_FOUND, "msg": "dispatcher not found."}
            uid = get_jwt_identity()
            if dispatcher.user_id != uid:
                return {"code": HTTPStatus.FORBIDDEN, "msg": "forbidden."}

            dispatchUnit.user_id = uid
            if dispatchUnit.next_action is not None:
                dispatchUnit.next_action = json.dumps(dispatchUnit.next_action)
            dispatchUnit.create()
            return {"code": HTTPStatus.OK, "msg": "success"}

    except Exception as e:
        db.session.rollback()
        return {"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)}


@dispatch_unit_bp.route('/dispatch_unit/<int:cid>', methods=['GET'])
@jwt_required()
def get_dispatch_unit(cid):
    try:
        dispatch_unit = DispatchUnit.query.get(cid)

        if not dispatch_unit or dispatch_unit.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "dispatch_unit not found."
            })

        uid = get_jwt_identity()
        if dispatch_unit.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "forbidden."})

        data = dispatch_unit.to_dict()

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


@dispatch_unit_bp.route('/dispatch_units/<int:cid>', methods=['GET'])
@jwt_required()
def get_dispatch_unit_list(cid):
    try:
        dispatcher = Dispatcher.query.get(cid)

        if not dispatcher or dispatcher.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "dispatcher not found."
            })

        uid = get_jwt_identity()
        if dispatcher.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "forbidden."})

        datas = DispatchUnit.query.filter_by(dispatcher_id=cid, status=1).all()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": [c.to_dict() for c in datas]
        })

    except Exception as e:
        return jsonify({
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "msg": str(e)
        })


@dispatch_unit_bp.route('/dispatch_unit', methods=['PUT'])
@jwt_required()
def update_dispatch_unit():
    try:
        data = request.get_json()
        return jsonify(update_dispatch_unit_in_data(data))
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


def update_dispatch_unit_in_data(data):
    try:
        aid = data.get('id')
        dispatch_unit = DispatchUnit.query.get(aid)

        if not dispatch_unit or dispatch_unit.status == 0:
            return{
                "code": HTTPStatus.NOT_FOUND,
                "msg": "agent not found."
            }

        err = ""
        uid = get_jwt_identity()
        if uid != dispatch_unit.user_id:
            err = "uid error."

        if uid != data.get('user_id'):
            err = "user_id error"

        if len(err) != 0:
            return {"code": HTTPStatus.BAD_REQUEST, "msg": err}

        # 必填校验
        err = validate_dispatch_unit_data(data)
        # 如果err有内容
        if err is not None:
            return {"code": HTTPStatus.BAD_REQUEST, "msg": err}

        dispatch_unit.query.filter_by(id=data.pop("id")).update(data)
        db.session.commit()

        return {
            "code": HTTPStatus.OK,
            "msg": "success",
        }

    except Exception as e:
        db.session.rollback()
        return {"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)}


@dispatch_unit_bp.route('/dispatch_unit/<int:aid>', methods=['DELETE'])
@jwt_required()
def delete_dispatch_unit(aid):
    try:
        dispatch_unit = DispatchUnit.query.get(aid)
        uid = get_jwt_identity()
        if not dispatch_unit or dispatch_unit.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "Permission denied"})

        # 逻辑删除角色
        dispatch_unit.status = 0
        db.session.commit()

        return jsonify({'code': HTTPStatus.OK, 'msg': 'agent deleted'})

    except Exception as e:

        db.session.rollback()

        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})
