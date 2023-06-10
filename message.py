import json


class FrogMessageBase:
    def __init__(self, req_data, message_api_client):
        self.req_data = req_data
        self.event_id = req_data.header.event_id
        self.event_type = req_data.header.event_type
        self.api = message_api_client


# 群聊消息
"""
{'schema': '2.0', 'header': {'event_id': '453a73632f175d22257f086b43605000', 'token': '6NM8o0rlP9jRLyMfRoEPsd02mDaq3XDN', 'create_time': '1683454481741', 'event_type': 'im.message.receive_v1', 'tenant_key': '11cf3a899a82d75a', 'app_id': 'cli_a4c604c309785009'}, 'event': {'message': {'chat_id': 'oc_c826d98bd260d00a9a3b2ed61c3ab95d', 'chat_type': 'group', 'content': '{"text":"我！"}', 'create_time': '1683454481595', 'message_id': 'om_754b5f6b836a5573091650491ab6c50b', 'message_type': 'text'}, 'sender': {'sender_id': {'open_id': 'ou_29d04636d74be1ff1fab3b7571c53513', 'union_id': 'on_b1c8037e7c816a2fc3f9fdb9410956df', 'user_id': '9582bef5'}, 'sender_type': 'user', 'tenant_key': '11cf3a899a82d75a'}}}
"""
class MessageReceive(FrogMessageBase):
    def __init__(self, req_data, message_api_client):
        super().__init__(req_data, message_api_client)
        self.message = req_data.event.message
        self.is_text = self.message.message_type == "text"
        self.is_group = self.message.chat_type == 'group'
        self.talker_id = req_data.event.sender.sender_id.user_id
        if self.is_text:
            self.text = json.loads(self.message.content).get('text')
        if self.is_group:
            self.chat_id = self.message.chat_id
        
    def reply_chat_text(self, text):
        self.api.send_text_with_chat_id(self.chat_id, text)
    
    def reply_chat_rich_text(self, post):
        self.api.send_rich_text_with_chat_id(self.chat_id, post)


# 点表情
"""
{'schema': '2.0', 'header': {'event_id': '76d51eb63e7ea7cadd5837ab50278e85', 'token': '6NM8o0rlP9jRLyMfRoEPsd02mDaq3XDN', 'create_time': '1683453438883', 'event_type': 'im.message.reaction.created_v1', 'tenant_key': '11cf3a899a82d75a', 'app_id': 'cli_a4c604c309785009'}, 'event': {'action_time': '1683453438883', 'message_id': 'om_50bd8a4ae6dbf8896a4415756eaae761', 'operator_type': 'user', 'reaction_type': {'emoji_type': 'SMILE'}, 'user_id': {'open_id': 'ou_29d04636d74be1ff1fab3b7571c53513', 'union_id': 'on_b1c8037e7c816a2fc3f9fdb9410956df', 'user_id': '9582bef5'}}}
"""
class MessageReactionCreated(FrogMessageBase):
    def __init__(self, req_data, message_api_client):
        super().__init__(req_data, message_api_client)
        self.message_id = req_data.event.message_id
        self.emoji = req_data.event.reaction_type.emoji_type
        self.user_id = req_data.event.user_id.user_id
        self.create_time = req_data.header.create_time


def message_factory(req_data, message_api_client):
    if req_data.header.event_type == 'im.message.receive_v1':
        return MessageReceive(req_data, message_api_client)
    elif req_data.header.event_type == 'im.message.reaction.created_v1':
        return MessageReactionCreated(req_data, message_api_client)
    else:
        return FrogMessageBase(req_data, message_api_client)
