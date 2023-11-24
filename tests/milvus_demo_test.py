from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
import sys

sys.path.append("..")
from agents_server.embedding.openai_embedding import GetOpenAIEmbeddings

from config import Config

# 参考资料： https://zhuanlan.zhihu.com/p/634255317

fmt = "\n=== {:30} ===\n"
search_latency_fmt = "search latency = {:.4f}s"
num_entities, dim = 100, 8  # 100个数据,向量维度8维
# 连接服务器
print(fmt.format("start connecting to Milvus"))
connections.connect(
    host=Config.VD_MILVUS_HOST,
    port=Config.VD_MILVUS_PORT,
    db_name=Config.VD_MILVUS_DB,
    # user=Config.VD_MILVUS_USER,
    # password=Config.VD_MILVUS_PWD,
)

has = utility.has_collection("hello_milvus")
print(f"Does collection hello_milvus exist in Milvus: {has}")

# if has:
#     # 删除集合
#     utility.drop_collection("hello_milvus")
#     has = utility.has_collection("hello_milvus")
#     print(f"Does collection hello_milvus exist in Milvus: {has}")

# 创建集合
fields = [
    FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=False),  # 定义了一个名为 "pk" 的属性，数据类型为整数（INT64）
    FieldSchema(name="random", dtype=DataType.DOUBLE),  # 定义了一个名为 "random" 的属性，数据类型为双精度浮点数（DOUBLE） 可以作为数据的属性，描述特征用
    FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=8)  # 定义了一个名为 "embeddings"
    # 的属性，数据类型为浮点数向量（FLOAT_VECTOR），它可以包含8个浮点数的数据，这个属性可以描述更高维度的魔术球特性，比如形状、质地等。
]

# 模拟创建聊天上下文消息集合
msgFields = [
    FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True, description="主键"),
    FieldSchema(name="message", dtype=DataType.VARCHAR, max_length=4096, description="消息"),
    FieldSchema(name="role", dtype=DataType.VARCHAR, max_length=64, description="角色"),
    FieldSchema(name="task_id", dtype=DataType.INT64, description="任务ID"),
    FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=1536, description="向量"),
]

schema = CollectionSchema(msgFields, "这是拉克丝的聊天上下文")  # 创造一个名为 "hello_milvus" 的集合
hello_milvus = Collection("hello_milvus", schema)
# hello_milvus = Collection("hello_milvus", schema, consistency_level="Strong")

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
embeddings = []
for sentence in sentences:
    res = GetOpenAIEmbeddings(sentence)
    embeddings.append(res)

# 生成随机数据
entities = [
    sentences,
    roles,
    task_ids,
    embeddings
]
print(fmt.format("create entities"))
print(entities)

insert_result = hello_milvus.insert(entities)
# 这行代码将创建好的实体插入到我们之前创建的 hello_milvus 集合中
# insert() 函数会返回一个插入结果对象。
# After final entity is inserted, it is best to call flush to have no growing segments left in memory
hello_milvus.flush()
# 这行代码调用 flush() 函数，将 hello_milvus 集合中的数据刷新到内存。这么做的好处是确保插入的实体数据已经存储到内存中，以便于我们后续进行查询、检索等操作。
print(f"Number of entities in Milvus: {hello_milvus.num_entities}")  # check the num_entites

# 创建索引
# 定义一个名为 index 的字典变量，它包含索引的相关参数
index = {
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
hello_milvus.create_index("embeddings", index)
# 根据设置好的索引参数，
# 我们调用 create_index() 函数为 hello_milvus 中的 "embeddings" 属性创建索引。
# 创建索引后，我们可以使用这个索引快速地查询距离符合要求的实体。


'''
# 通过主键删实体
expr = f"pk in [{ids[0]}, {ids[1]}]"
hello_milvus.delete(expr)

# 删除集合
utility.drop_collection("hello_milvus")

'''
