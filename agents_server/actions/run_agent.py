"""
@Time        : 2023/9/15 9:36
@Author      : LinightX
@File        : run_agent.py
@Description : 运行一个Agent
"""
import os

from agents_server.actions.agent_data import AgentDate
from agents_server.actions.common_data import task_running_status
from agents_server.actions.run_dispatcher import RunDispatcher
from agents_server.logger import logger_runner
from agents_server.memory.message import CreateMilvusCollection
from agents_server.models.agent import Agent
from agents_server.models.agent_task import AgentTask, AgentTasks_Start
from agents_server.models.dispatcher import Get_start_dispatcher


# 运行一个Agent
class RunAgent(AgentDate):
    def __init__(self, agent_task: AgentTask, agent: Agent):
        # 创建工作区
        # 定义工作目录
        work_dir = f'./workspace/{agent_task.id}'

        # 判断目录是否存在
        if not os.path.exists(work_dir):
            # 目录不存在,创建目录
            os.makedirs(work_dir)
            logger_runner.info(f'工作目录 {work_dir} 创建成功')
        else:
            # 目录已存在
            logger_runner.info(f'工作目录 {work_dir} 已存在')
        super().__init__(work_dir)
        self.task = agent_task
        self.agent = agent

    def start(self):
        try:
            logger_runner.info(f'{self.task.id}-{self.task.name}-{self.agent.name} start running')
            # 创建全局上下文向量库 向量库名称为 task_id
            CreateMilvusCollection(self.task.id, self.agent.name)
            # 找第一个调度 让调度开始上班
            dispatcher = Get_start_dispatcher(self.agent.id)
            if dispatcher:
                AgentTasks_Start(self.task.id)
                task_running_status[self.task.id] = True
                RunDispatcher(self.task.id, dispatcher, self.workspace, self.task.input_data).run()

            else:
                logger_runner.error(f'{self.task.id}-{self.task.name}-{self.agent.name} has no start_dispatcher')
        except Exception as e:
            logger_runner.error("RunAgent.start error:", e, exc_info=True)
