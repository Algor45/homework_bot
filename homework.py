import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (ListKeyError, NoResponseError, NotaListError,
                        ParseMissStatusError, SendMessageError)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s -'
                              ' %(levelname)s - %(message)s')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправляем сообщение в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение отправлено: {message}')
    except SendMessageError as error:
        logger.error(f'Сообщение не отправлено: {error.txt}')


def get_api_answer(current_timestamp):
    """Запрос к API yandex."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code == 200:
        response = response.json()
        logger.debug(f' Ответ от API: {response}')
        return response
    raise NoResponseError


def check_response(response):
    """Ответ API проверяется на корректность."""
    list_key = response['homeworks']
    if not isinstance(list_key, list):
        raise NotaListError
    if list_key is None:
        raise ListKeyError
    logger.debug(list_key)
    return list_key


def parse_status(homework):
    """Проверяем статус домашней работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework_status]
        logger.debug(verdict)
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    raise ParseMissStatusError


def check_tokens():
    """Проверяется наличие необходимых переменных окружения."""
    if ((PRACTICUM_TOKEN is not None)
            and (TELEGRAM_TOKEN is not None)
            and (TELEGRAM_CHAT_ID is not None)):
        return True
    return False


def main():
    """Основная логика работы бота."""
    if not check_tokens:
        logger.critical('Отсутствуют переменные окружения в файле .env')
        raise Exception('Проверьте наличие переменных в файле .env')

    cached_response = None
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            if cached_response != response.get('homeworks'):
                cached_response = response.get('homeworks')
                homework = check_response(response)
                if homework != []:
                    homework_verdict = parse_status(homework[0])
                    send_message(bot, homework_verdict)

            else:
                logger.debug('В ответе от API отсутствуют новые статусы.')

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            logger.error(error.txt)
            message = f'Сбой в работе программы: {error.txt}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
