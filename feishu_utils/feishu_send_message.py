import json
import requests

from feishu_utils.feishu_token_manager import token_manager


def send_msg_text(chat_id,msg):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "chat_id"}
    msg = msg
    msgContent = {
        "text": msg,
    }
    req = {
        "receive_id": chat_id,  # chat id
        "msg_type": "text",
        "content": json.dumps(msgContent)
    }
    payload = json.dumps(req)
    token = token_manager.get_token()
    headers = {
        'Authorization': f'Bearer {token}',  # your access token
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    print(response.headers['X-Tt-Logid'])  # for debug or oncall
    print(response.content)  # Print Response


if __name__ == '__main__':
    send_msg_text("oc_a42bdfd8d242298ef167a018418cc172","你好，你好")
