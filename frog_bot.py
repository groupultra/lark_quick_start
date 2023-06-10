class FrogBot:
    def __init__(self, message_api_client):
        self.api = message_api_client

    def on_group_text_message(self, msg):
        print(msg.text)
        if msg.text == 'shit':
            msg.reply_chat_text('Delicious!') # 屎真香！
        else:
            pass