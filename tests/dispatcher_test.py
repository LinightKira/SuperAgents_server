import sys

sys.path.append("..")
from agents_server import app
from agents_server.models.dispatcher import Get_start_dispatcher

with app.app_context():
    dispatcher = Get_start_dispatcher(1)
    print(dispatcher)