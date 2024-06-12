from datetime import timedelta


class Config:

    # mysql
    MYSQL_HOST = '127.0.0.1'  # 127.0.0.1/localhost
    MYSQL_PORT = 3306
    MYSQL_DATA_BASE = '8888888888'
    MYSQL_USER = 'root'  # root

    MYSQL_PWD = '1234567'  #
    MYSQL_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATA_BASE}?charset=utf8'

    # wx_app
    APP_ID = ''
    SECRET = ''

    # JWT
    JWT_KEY = ''
    JWT_EXPIRE = timedelta(days=2)

    # Vector Database
    VD_MILVUS_HOST = 'localhost'
    VD_MILVUS_PORT = 19530
    VD_MILVUS_USER = 'root'
    VD_MILVUS_PWD = ''
    VD_MILVUS_ALIAS = 'default'
    VD_MILVUS_DB = 'SuperAgents'

    # static url
    Statics_url = 'https://www.'

