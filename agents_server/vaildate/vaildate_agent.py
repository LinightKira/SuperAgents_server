# 新增或更新character时的必填字段校验函数
def validate_agent_data(data):

    if not data.get('name'):
        return 'name is required'

    return None
