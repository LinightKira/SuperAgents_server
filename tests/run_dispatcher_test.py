import sys

sys.path.append("..")
from agents_server import app, db
from agents_server.actions.run_dispatcher import RunDispatcher
from agents_server.models.dispatcher import Dispatcher

with app.app_context():
    dispatcher = db.session.query(Dispatcher).get(1)
    print("disUnit:",dispatcher.dispatch_units)
    print(dispatcher)
    runer = RunDispatcher(dispatcher)
    runer.run()



