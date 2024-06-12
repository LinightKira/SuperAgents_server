from datetime import datetime

from pymongo import MongoClient


class ChatDatabase:
    def __init__(self, db_name='chat_db', collection_name='messages', user='root', password='Freedom7',
                 host='localhost', port=27017):
        self.client = MongoClient(f'mongodb://{user}:{password}@{host}:{port}/')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def create_message(self, session_id, message_body):
        message = {
            'session_id': session_id,
            'message_body': message_body,
            'created_at': datetime.utcnow()
        }
        result = self.collection.insert_one(message)
        return str(result.inserted_id)

    def read_message(self, message_id):
        message = self.collection.find_one({'_id': message_id})
        return message

    def update_message(self, message_id, updated_body):
        result = self.collection.update_one(
            {'_id': message_id},
            {'$set': {'message_body': updated_body}}
        )
        return result.modified_count

    def delete_message(self, message_id):
        result = self.collection.delete_one({'_id': message_id})
        return result.deleted_count

    def find_messages_by_session(self, session_id):
        messages = self.collection.find({'session_id': session_id})
        return list(messages)

    # 通过会话ID进行分页查询，从最新消息开始，每次获取per_page条记录。
    # 使用sort('created_at', -1)
    # 按创建时间降序排序
    def find_messages_by_session_paginated(self, session_id, page, per_page):
        messages = self.collection.find({'session_id': session_id}) \
            .skip((page - 1) * per_page) \
            .limit(per_page)
        return list(messages)

    # 通过会话ID和最后一条消息ID进行分页查询，避免数据重复。
    # 查找指定消息ID对应的消息，使用其created_at字段作为基准，查询所有在此时间之前的消息。
    # 使用sort('created_at', -1)
    # 按创建时间降序排序，确保从最新消息开始查询
    def find_latest_messages_by_session_paginated(self, session_id, page, per_page):
        messages = self.collection.find({'session_id': session_id}) \
            .sort('created_at', -1) \
            .skip((page - 1) * per_page) \
            .limit(per_page)
        return list(messages)

    def find_messages_after_id(self, session_id, last_message_id, per_page):
        last_message = self.collection.find_one({'_id': last_message_id})
        if not last_message:
            return []
        messages = self.collection.find({
            'session_id': session_id,
            'created_at': {'$lt': last_message['created_at']}
        }) \
            .sort('created_at', -1) \
            .limit(per_page)
        return list(messages)


# Example usage
if __name__ == "__main__":
    db = ChatDatabase()

    # Create a message
    message_id = db.create_message('session1', {'type': 'text', 'content': 'Hello, World!'})

    # Read the message
    print("Message:", db.read_message(message_id))

    # Update the message
    db.update_message(message_id, {'type': 'text', 'content': 'Hello, MongoDB!'})

    # Find messages by session ID
    print("Messages in session1:", db.find_messages_by_session('session1'))

    # Find paginated messages by session ID
    page = 1
    per_page = 10
    print(f"Messages in session1, page {page}:", db.find_messages_by_session_paginated('session1', page, per_page))

    # Find latest paginated messages by session ID
    print(f"Latest messages in session1, page {page}:",
          db.find_latest_messages_by_session_paginated('session1', page, per_page))

    # Find messages after a specific message ID
    print(f"Messages in session1 after message ID {message_id}:",
          db.find_messages_after_id('session1', message_id, per_page))

    # Delete the message
    db.delete_message(message_id)
