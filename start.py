from agents_server import app, socketio

if __name__ == '__main__':
    # agents_server.run(port=5000, debug=True,host="0.0.0.0",ssl_context=('fssl.pem', 'fssl.key'))
    # app.run(port=5000, debug=True, host="0.0.0.0")
    socketio.run(app, port=5000, host='0.0.0.0', debug=True)
