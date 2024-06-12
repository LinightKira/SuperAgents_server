import os
import config
import lark_oapi as lark
from lark_oapi.api.drive.v1 import *


# SDK 使用说明: https://github.com/larksuite/oapi-sdk-python#readme
# 复制该 Demo 后, 需要将 "YOUR_APP_ID", "YOUR_APP_SECRET" 替换为自己应用的 APP_ID, APP_SECRET.
def upload_files(file_path, parent_node):
    # 创建client
    client = lark.Client.builder() \
        .app_id(config.Config.FEISHU_ROBOT_APP_ID) \
        .app_secret(config.Config.FEISHU_ROBOT_APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    file = open(file_path, "rb")
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    request: UploadAllFileRequest = UploadAllFileRequest.builder() \
        .request_body(UploadAllFileRequestBody.builder()
                      .file_name(file_name)
                      .parent_type("explorer")
                      .parent_node(parent_node)
                      .size(file_size)
                      .file(file)
                      .build()) \
        .build()

    # 发起请求
    response: UploadAllFileResponse = client.drive.v1.file.upload_all(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.drive.v1.file.upload_all failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    return response


if __name__ == "__main__":
    upload_files('./feishu_token_manager.py', config.Config.FEISHU_ROBOT_UPLOAD_FOLDER_TOKEN)
