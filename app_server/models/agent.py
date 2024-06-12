from http import HTTPStatus

from requests import Response

from app_server.tools.dify.dify_request import Make_dify_request, response_streaming


class DifyAgent:
    name = ""
    introduction = ""
    api_key = ""
    response_mode = ""
    mode = ""

    def __init__(self, name, introduction, api_key, response_mode, mode):
        self.name = name
        self.introduction = introduction
        self.api_key = api_key
        self.response_mode = response_mode
        self.mode = mode

    def run(self, input_data: dict = None, query: str = "", user="123456") -> Response:
        print('start agent:', self.name)
        payload = {
            "inputs": input_data,
            "query": query,
            "response_mode": self.response_mode,
            "user": user
        }
        # 请求参数分类
        print('payload:', payload)
        return Make_dify_request(self.api_key, payload, mode=self.mode)

    def run_to_str(self, input_data=None, query: str = "", user="123456") -> str:
        if input_data is None:
            input_data = {}
        print('input_data:', input_data)
        print('query:', query)
        response = self.run(input_data, query, user)

        if self.response_mode == 'streaming':
            return response_streaming(response)
        else:
            if response.status_code != HTTPStatus.OK:
                print('response status_code:', response.status_code)
                print('response:', response.text)
                return f'response status_code: {response.status_code}, response: {response.text}'
            json_data = response.json()
            return json_data.get('answer')

