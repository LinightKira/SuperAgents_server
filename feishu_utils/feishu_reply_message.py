import json

import requests

from feishu_utils.feishu_token_manager import token_manager


def reply_msg_text(message_id, msg, uuid=None):
    """
    回复指定消息

    Args:
        message_id (str): 待回复的消息ID
        msg (str): 回复内容,JSON格式
        uuid (str, optional): 唯一字符串序列,用于请求去重,默认为None

    """
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
    token = token_manager.get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    msgContent = {
        "text": msg,
    }
    data = {
        "content": json.dumps(msgContent),
        "msg_type": "text",
        "reply_in_thread": False
    }
    if uuid:
        data["uuid"] = uuid

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


if __name__ == '__main__':
    reply_msg_text("om_15906ac45608f5c244f7c81dde828019", "真是有意思")
