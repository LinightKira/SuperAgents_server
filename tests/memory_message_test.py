from agents_server.embedding.openai_embedding import GetOpenAIEmbeddings
from agents_server.memory.message import MsgSchema, MSG_INDEX_NAME, MSG_FIELDS, MSG_INDEX, InsertMsgsToMilvus
from agents_server.memory.milvus import hasCollection, createSchema, createSchemaAndIndex

if hasCollection("freedom"):
    col = createSchema("freedom", MSG_FIELDS)  # pass
else:
    col = createSchemaAndIndex("freedom", MSG_FIELDS, MSG_INDEX_NAME, MSG_INDEX, "freedom测试", )
    print(hasCollection("freedom"))

sentences = [
    "今天天气晴朗，阳光明媚。",
    "生活需要勇敢面对困难。",
    "世界充满了未知的奥秘。",
    "家人的爱永远是最重要的。",
    "学习是通向成功的道路。",
    "快乐可以从简单的事物中找到。",
    "爱是连接人们心灵的纽带。",
    "勤劳是取得成就的关键。",
    "梦想可以改变未来的命运。",
    "感恩每一个美好的时刻。"
]
roles = [
    "系统", "用户", "管理员", "开发者", "测试人员", "运维人员", "财务人员", "客服人员", "技术人员", "产品经理"
]

task_ids = [11, 12, 13, 14, 15, 16, 17, 18, 19, 10]
messages = []

# 造数据
for i in range(10):
    pk = i + 1
    message = sentences[i]
    role = roles[i]
    task_id = task_ids[i]
    embeddings = GetOpenAIEmbeddings(message)

    msg = MsgSchema(pk, message, role, task_id, embeddings)
    messages.append(msg)

InsertMsgsToMilvus(col, messages)
