import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.utils.request import Request

TOKEN = '972067680:AAH9Z7H5-u3XylOqG6RRvyj2m5j5JejQK68'

def dialog(update, context):
    if update.message.text == 'да':
        update.message.reply_text('Введите название сервера')
    else:
        update.message.reply_text('Другого функционала у меня пока нет, пока')


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привет, вы хотите создать виртуальный сервер ?')

def start_telegram_bot():
    kwargs= {}
    kwargs['proxy_url'] = 'socks5://61.41.9.213:1081'
    bot = telegram.Bot(token=TOKEN, request=Request(**kwargs))
    print(bot.get_me(timeout=100000000000))
    updater = Updater(token=TOKEN, request_kwargs=kwargs, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, dialog))
    updater.start_polling(timeout=10000000000000)

start_telegram_bot()