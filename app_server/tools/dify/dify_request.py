import json

import requests

import config

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

    # print('url:', url)

    isStreaming = payload.get('response_mode') == 'streaming'
    # print('isStreaming:', isStreaming)

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    # print('payload:', payload)
    # print('headers:', headers)
    # print('url:', url)
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
