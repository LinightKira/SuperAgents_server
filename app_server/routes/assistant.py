# 聊天主题部分
# @Time: 2024/5/17 20:38
# @Author: 宏伟（散人）
# @File: assistant.py
# @Description:修改了聊天逻辑，改为先聊天，再做意图识别
import asyncio
import json
import re
import threading
from http import HTTPStatus

from flask import request, jsonify, Blueprint

import config
from app_server.tools.dify.dify_request import make_dify_request, response_streaming, parse_response
from app_server.tools.file_tools import write_file, delete_file
from config import Config
from app_server.db import mgdb
from feishu_utils.feishu_reply_message import reply_msg_text
from feishu_utils.feishu_upload_files import upload_files

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
            "content": json.dumps({"text": "done"}, ensure_ascii=False)
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
    mgdb.create_message(Config.SESSION_ID,
                        {'type': final_answer['msg_type'], 'content': final_answer['content'], 'role': 'assistant'})


@assistant_bp.route('/assistant/upload-feishu-file', methods=['POST'])
def assistant_upload_feishu_file():
    print('assistant upload feishu file:=======================')
    try:

        raw_data = request.data
        # print('Raw data:', raw_data)

        data = clean_request_data(raw_data)
        print('Cleaned data:', data)

        # data = request.json
        # print('data:', data)
        input_data = data.get('content')
        title = data.get('title')
        if not input_data:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "input is empty."})

        file_path = write_file(config.Config.WORKSPACE_DIR, f"{title}.md", input_data.encode('utf-8'))

        response = upload_files(file_path, config.Config.FEISHU_ROBOT_UPLOAD_FOLDER_TOKEN)

        if response.code == 0:
            file_token = response.data.file_token
            delete_file(file_path)
            return jsonify({"code": HTTPStatus.OK, "msg": "success",
                            "data": f"[{title}](https://uxsxrugqmxi.feishu.cn/file/{file_token})"})
        else:
            print('response code:', response.code)
            print('response msg:', response.msg)
        return jsonify({"code": HTTPStatus.OK, "msg": response.msg})

    except Exception as e:
        print('start agent error:', str(e))
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


# 处理多线程运行异步函数
def run_async(func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(func(*args))
    finally:
        loop.close()


def clean_request_data(data):
    # 去除尾部的换行符
    cleaned_data = data.rstrip(b'\n')

    # 将字节数据转换为字符串
    cleaned_data_str = cleaned_data.decode('utf-8')
    # 替换未转义的控制字符，保持换行符和其他格式字符
    cleaned_data_str = re.sub(r'[\x00-\x1f\x7f]', lambda match: '\\n' if match.group(0) == '\n' else '',
                              cleaned_data_str)

    print('cleaned_data_str:', cleaned_data_str)

    # 解析 JSON 数据
    json_data = json.loads(cleaned_data_str)

    return json_data
