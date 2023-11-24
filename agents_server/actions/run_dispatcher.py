# -*- coding: utf-8 -*-
"""
@Time        : 2023/10/10 23:08
@Author      : LinightX
@File        : run_dispatcher.py
@Description : 运行一个调度员，遍历调度员下的所有AgentUnit 自动运行下一个AgentUnit(未完成）
"""
import json
import time

from jinja2 import Template

from agents_server.actions.agent_data import AgentDate
from agents_server.actions.common_data import task_running_status, task_input_data
from agents_server.actions.run_agent_unit import RunAgentUnit
from agents_server.logger import logger_runner
from agents_server.models.agent_unit import GetAgentUnitById
from agents_server.models.dispatcher import Dispatcher, Get_dispatcher_by_id
from agents_server.routes.websocket import socketio


class RunDispatcher(AgentDate):
    def __init__(self, task_id, dispatcher: Dispatcher, workspace, in_data=None):
        super().__init__(workspace)
        self.dispatcher = dispatcher
        self.task_id = task_id
        self.in_data = in_data

    def run(self):
        logger_runner.info(f'{self.task_id}-{self.dispatcher.name} start running')
        resList = []

        # 定义Markdown文件模板
        # md_template 应该是一个 Template
        md_template = Template("# {{ agent_name }}\n\n{{content}}\n\n")

        try:
            # 获取调度员下的所有AgentUnit
            dispatch_units = self.dispatcher.dispatch_units
            if len(dispatch_units) == 0:
                return "No dispatch units."
            for dispatch_unit in dispatch_units:
                agent_unit = GetAgentUnitById(dispatch_unit.agent_unit_id)

                # 创建AgentUnit运行实例
                runAU = RunAgentUnit(self.task_id, agent_unit, self.workspace, dispatch_unit.settings, self.in_data)

                # 运行AgentUnit
                res, tokens = runAU.run()

                response = {
                    "task_id": self.task_id,
                    "dispatcher_id": self.dispatcher.id,
                    "agent_unit_id": agent_unit.id,
                    "res": res,
                    "tokens": tokens,
                    "dispatch_unit": dispatch_unit
                }
                resList.append(response)
                logger_runner.info(f'{self.task_id}-{self.dispatcher.name}-{agent_unit.name} response: {response}')
                # 将结果写入工作区文件
                # 结果的格式是： AgentName res
                agent_name = agent_unit.name
                content = res

                # 渲染模板,填入数据
                md_output = md_template.render(
                    agent_name=agent_name,
                    content=content
                )

                # 输出文件名
                md_file = f"{self.workspace}/output.md"

                # 写入文件
                with open(md_file, 'a', encoding='utf-8') as f:
                    f.write(md_output)

            logger_runner.info(f'{self.task_id}-{self.dispatcher.name} end running')

            # 收集结果 处理next_action
            for k, dispatch_unit in enumerate(dispatch_units):
                if dispatch_unit.next_action:
                    print(dispatch_unit.next_action)
                    nextData = json.loads(dispatch_unit.next_action)
                    # 调度到下一个Agent
                    if nextData["type"] == "dispatch":
                        next_id = nextData["id"]
                        dispatcher = Get_dispatcher_by_id(next_id)
                        if not dispatcher:
                            logger_runner.error(f'{self.task_id}-{self.dispatcher.name} has no dispatcher: {next_id}')
                            continue
                        if dispatch_unit.auto_next:
                            # 自动进行下一步
                            # print("自动执行下一步")
                            RunDispatcher(self.task_id, dispatcher, self.workspace, resList[k]["res"]).run()
                        else:
                            # 需要手动调整
                            logger_runner.info(f'{self.task_id}-{self.dispatcher.name} is waiting for next')
                            # 返回Res给前端
                            socketio.emit('res', resList[k]["res"], namespace='/agents_running', room=self.task_id)
                            # 暂停当前任务
                            task_running_status[self.task_id] = False

                            while not task_running_status[self.task_id]:
                                time.sleep(2)
                                print(f'{self.task_id}-{self.dispatcher.name} is waiting for next')

                            # 接收到next后,继续运行
                            logger_runner.info(f'{self.task_id}-{self.dispatcher.name} is continue running')
                            new_input_data = task_input_data.get(self.task_id)
                            RunDispatcher(self.task_id, dispatcher, self.workspace, new_input_data).run()

        except Exception as e:
            logger_runner.error(e, exc_info=True)
            return e
