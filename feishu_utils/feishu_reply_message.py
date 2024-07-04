import json

import requests

from feishu_utils.feishu_token_manager import token_manager


def reply_msg_text(message_id, msg, uuid=None):
    """
    回复指定消息

    Args:
        message_id (str): 待回复的消息ID
        msg (dict): 回复内容,JSON格式
        uuid (str, optional): 唯一字符串序列,用于请求去重,默认为None

    """
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
    token = token_manager.get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {
        "content": msg['content'],
        "msg_type": msg['msg_type'],
        "reply_in_thread": False
    }

    print('data:', data)
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
    # reply_msg_text("om_2d7e5990330ccdee040347023789401b", {"msg_type": "text", "content": "{\"text\":\"test content\"}"})
    reply_msg_text("om_2d7e5990330ccdee040347023789401b",  {'content': "{\"text\": \"你好！请问有什么我可以帮助你的吗？无论是查询信息、解决问题还是其他需求，请随时告诉我。\"}", 'msg_type': 'text', 'reply_in_thread': False})
# {'content': '{"zh_cn": {"content": [[{"tag": "text", "text": "星空图已经为你生成，请查看下图：\\n\\n![星空图](attachment://generated_image.png)"}], [{"tag": "img", "image_key": "/files/tools/695f03d3-71ae-4a9f-88cf-e85bf70e0d47.png?timestamp=1720086259&nonce=6209209ed77351e915d3398a6235adf2&sign=YLx3xx3EE_mpYg0LJ7tzVrB5N4Rmp_cDiJwNo6AM1OU="}]]}}'