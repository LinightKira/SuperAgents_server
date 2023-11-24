from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import emit, Namespace, disconnect, join_room, SocketIO, send

from agents_server.actions.common_data import task_running_status, task_input_data
from agents_server.vaildate.vaildate_agent_task import validate_task_user_permission

# 注册websocket
socketio = SocketIO(cors_allowed_origins="*")


@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    print("default_error_handler:", e)
    send({'error': str(e)})
    disconnect()


@socketio.on('connect')
def connect_handler(namespace):
    if namespace != '/agents_running':
        return False  # 拒绝连接


class AgentsRunningNamespace(Namespace):
    @staticmethod
    @jwt_required()
    def on_connect():
        task_id = request.args.get('task_id')
        if not task_id:
            # 没有task_id,拒绝
            return False
        # task_id与user的权限校验
        uid = get_jwt_identity()
        err = validate_task_user_permission(task_id, uid)
        if err is not None:
            return False
        # task_id存在,加入房间
        join_room(task_id)
        print(f'Client connected to room {task_id}')

    @staticmethod
    def on_disconnect():
        print('Client disconnected')

    @staticmethod
    @jwt_required()
    def on_next_agent(data):

        # 检查task_id
        task_id = request.args.get('task_id')
        if not task_id:
            # 没有task_id,拒绝
            emit('res', {'error': 'no task id'})
            return
            # task_id与user的权限校验
        uid = get_jwt_identity()
        err = validate_task_user_permission(task_id, uid)
        if err is not None:
            emit('res', {'error': err})
            return False
        if task_id != data.get('task_id'):
            # 房间不匹配
            emit('res', {'error': 'wrong task id'})
            return

        # 校验通过,获取input
        input_data = data.get('data')
        print(f'Received data: {input_data}')

        # TODO: 处理input
        task_input_data[task_id] = input_data
        task_running_status[task_id] = True

        # 返回结果
        emit('res', {'result': 'success'})
        print('Client sent message(next agent): ' + str(data))

    @staticmethod
    def on_join(data):
        room = data['task_id']
        join_room(room)

    # @staticmethod
    # def on_my_event(data):
    #     emit('my_response', data)
    #     print('Client sent message: ' + str(data))


socketio.on_namespace(AgentsRunningNamespace('/agents_running'))
