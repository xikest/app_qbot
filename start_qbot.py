import logging

from bots import BotQ
from info.sender import Sender

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = Sender().get_token()
BotQ(TOKEN).start()
