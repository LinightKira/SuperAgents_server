"""
@Time        : 2023/9/14 15:43
@Author      : LinightX
@File        : run_agent_unit.py
@Description : 运行一个Agent单元，需要输入AgentUnit和输入的数据
"""
import json

from agents_server.actions.agent_data import AgentDate
from agents_server.llm.openai_api import OpenaiApi
from agents_server.logger import logger_runner
from agents_server.memory.message import MakeMilvusCollection, SaveMsgsToMilvus
from agents_server.models.agent_unit import AgentUnit


# 运行一个Agent单元
class RunAgentUnit(AgentDate):
    def __init__(self, task_id, agent_unit: AgentUnit, workspace, settings=None, in_data=None):
        super().__init__(workspace)
        self.agent_unit = agent_unit
        self.task_id = task_id
        self.settings = settings
        self.in_data = in_data

    def run(self):
        # 创建一个LLM运行实例
        # 未补充：根据不同的LLM配置参数选择不同的调用模型
        runLLM = OpenaiApi()
        runLLM.addSystemMessage(self.agent_unit.prompt)

        # 输入的数据需要结构化处理 未完成
        if self.in_data:
            runLLM.addUserMessage(self.in_data)

        logger_runner.info(f'{self.agent_unit.name}:start running')

        llm_config_str = self.agent_unit.llm_config
        llm_config = json.loads(llm_config_str)

        # 获取LLM设置
        llm_model = llm_config.get("model", "gpt-3.5-turbo")
        temperature = llm_config.get("temperature", 0.5)
        max_tokens = llm_config.get("max_tokens", 100)

        # 运行请求LLM
        res, tokens = runLLM.get_completion_and_token_count(llm_model, temperature, max_tokens)
        logger_runner.info(f'{self.agent_unit.name}:end running')
        runLLM.addAssistantMessage(res)
        # 公共记忆保存
        print("runLLM:", runLLM.Messages)
        if self.task_id != 'agent_unit_test':
            self.saveToMilvus(runLLM.Messages)
        return res, tokens

    # 保存消息到数据库
    def saveToMilvus(self, msg_list):
        col = MakeMilvusCollection(self.task_id)
        SaveMsgsToMilvus(col, msg_list)
