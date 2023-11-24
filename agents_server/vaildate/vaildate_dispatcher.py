def validate_dispatcher_data(data):

    if not data.get('agent_id'):
        return 'agent_id is required'

    return None
