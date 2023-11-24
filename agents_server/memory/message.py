from pymilvus import FieldSchema, DataType, Collection

from agents_server.embedding.openai_embedding import GetOpenAIEmbeddings
from agents_server.logger import logger_runner
from agents_server.memory.milvus import milvusCollection, createSchema

# 模拟创建聊天上下文消息集合 每一个任务，创建一条上下文记录集合
MSG_FIELDS = [
    FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True, description="主键"),
    FieldSchema(name="message", dtype=DataType.VARCHAR, max_length=4096, description="消息"),
    FieldSchema(name="role", dtype=DataType.VARCHAR, max_length=64, description="角色"),
    # FieldSchema(name="task_id", dtype=DataType.INT64, description="任务ID"),
    FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=1536, description="向量"),
]

# 创建索引
# 定义一个名为 index 的字典变量，它包含索引的相关参数
MSG_INDEX = {
    "index_type": "IVF_FLAT",
    # 设置索引类型为 "IVF_FLAT"。
    # 这是一种基于倒排文件（IVF）的索引类型，它通过扁平扫描（FLAT）来实现精确的距离计算。
    # 这种索引类型适用于中等大小的数据集。
    "metric_type": "L2",
    # 设置距离度量方式为欧氏距离（L2距离）。这是一种常用的度量向量相似性的方法。
    "params": {"nlist": 128},
    # 设置索引的参数。这里我们设置参数 "nlist" 为 128，
    # 它表示倒排文件中创建 128 个倒排列表（inverted lists）。
    # 较大的 nlist 值有助于提高搜索速度，但会增加索引的内存消耗。
}

MSG_INDEX_NAME = "embeddings"


# 任务消息上下文
class MsgSchema:
    def __init__(self, message, role, embeddings, pk=None):
        self.pk = pk
        self.message = message
        self.role = role
        self.embeddings = embeddings


# 创建一个数据集 创建Task的时候调用，会创建索引
def CreateMilvusCollection(name: str, description: str) -> None:
    milvusCollection(name, MSG_FIELDS, MSG_INDEX_NAME, MSG_INDEX, description)
    return


# 创建一个数据集连接
def MakeMilvusCollection(name: str) -> Collection:
    # return createSchema(name, MSG_FIELDS)
    return Collection(name)


# 保存数据到向量数据库 msgs 是一个 list
def SaveMsgsToMilvus(collection: Collection, msgs: []):
    MsgSchemaList = []
    for msg in msgs:
        embeddings = GetOpenAIEmbeddings(msg["content"])
        MsgSchemaList.append(MsgSchema(message=msg["content"], role=msg["role"], embeddings=embeddings))
    InsertMsgsToMilvus(collection, MsgSchemaList)


# 添加数据到向量数据库
def InsertMsgsToMilvus(collection: Collection, msgs: list[MsgSchema]):
    msgList = []
    roles = []
    embeddings = []
    for msg in msgs:
        msgList.append(msg.message)
        roles.append(msg.role)
        # task_ids.append(msg.task_id)
        embeddings.append(msg.embeddings)
    entities = [msgList, roles, embeddings]
    insert_result = collection.insert(entities)
    # insert() 函数会返回一个插入结果对象。
    # After final entity is inserted, it is best to call flush to have no growing segments left in memory
    collection.flush()
    # 这行代码调用 flush() 函数，将集合中的数据刷新到内存。这么做的好处是确保插入的实体数据已经存储到内存中，以便于我们后续进行查询、检索等操作。
    logger_runner.info(f"Number of entities in Milvus {collection.name}: {insert_result}")
