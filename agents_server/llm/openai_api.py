# 支持Messages 和 token 统计
import openai

from agents_server.logger import logger_runner


class OpenaiApi(object):
    def __init__(self, messages=None):
        if messages is None:
            messages = []
        self.Messages = messages

    def addSystemMessage(self, msg):
        self.Messages.append({"role": "system", "content": msg})

    def addUserMessage(self, msg):
        self.Messages.append({"role": "user", "content": msg})

    def addAssistantMessage(self, msg):
        self.Messages.append({"role": "assistant", "content": msg})

    def get_completion_and_token_count(
            self, model="gpt-3.5-turbo", temperature=0.5, max_tokens=500
    ):
        if len(self.Messages) == 0:
            return "Messages is empty", {}

        res = openai.ChatCompletion.create(
            model=model,
            messages=self.Messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        logger_runner.info(f'model:{model} messages:{self.Messages} temperature:{temperature} max_tokens:{max_tokens}')

        content = res.choices[0].message["content"]

        tokens = {
            "prompt_tokens": res["usage"]["prompt_tokens"],
            "completion_tokens": res["usage"]["completion_tokens"],
            "total_tokens": res["usage"]["total_tokens"],
        }

        logger_runner.info(f'content:{content} tokens:{tokens}')

        return content, tokens
