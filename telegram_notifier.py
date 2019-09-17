import locale
import time
import traceback
from collections import deque
from dataclasses import dataclass

import telegram

import settings

TELEGRAM_MAX_MESSAGE_LENGTH = 4096
TELEGRAM_PERSONAL_MESSAGE_MAX_RATE = 30  # 30 messages/sec
TELEGRAM_GROUP_MESSAGE_MAX_RATE = 20/60  # 20 messages/min


@dataclass
class TelegramMessage:
    chat_id: str
    text: str


class CianNotifierBot:
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
    personal_messages_queue = deque()
    group_messages_queue = deque()

    actions_map = {
        'change': 'изменено',
        'add': 'добавлено',
    }

    fields_to_ignore = ['statistic', 'priceChanges']

    @classmethod
    def check_ignored_field(cls, field_path):
        for ignored in cls.fields_to_ignore:
            if ignored in field_path:
                return True
        return False

    @classmethod
    def send_message(cls, chat_id, message):
        message_end = ' < ... >'
        content_len = TELEGRAM_MAX_MESSAGE_LENGTH - len(message_end)
        message = (message[:content_len] + message_end) if len(message) > content_len else message
        return cls.bot.send_message(chat_id=chat_id, text=message)

    @classmethod
    def enqueue_message(cls, chat_id, message):
        message = TelegramMessage(chat_id, message)
        if int(chat_id) > 0:
            cls.personal_messages_queue.append(message)
        else:
            cls.group_messages_queue.append(message)

    @staticmethod
    def process_personal_messages_queue():
        while True:
            try:
                message = CianNotifierBot.personal_messages_queue.pop()
                CianNotifierBot.send_message(message.chat_id, message.text)
            except IndexError:
                pass
            except Exception as e:
                print('process_personal_messages_queue')
                print(f'Traceback: {traceback.format_exc()}')
            time.sleep(1/TELEGRAM_PERSONAL_MESSAGE_MAX_RATE)

    @staticmethod
    def process_group_messages_queue():
        while True:
            try:
                message = CianNotifierBot.group_messages_queue.pop()
                CianNotifierBot.send_message(message.chat_id, message.text)
            except IndexError:
                pass
            except Exception as e:
                print('process_group_messages_queue')
                print(f'Traceback: {traceback.format_exc()}')
            time.sleep(1/TELEGRAM_GROUP_MESSAGE_MAX_RATE)

    @classmethod
    def generate_readable_diff(cls, diff):
        result = []
        for action, field_path, values in diff:
            action_text = cls.actions_map.get(action, action)
            if type(field_path) is not str:
                field_path = '.'.join(str(f) for f in field_path)
            if cls.check_ignored_field(field_path):
                continue
            if action == 'change':
                values_text = ' -> '.join(f'`{v}`' for v in values)
            else:
                values_text = str(values)
            text = f'{action_text}: {field_path}\n{values_text}'
            result.append(text)
        return '\n\n'.join(result)

    @staticmethod
    def get_offer_link(offer):
        cian_id = offer['cianId']
        return f'https://www.cian.ru/rent/flat/{cian_id}/'

    @classmethod
    def get_offer_info(cls, offer):
        offer_link = cls.get_offer_link(offer)
        price = offer['bargainTerms']['price']
        stats = offer.get('statisctic', {})
        total_views = stats.get('total')
        daily_views = stats.get('daily')
        price = locale.currency(price, grouping=True)
        added_date = offer['added']
        text = f'{offer_link}\nЦена: {price}\nДобавлено: {added_date}'
        if total_views and daily_views:
            text += '\nПросмотров: {total_views}\nЗа сегодня: {daily_views}'
        return text


    @classmethod
    def send_new_offer(cls, offer):
        info_text = cls.get_offer_info(offer)
        text = f'#новое предложение:\n{info_text}'
        return cls.enqueue_message(settings.TELEGRAM_CHAT_ID, text)

    @classmethod
    def send_offer_changed(cls, offer, diff):
        info_text = cls.get_offer_info(offer)
        diff_text = cls.generate_readable_diff(diff)
        if diff_text:
            text = f'#изменение предложения:\n{info_text}\n\n{diff_text}'
            return cls.enqueue_message(settings.TELEGRAM_CHAT_ID, text)
