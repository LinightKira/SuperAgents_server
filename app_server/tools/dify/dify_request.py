import json

import requests

import config
from feishu_utils.feishu_upload_image import upload_image

"""
Generate a POST request to the DIFY API based on the provided API key, payload, and mode.

Parameters:
- api_key (str): The API key for authentication.
- payload (dict): The data to be sent in the request body.
- mode (str): The mode of the request, either 'completion' or 'chat'.

Returns:
- response: The response object from the POST request.
"""


def make_dify_request(api_key, payload, mode='chat'):
    base_url = config.Config.DIFY_BASE_URL

    if mode == 'completion':
        url = base_url + 'completion-messages'
    elif mode == 'chat':
        url = base_url + 'chat-messages'
    else:
        raise ValueError("Invalid mode. Use 'completion' or 'chat'.")

    isStreaming = payload.get('response_mode') == 'streaming'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    # print('payload:', payload)
    # print('headers:', headers)
    # print('dify url:', url)

    response = requests.post(url, headers=headers, json=payload, stream=isStreaming)

    return response


def response_streaming(response):
    content = ''
    incomplete_chunk = b''  # 保存上一个不完整的数据块
    for chunk in response.iter_content(chunk_size=1024):
        # print('chunk:', chunk)
        # 合并上一个不完整的数据块和当前数据块
        # print(chunk)
        data = incomplete_chunk + chunk
        try:
            # 将字节字符串解码为普通字符串
            decoded_data = chunk.decode('utf-8')

            # 从字符串中提取 JSON 部分
            json_data_start = decoded_data.find('{')
            json_data_end = decoded_data.rfind('}') + 1
            json_data = decoded_data[json_data_start:json_data_end]

            # 解析 JSON 数据
            parsed_data = json.loads(json_data)

            # 获取 answer
            answer = parsed_data.get('answer', '')
            if answer:
                content += answer
        except json.decoder.JSONDecodeError:
            # 如果解码失败，说明数据块不完整，保存当前数据块以备下一次使用
            incomplete_chunk = data
        else:
            # 如果解码成功，说明数据块完整，清空不完整的数据块
            incomplete_chunk = b''
    print('content:', content)
    return content


def parse_response(response):
    # 获取response的文本内容
    response_text = response.text
    print('response_text:', response_text)
    conversation_id = None

    # 分割并解析每行JSON数据
    answers = []
    images = []
    for line in response_text.strip().split('\n'):
        if line.startswith('data: '):
            json_data = json.loads(line[6:])
            if 'conversation_id' in json_data and conversation_id is None:
                conversation_id = json_data['conversation_id']
            if 'answer' in json_data:
                answers.append(json_data['answer'])
            if json_data.get('event') == 'message_file':
                images.append(json_data['url'])

    if config.Config.SESSION_ID == '':
        config.Config.SESSION_ID = conversation_id

    # 拼接所有的answer
    full_answer = ''.join(answers)

    if images:
        # 生成富文本内容
        content = []
        if full_answer:
            content.append([{"tag": "text", "text": full_answer}])
        for img_url in images:
            res = upload_image(config.Config.DIFY_HOST + img_url)

            # 解析JSON字符串
            res_dict = json.loads(res)

            # 检查code的值
            if res_dict["code"] == 0:
                content.append([{"tag": "img", "image_key": res_dict['data']['image_key']}])
            else:
                print(f"code: {res_dict['code']}, msg: {res_dict['msg']}")
                content.append([{"tag": "text", "text": f"code: {res_dict['code']}, msg: {res_dict['msg']}"}])

        full_content = json.dumps({
            "zh_cn": {
                "content": content
            }
        }, ensure_ascii=False)

        msgContent = {
            "msg_type": "post",
            "content": full_content
        }
    else:
        full_answer = json.dumps({"text": full_answer}, ensure_ascii=False)
        msgContent = {
            "msg_type": "text",
            "content": full_answer
        }

    print('msgContent:', msgContent)

    return msgContent
