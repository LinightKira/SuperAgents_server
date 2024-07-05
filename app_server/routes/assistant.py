# 聊天主题部分
# @Time: 2024/5/17 20:38
# @Author: 宏伟（散人）
# @File: assistant.py
# @Description:修改了聊天逻辑，改为先聊天，再做意图识别
import asyncio
import json
import threading
from http import HTTPStatus

from flask import request, jsonify, Blueprint

from app_server.tools.dify.dify_request import make_dify_request, response_streaming, parse_response
from config import Config
from app_server.db import mgdb
from feishu_utils.feishu_reply_message import reply_msg_text

assistant_bp = Blueprint('assistant', __name__)


@assistant_bp.route('/assistant/main', methods=['POST'])
def assistant_main():
    print('assistant main:=======================')
    try:
        data = request.get_json()
        input_data = data.get('content')
        if not input_data:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "input is empty."})
        msg_id = data.get('message_id')
        if not msg_id:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "msg_id is empty."})

        t = threading.Thread(target=run_async, args=(assistant_input_process, input_data, msg_id))
        t.start()

        # assistant_input_process(input_data,msg_id)
        return jsonify({"code": HTTPStatus.OK, "msg": "success"})

    except Exception as e:
        print('start agent error:', str(e))
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


# 处理用户输入
async def assistant_input_process(input_data, msg_id):
    print('input_data:', input_data)
    if input_data == '{"text":"clean"}':
        Config.SESSION_ID = ''
        msgContent = {
            "msg_type": "text",
            "content": 'done'
        }
        reply_msg_text(msg_id, msgContent)
        return

    api_key = Config.DIFY_AGENT_KEY
    # 构造请求参数
    payload = {
        "inputs": {},
        "query": input_data,
        "response_mode": "streaming",
        "conversation_id": Config.SESSION_ID,
        "user": "123456"
    }
    # 请求参数分类
    response = make_dify_request(api_key, payload)
    if response.status_code != HTTPStatus.OK:
        print('response status_code:', response.status_code)
        print('response:', response.text)
        return

    # final_answer = response_streaming(response)
    final_answer = parse_response(response)

    print('response answer:', final_answer)
    mgdb.create_message(Config.SESSION_ID, {'type': 'text', 'content': input_data, 'role': 'user'})
    reply_msg_text(msg_id, final_answer)
    mgdb.create_message(Config.SESSION_ID, {'type': final_answer['msg_type'], 'content': final_answer['content'], 'role': 'assistant'})


# 处理多线程运行异步函数
def run_async(func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(func(*args))
    finally:
        loop.close()
