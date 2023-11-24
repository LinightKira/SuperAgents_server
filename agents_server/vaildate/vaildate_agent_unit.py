def validate_agent_unit_data(data):

    if not data.get('name'):
        return 'name is required'

    return None
