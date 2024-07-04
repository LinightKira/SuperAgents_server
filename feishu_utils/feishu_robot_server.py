import json

import lark_oapi as lark
import requests

import config


def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    # print(f'[ do_p2_im_message_receive_v1 access ], data: {lark.JSON.marshal(data, indent=4)}')
    print('message id', data.event.message.message_id)
    print('content', data.event.message.content)
    send_msg_to_server(data.event.message.message_id, data.event.message.content)


# def do_message_event(data: lark.CustomizedEvent) -> None:
#     print(f'[ do_customized_event access ], type: message, data: {lark.JSON.marshal(data, indent=4)}')


# 初始化事件处理器（event_handler），两个参数建议填空字符串
# event_handler = lark.EventDispatcherHandler.builder("", "") \
#     .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
#     .register_p1_customized_event("message", do_message_event) \
#     .build()
event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1).build()


def feishu_robot_start():
    cli = lark.ws.Client(config.Config.FEISHU_ROBOT_APP_ID, config.Config.FEISHU_ROBOT_APP_SECRET,
                         event_handler=event_handler,
                         log_level=lark.LogLevel.DEBUG)
    cli.start()


def send_msg_to_server(message_id, content):
    url = f'{config.Config.SERVER_BASE_URL}assistant/main'  # 本地服务器地址
    headers = {'Content-Type': 'application/json'}  # 设定header信息
    payload = {
        'message_id': message_id,
        'content': content
    }

    print('send mes to server:', payload)

    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # 检查请求是否成功
        if response.status_code == 200:
            print('Success:', response.text)
        else:
            print('Failed:', response.text)

    except requests.exceptions.RequestException as e:
        print('An error occurred:', e)


if __name__ == "__main__":
    feishu_robot_start()
    send_msg_to_server("oc_a42bdfd8d242298ef167a018418cc172", "你好，你好")
