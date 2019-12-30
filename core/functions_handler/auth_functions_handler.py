from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from sbcloud.sbcloud_helper import sbcloud_req_res, get_headers_by_auth_resp
from states.auth_states import *
from states.common_states import *
from states.create_project_states import CREATE_PROJECT

def start(update, context):
    reply_keyboard = [['Да','Нет']]
    update.message.reply_text(
        'Привет! Я ваш облачный бот-инженер. Помогаю создавать и управлять виртуальными ЦОД на sbcloud.ru.'
        'Напиши /stop для выхода из диалога со мной.\n\n'
        'Вы уже зарегистрированы на sbcloud.ru?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SELECTING_ACTION


def start_auth(update, context):
    text = 'Введите свой логин и пароль'
    buttons = [[
        InlineKeyboardButton(text='Логин', callback_data=str(LOGIN)),
        InlineKeyboardButton(text='Пароль', callback_data=str(PASSWORD)),
        InlineKeyboardButton(text='Отправить', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    if update.message is None:
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
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
    text = 'Пока!'
    if update.message is None:
        update.callback_query.edit_message_text(text=text)
    else:
        update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
    return END


def stop_auth(update, context):
    update.message.reply_text('Для того чтобы создать виртуальный сервер необходимо зарегистрироваться на sbcloud.ru! Пока.', reply_markup=ReplyKeyboardRemove())
    return END

def req_auth_to_sbcloud(update, context):
    ud = context.user_data
    response = sbcloud_req_res(ud[AUTH_DATA][LOGIN], ud[AUTH_DATA][PASSWORD])
    if response.status_code == 200:
        ud[HEDEARS] = get_headers_by_auth_resp(response)
        text = 'Авторизация прошла успешна'
        buttons = [[
            InlineKeyboardButton(text='Создать проект', callback_data=str(CREATE_PROJECT)),
            InlineKeyboardButton(text='Авторизация', callback_data=str(REPEAT_AUTH)),
            InlineKeyboardButton(text='Выход', callback_data=str(END))
        ]]
        keyboard = InlineKeyboardMarkup(buttons)
    else:
        text = 'Авторизация не выполнена код ошибки:' + str(response.status_code)
        buttons = [[
            InlineKeyboardButton(text='Авторизация', callback_data=str(REPEAT_AUTH)),
            InlineKeyboardButton(text='Выход', callback_data=str(END))
        ]]
        keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return RESULT_AUTH
