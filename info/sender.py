import os

class Sender:
    def __init__(self):
        # self.bot_token = "7152804569:AAHVhDdhY6pKg-Vxaki3SASZRhVjGvT2WWw"
        self.bot_token = os.environ.get("Q_BOT_TOKEN")

    def get_token(self)->str:
        return self.bot_token
