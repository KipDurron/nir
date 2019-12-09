import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from auth_functions_handler import *

def first_auth_conversation():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: [MessageHandler(Filters.regex('^Да$'), start_auth),
                               MessageHandler(Filters.regex('^Нет$'), stop_auth)],
            AUTH: [CallbackQueryHandler(ask_for_input, pattern='^(?!' + str(END) + ').*$'),
                   CallbackQueryHandler(req_auth_to_sbcloud, pattern='^' + str(END) + '.*$')],
            TYPING: [MessageHandler(Filters.text, save_input)],
            SUCCESS_AUTH: [MessageHandler(Filters.text, save_input)],
            ERROR_AUTH: [MessageHandler(Filters.text, save_input)],
        },

        fallbacks=[CommandHandler('stop', stop)]
    )