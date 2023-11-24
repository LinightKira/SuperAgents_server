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

if not has:
    print(f"hello_milvus is not exist")
else:
    print(f"hello_milvus is exist")

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

    # 加载集合到内存并执行向量相似度搜索
    # Before conducting a search or a query, you need to load the data in `hello_milvus` into memory.
    # print(fmt.format("Start loading"))
    hello_milvus.load()

    vectors_to_search = [GetOpenAIEmbeddings("成功的道路有哪些")]
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }

    # 这里我们定义了一个名为search_params的字典变量，用来设置搜索参数。
    # "metric_type": "L2"：设置距离度量方式为欧氏距离（L2距离）。
    # "params": {"nprobe": 10}：设置搜索参数
    # "nprobe"为10，表示从倒排列表中查找10个最相近的候选项进行精确的距离计算。较大的nprobe值有助于提高搜索精度，但会降低搜索速度
    result = hello_milvus.search(vectors_to_search, "embeddings", search_params, limit=3,
                                 output_fields=["message", "pk"])
    # 根据查询向量 vectors_to_search、索引属性 "embeddings" 和搜索参数 search_params，
    # 调用 search() 函数进行搜索。同时，设置 limit=3 来限制搜索结果的数量，返回最相近的前三个实体。
    # output_fields=["random"] 表示输出结果包括 "random" 属性。

    print(fmt.format("Search results:"))
    for res in result:
        print(f"- Query results: {res}")

    # 执行查询向量
    result = hello_milvus.query(expr="role == '系统' ", output_fields=["message", "pk"])
    # 调用 query() 函数进行条件查询。
    # 我们在这个函数中设定了查询表达式 expr="random > -14"，表示查询 hello_milvus 魔术球袋子中 "random" 属性大于 -14 的实体。
    # output_fields = ["random", "embeddings"]：设置输出结果包括"random"和"embeddings"两个属性。
    # 这意味着查询结果将返回满足条件的实体及其这两个属性值。
    # result变量存储了查询结果，这个结果包含了满足条件（"random"属性大于 - 14）的实体以及它们的"random"和"embeddings"属性值。
    print(fmt.format("Search results:"))
    for res in result:
        print(f"- Query results: {res}")

    '''
    # 执行混合搜索
    result = hello_milvus.search(vectors_to_search, "embeddings", search_params, limit=3, expr="random > -12",
                                 output_fields=["random"])

    # 具体解释如下：result = hello_milvus.search(...)：根据查询向量vectors_to_search、索引属性"embeddings"和搜索参数search_params，调用
    # search()函数进行搜索。此外，设置limit = 3来限制搜索结果的数量，返回离查询向量最相近的前三个魔术球实体。
    #
    # expr = "random > -12"：新增一个条件表达式，表示只搜索满足条件（"random"属性大于 - 12）的实体。
    # 这样，我们可以在搜索相似向量的同时满足其他属性条件。
    #
    # output_fields = ["random"]：设置输出结果仅包括"random"属性。
    # 这意味着搜索结果将返回满足条件的实体及其"random"属性值。
    #
    # result变量存储了搜索结果，这个结果包含了离查询向量最相近的前三个满足条件（"random"属性大于 - 12）的实体，以及它们的"random"属性值。
    print(fmt.format("Search results:"))
    for res in result:
        print(f"- Query results: {res}")
        
    
    '''

    hello_milvus.release()
