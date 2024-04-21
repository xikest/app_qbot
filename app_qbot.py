import logging

from bot import Bot_Q
from info.sender import Sender

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = Sender().get_token()
print(TOKEN)
Bot_Q(TOKEN).start()
