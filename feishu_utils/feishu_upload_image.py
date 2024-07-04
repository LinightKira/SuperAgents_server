import requests
from requests_toolbelt import MultipartEncoder

from feishu_utils.feishu_token_manager import token_manager


def upload_image(image_url: str):
    # 下载图片
    print(f"Downloading image: {image_url}")
    image_response = requests.get(image_url)
    if image_response.status_code != 200:
        raise Exception(f"Failed to download image: {image_response.status_code}")

    # 将图片数据保存到内存文件
    from io import BytesIO
    image_file = BytesIO(image_response.content)
    image_file.name = 'image.jpg'  # 设置文件名

    url = "https://open.feishu.cn/open-apis/im/v1/images"
    form = {
        'image_type': 'message',
        'image': (image_file.name, image_file, 'image/jpeg')  # 指定图片的文件名和MIME类型
    }
    multi_form = MultipartEncoder(form)
    token = token_manager.get_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': multi_form.content_type
    }

    # 上传图片
    response = requests.post(url, headers=headers, data=multi_form)

    # 打印响应内容和日志ID以进行调试
    print(response.headers.get('X-Tt-Logid', 'No Log ID'))  # for debug or oncall
    print(response.content)  # Print Response

    return response.content


if __name__ == '__main__':
    url = 'http://localhost/files/tools/44c01142-2f8a-4eda-a56d-d319da59d12d.png?timestamp=1720094134&nonce=c9b1e4ea1af8a3051b8700674a97cbd6&sign=woTQC8pHxYNl4FnlkY7KeQTfsWA7sJnuYn4nxdOFdtA='
    upload_image(url)
