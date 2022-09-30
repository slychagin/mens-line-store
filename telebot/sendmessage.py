import requests
from django.core.exceptions import ObjectDoesNotExist
from telebot.models import TeleSettings


def send_telegram(order_number, total_sum, last_name, first_name, email, phone_number):
    try:
        settings = TeleSettings.objects.get(pk=2)
        token = str(settings.tg_token)
        chat_id = str(settings.tg_chat)
        text = str(settings.tg_message)

        api = 'https://api.telegram.org/bot'
        method = api + token + '/sendMessage'

        text_message = text.replace('{order_number}', order_number).\
            replace('{total_sum}', str(total_sum)).\
            replace('{full_name}', f'{last_name} {first_name}').\
            replace('{email}', email).\
            replace('{phone_number}', phone_number)

        try:
            req = requests.post(method, data={
                'chat_id': chat_id,
                'text': text_message
            })
        except:
            pass
        finally:
            if req.status_code != 200:
                print('Ошибка отправки!')
            elif req.status_code == 500:
                print('Ошибка 500')
            else:
                pass
    except ObjectDoesNotExist:
        pass
