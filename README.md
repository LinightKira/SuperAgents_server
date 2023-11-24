# 这是一个产品经理，通过AI和各种教程+自己的想法拼凑成的项目
# 很不完善，仅供学习和交流
SuperAgents 主要工作原理


# Agent
每个Agent是一个独立的工作单元

Agent的数据结构为：
- 1.主键ID
- 2.用户ID-与UserID绑定
- 3.Agent 名字
- 4.Agent 说明
- 5.Agent 状态
- 6.Agent 头像
- 7.创建和修改时间
- 8.记忆设置
- 9.资料库设置
每一个Agent是众多Dispatcher(调度)的合集

# Dispatcher(调度员)
Agent的工作流程，就是每一个调度员顺序进行工作

每个一调度员负责将输入内容 交付给各个Agent单元 并将输出的结果，交付到下一个调度员手中

一个调度员可以调用多个Agent单元，并且可以根据不同的输入内容进行判断

调度员也具有智能模式，可以和LLM进行交互
Dispatcher的数据结构为：
- 1.主键ID
- 2.AgentID
- 3.Dispatcher 名字
- 4.Dispatcher 说明
- 5.Dispatcher 状态
- 6.创建和修改时间

Dispatch_list 数据结构
- 1.主键ID
- 2.Dispatcher_ID
- 3.agent_unit_ID 
- 4.prompt 智能检测输入
- 5.nextAct 下一步动作(json格式，可能是保存到文件，也可能是到下一个调度) 
- 6.是否自动执行下一步
- 7.创建和修改时间

# Agent_unit 代理单元
Agent 最小执行单元

每一个unit 包括 主键ID 输入数据清洗 Prompt Tools 输出结果数据清洗 4个主要部分

工作流程是 输入数据清洗 Prompt+Tools 访问LLM  输出结果清洗 

其中数据清洗先不考虑

其中 访问LLM可能有多次，也可能是0次，如仅使用工具进行处理，不使用LLM能力
Agent_unit 数据结构
- 1.主键ID
- 2.Agent_ID
- 4.prompt 提示词
- 5.tools 工具ID 是一个列表
- 6.创建和修改时间
- 7.LLM配置

# 公共记忆
每一个Agent 有一个公共记忆，公共记忆包含每一个调度员的输入和输出
公共记忆保存两份，一份在向量数据库中，方便检索，一份在文件中，作为Agent最终交付的内容

Agent要求存储器具有自动检索记忆的能力。
自动检索的一个重要方法是考虑三个指标： 最近性（Recency）、相关性（Relevance）和重要性（Importance）。
记忆得分由这些指标加权组合而成，得分最高的记忆在模型的上下文中被优先考虑。

# 上下文
每一个调度员(Dispatcher)具有上下文记忆，用户记录调用Agent_unit的情况，上下文保存在redis中
