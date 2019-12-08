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
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
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

    # lst = get_proxies()
    kwargs= {}
    # if len(lst) == 0:
    #     print('Using default proxy')
    #     bot = telegram.Bot(token=TOKEN, request=Request(**kwargs))
    #     print(bot.get_me())
    # else:
    #     # kwargs.pop('urllib3_proxy_kwargs')
    #     noconnect = True
    #     while noconnect:
    #         kwargs['proxy_url'] = 'socks5://61.41.9.213:1081' + random.choice(lst)
    #         print('Testing connection with ' + kwargs['proxy_url'])
    #         try:
    #             bot = telegram.Bot(token=TOKEN, request=Request(**kwargs))
    #             print(bot.get_me())
    #             noconnect = False
    #         except Exception as e:
    #             pass
    kwargs['proxy_url'] = 'socks5://61.41.9.213:1081'
    bot = telegram.Bot(token=TOKEN, request=Request(**kwargs))
    print(bot.get_me())
    updater = Updater(token=TOKEN, request_kwargs=kwargs)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    # dispatcher.add_handler(CommandHandler('login', login_handler))
    # dispatcher.add_handler(CommandHandler('lo', list_organisations))
    # dispatcher.add_error_handler(error_callback)
    while True:
        try:
            updater.start_polling()
        except Exception as e:
            print(e)


def get_proxies():
    # обновим файл PROXY_LIST_FILE на основе списка с PROXY_LIST_URL, если он старее 2-х недель
    format = "%Y-%m-%d %H:%M:%S"
    tm = localtime(os.path.getctime(PROXY_LIST_FILE))
    dt = datetime.strptime(strftime(format, tm), format)
    if dt + timedelta(days=14) < datetime.now():
        url = urlopen(PROXY_LIST_URL)
        s = url.read()
        open(PROXY_LIST_FILE, "w").write(s)

    # загрузим список прокси
    s = open(PROXY_LIST_FILE, 'r').readlines()
    lst = []
    for line in s:
        lst.append(line.strip('\n'))
    return lst