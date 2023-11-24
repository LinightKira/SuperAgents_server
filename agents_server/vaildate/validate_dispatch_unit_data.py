def validate_dispatch_unit_data(data):
    if not data.get('dispatcher_id'):
        return 'dispatcher is required'
    if not data.get('agent_unit_id'):
        return 'agent_unit_id is required'
    # if not data.get('next_action'):
    #     return 'next_action is required'

    return None
