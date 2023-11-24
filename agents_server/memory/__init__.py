"""
@Time        : 2023/9/26 8:288
@Author      : LinightX
@File        : __init__.py
@Description : 向量数据库初始化
"""
from pymilvus import connections

from config import Config

fmt = "\n=== {:30} ===\n"
# 连接服务器
print(fmt.format("start connecting to Milvus"))
connections.connect(
    alias=Config.VD_MILVUS_ALIAS,
    user=Config.VD_MILVUS_USER,
    password=Config.VD_MILVUS_PWD,
    host=Config.VD_MILVUS_HOST,
    port=Config.VD_MILVUS_PORT,
    db_name=Config.VD_MILVUS_DB
)
