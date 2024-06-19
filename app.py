import threading

from app_server import app
from feishu_utils.feishu_robot_server import feishu_robot_start

if __name__ == '__main__':
    # 开一个线程 处理消息
    t = threading.Thread(target=feishu_robot_start)  # 传入参数
    t.start()
    # app.run(port=5000, debug=True,host="0.0.0.0",ssl_context=('fssl.pem', 'fssl.key'))
    app.run(port=5000, debug=True, host="0.0.0.0")

