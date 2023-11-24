"""
@Time        : 2023/9/14 15:43
@Author      : LinightX
@File        : agent_data.py
@Description : Agent公共数据部分，包括任务ID，记忆存储，临时数据等，待重写
"""


class AgentDate(object):
    # 上下文
    def __init__(self, workspace):
        # 记忆
        self.workspace = workspace
        self.memory = ""
