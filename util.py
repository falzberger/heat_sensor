import requests

from config import BOT_TOKEN, CHAT_ID

BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'


def send_message(msg: str) -> requests.Response:
    # https://core.telegram.org/bots/api#sendmessage
    return requests.get(f'{BASE_URL}/sendMessage',
                        {'chat_id': CHAT_ID, 'text': msg})


def send_image(path: str, msg: str = ''):
    # https://core.telegram.org/bots/api#sendphoto
    with open(path, 'rb') as file:
        return requests.post(f'{BASE_URL}/sendPhoto',
                             {'chat_id': CHAT_ID, 'photo': path, 'caption': msg, 'disable_notification': True},
                             files={'photo': file})
