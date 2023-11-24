from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'mysecretkey'  # 设置一个密钥用于保护WebSocket通信
socketio = SocketIO(app, cors_allowed_origins="*")


# 初始化WebSocket连接
@socketio.on('connect')
def handle_connect():
    print("data:", request.query_string)
    task_id = request.args.get('task_id')
    print(f'Client connected to task {task_id}')
    print('WebSocket connected')


# 处理客户端发送的消息
@socketio.on('message')
def handle_message(message):
    print(f'Received message: {message}')
    # 发送消息给所有连接的客户端
    send(f'Server received: {message}', broadcast=True)


# 渲染网页
@app.route('/')
def index():
    return render_template('ws_index.html')


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001)
