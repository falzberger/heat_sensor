import logging

import requests

from config import BOT_TOKEN, CHAT_ID


def send_telegram(msg: str):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}'
    logger = logging.getLogger('heat_sensor')
    logger.info(f'GET request to {url}')
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(f'Could not send message to telegram: {response}')
