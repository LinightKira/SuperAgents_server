import sys

sys.path.append("..")

from agents_server.llm.openai_api import OpenaiApi

messages = [
    {"role": "system", "content": """You are my CEO, I am your employee."""},
    {"role": "user", "content": """今天是我入职的第一天，有什么工作要安排给我吗？"""},
]

runLLM = OpenaiApi(messages=messages)

res, tokens = runLLM.get_completion_and_token_count()
print(res)
print("==============================")
print(tokens)
