import telegram
from telegram.ext import Updater
from telegram.utils.request import Request
import conversation_helper

TOKEN = '972067680:AAH9Z7H5-u3XylOqG6RRvyj2m5j5JejQK68'
PROXY = 'socks5://208.113.154.54:50827'

def start_telegram_bot():
    kwargs= {}
    kwargs['proxy_url'] = PROXY
    bot = telegram.Bot(token=TOKEN, request=Request(**kwargs))
    print(bot.get_me(timeout=10000000))
    updater = Updater(token=TOKEN, request_kwargs=kwargs, use_context=True)
    dispatcher = updater.dispatcher

    first_conv_handler = conversation_helper.first_auth_conversation()
    dispatcher.add_handler(first_conv_handler)
    updater.start_polling(timeout=10000000)
    updater.idle()

start_telegram_bot()