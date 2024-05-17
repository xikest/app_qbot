import logging
import os
from bot import Bot_Q

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot_token = os.environ.get("Q_BOT_TOKEN")
Bot_Q(bot_token).start()
