import logging
from settings import LOG_LVL, LOG_FILE, LOG_PATH

logger = logging.getLogger(__name__)

logger.setLevel(LOG_LVL)
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LVL)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
if LOG_FILE:
    file_handler = logging.FileHandler(f'{LOG_PATH}/{LOG_FILE}', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
