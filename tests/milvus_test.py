import sys

from agents_server.memory.message import MSG_FIELDS, MSG_INDEX_NAME, MSG_INDEX
from agents_server.memory.milvus import hasCollection, createSchema, createSchemaAndIndex, dropCollection

sys.path.append("..")

print(hasCollection("f1"))  # pass
# createSchema("freedom", MSG_FIELDS, "freedom测试") # pass
# print(hasCollection("freedom"))
#
# print(hasCollection("justice"))
# createSchemaAndIndex("justice", MSG_FIELDS, "", MSG_INDEX_NAME, MSG_INDEX) # pass
# print(hasCollection("justice"))

# dropCollection("freedom") # pass
