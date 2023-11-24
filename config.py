from datetime import timedelta


class Config:

    # mysql
    MYSQL_HOST = '127.0.0.1'  # 127.0.0.1/localhost
    MYSQL_PORT = 3306
    MYSQL_DATA_BASE = 'SuperAgents'
    MYSQL_USER = 'root'  # root
    MYSQL_PWD = 'Freedom7'  # Freedom7
    MYSQL_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATA_BASE}?charset=utf8'

    # wx_app
    APP_ID = 'wxc4e0282dbcd53c9b'
    SECRET = '475a1a22fa73a6cd85061d00431c46da'

    # JWT
    JWT_KEY = '475a1a22fa73a612a4061d00431c46da'
    JWT_EXPIRE = timedelta(days=2)

    # Vector Database
    VD_MILVUS_HOST = 'localhost'
    VD_MILVUS_PORT = 19530
    VD_MILVUS_USER = 'root'
    VD_MILVUS_PWD = ''
    VD_MILVUS_ALIAS = 'default'
    VD_MILVUS_DB = 'SuperAgents'

    # static url
    Statics_url = 'https://www.fwculture.cn/statics/'
