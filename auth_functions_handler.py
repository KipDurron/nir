import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from sbcloud_helper import sbcloud_req_res

AUTH, SELECTING_ACTION, TYPING, LOGIN, PASSWORD, CURRENT_AUTH_DATA, AUTH_DATA, START_OVER, SUCCESS_AUTH, ERROR_AUTH = map(chr, range(10))
END = ConversationHandler.END


def start(update, context):
    reply_keyboard = [['Да','Нет']]
    update.message.reply_text(
        'Привет! Меня зовут VMStarter Bot. Я помогу создать виртуальный сервер в sbcloud. '
        'Напиши /stop для выхода из диалога со мной.\n\n'
        'Вы зарегестрированны в sbcloud?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SELECTING_ACTION


def start_auth(update, context):
    text = 'Введите свой логин и пароль'
    buttons = [[
        InlineKeyboardButton(text='Ввести логин', callback_data=str(LOGIN)),
        InlineKeyboardButton(text='Ввести пароль', callback_data=str(PASSWORD)),
        InlineKeyboardButton(text='Готово', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text=text, reply_markup=keyboard)
    if not context.user_data.get(START_OVER):
        context.user_data[AUTH_DATA] = {}
    context.user_data[START_OVER] = False
    return AUTH

def ask_for_input(update, context):
    context.user_data[CURRENT_AUTH_DATA] = update.callback_query.data
    text = 'Напишите'
    update.callback_query.edit_message_text(text=text)
    return TYPING

def save_input(update, context):
    ud = context.user_data
    ud[AUTH_DATA][ud[CURRENT_AUTH_DATA]] = update.message.text
    ud[START_OVER] = True
    return start_auth(update, context)

def stop(update, context):
    user = update.message.from_user
    update.message.reply_text('Пока!', reply_markup=ReplyKeyboardRemove())
    return END


def stop_auth(update, context):
    update.message.reply_text('Для того что бы создать виртуальный сервер необходимо зарегестрироваться на sbclod! Пока.', reply_markup=ReplyKeyboardRemove())
    return END

def req_auth_to_sbcloud(update, context):
    ud = context.user_data
    response = sbcloud_req_res(ud[AUTH_DATA][LOGIN], ud[AUTH_DATA][PASSWORD])
    if response.status_code == 200:
        text = 'Авторизация прошла успешна'
        result = SUCCESS_AUTH
    else:
        text = 'Авторизация не выполнена код ошибки:' + str(response.status_code)
        result = ERROR_AUTH
    update.callback_query.edit_message_text(text=text)
    return result