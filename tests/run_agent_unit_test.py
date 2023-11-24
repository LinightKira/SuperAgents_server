import sys

sys.path.append("..")
from agents_server import app
from agents_server.actions.run_agent_unit import RunAgentUnit
from agents_server.models.agent_unit import AgentUnit

with app.app_context():
    agent_unit = AgentUnit.query.get(1)
run_agent_unit = RunAgentUnit(agent_unit)
res, tokens = run_agent_unit.run()
print(res)
print("==============================")
print(tokens)
