from pymilvus import FieldSchema, CollectionSchema, Collection
from pymilvus.orm import utility

from agents_server.logger import logger_runner


# 判断数据集是否存在
def hasCollection(name) -> bool:
    return utility.has_collection(name)


# 删除数据集
def dropCollection(name) -> None:
    utility.drop_collection(name)
    logger_runner.info(f'drop milvus collection: {name}')


# 创建数据集
def createSchema(name: str, fields: list[FieldSchema], description="") -> Collection:
    schema = CollectionSchema(fields, description)
    collect = Collection(name, schema)
    return collect


# 创建数据集并添加索引
# input: name(集合名), fields:（字段模板）, description（说明），index的字段名，index的参数
def createSchemaAndIndex(name: str, fields: list[FieldSchema], field_name,
                         index_params, description) -> Collection:
    collect = createSchema(name, fields, description)
    collect.create_index(field_name, index_params)
    logger_runner.info(f'create milvus collection: {name}')
    return collect


# 创建milvus连接
def milvusCollection(name: str, fields: list[FieldSchema], field_name,
                     index_params, description) -> Collection:
    if not hasCollection(name):
        return createSchemaAndIndex(name, fields, field_name, index_params, description)
    else:
        return createSchema(name, fields, description)
