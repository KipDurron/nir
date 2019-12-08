import os
import random
from datetime import datetime, timedelta
from time import localtime, strftime
from urllib.request import urlopen

import telegram
import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.utils.request import Request
from telegram.vendor.ptb_urllib3.urllib3.contrib.socks import SOCKSProxyManager
# import requests
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
import socks



TOKEN = '972067680:AAH9Z7H5-u3XylOqG6RRvyj2m5j5JejQK68'
PROXY_LIST_FILE = 'proxies.txt'
PROXY_LIST_URL = 'https://www.proxy-list.download/api/v1/get?type=socks5'

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def start_telegram_bot():
    print('Selecting proxy')
    kwargs={
    'proxy_url': 'socks5://' + '50.62.35.107:20207',
    # Optional, if you need authentication:
    'urllib3_proxy_kwargs': {
        'assert_hostname': 'False',
        'cert_reqs': 'CERT_NONE'
        # 'username': 'user',
        # 'password': 'password'
    }
}
    # kwargs['proxy_url'] = 'socks5://' + '187.16.109.209:9999'
    bot = telegram.Bot(token=TOKEN, request=Request(**kwargs))
    # print(bot.get_me())
    updater = Updater(token=TOKEN, request_kwargs=kwargs, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))


    try:
        updater.start_polling()
    except Exception as e:
        print(e)
