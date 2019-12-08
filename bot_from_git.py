import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.utils.request import Request

TOKEN = '972067680:AAH9Z7H5-u3XylOqG6RRvyj2m5j5JejQK68'
PROXY_LIST_FILE = 'proxies.txt'
PROXY_LIST_URL = 'https://www.proxy-list.download/api/v1/get?type=socks5'

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text('А может быть ты ' + update.message.text)

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def start_telegram_bot():
    kwargs= {}
    kwargs['proxy_url'] = 'socks5://61.41.9.213:1081'
    bot = telegram.Bot(token=TOKEN, request=Request(**kwargs))
    print(bot.get_me())
    updater = Updater(token=TOKEN, request_kwargs=kwargs, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    updater.start_polling()

start_telegram_bot()