import os

class Sender:
    def __init__(self):
        self.bot_token = os.environ.get("Q_BOT_TOKEN")
        self.qndl_key = os.environ.get("QNDL_KEY")

    def get_token(self)->str:
        return self.bot_token

    def get_qndl_key(self)->str:
        return self.qndl_key