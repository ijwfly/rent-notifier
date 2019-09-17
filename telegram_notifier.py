import locale

import telegram

import settings


class CianNotifierBot:
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)

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
    def send_message(cls, text):
        return cls.bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=text)

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
        return cls.send_message(text)

    @classmethod
    def send_offer_changed(cls, offer, diff):
        info_text = cls.get_offer_info(offer)
        diff_text = cls.generate_readable_diff(diff)
        if diff_text:
            text = f'#изменение предложения:\n{info_text}\n\n{diff_text}'
            return cls.send_message(text)
