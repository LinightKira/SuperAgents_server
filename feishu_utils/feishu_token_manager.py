import requests
import time

import config


class TokenManager:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.token = None
        self.expire_time = 0

    def get_token(self):
        if self.token and self.expire_time > time.time():
            # 如果当前令牌还没过期,直接返回
            return self.token
        else:
            print("Token expired, refreshing...")
            # 否则,请求新的令牌
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            headers = {"Content-Type": "application/json; charset=utf-8"}
            data = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            response = requests.post(url, headers=headers, json=data)
            response_data = response.json()

            if response_data["code"] == 0:
                self.token = response_data["tenant_access_token"]
                self.expire_time = time.time() + response_data["expire"]
                return self.token
            else:
                raise Exception(f"Failed to get token: {response_data['msg']}")


token_manager = TokenManager(config.Config.FEISHU_ROBOT_APP_ID, config.Config.FEISHU_ROBOT_APP_SECRET)

if __name__ == '__main__':
    # 获取令牌
    token = token_manager.get_token()
    print(f"Token: {token}")
