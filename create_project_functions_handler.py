from states.common_states import *
from states.create_project_states import *
from states.common_states import *
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from  sbcloud_helper import *


def start_create_project(update, context):
    buttons = [[
        InlineKeyboardButton(text='Название', callback_data=str(PROJECT_NAME)),
        InlineKeyboardButton(text='Отправить', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    if update.message is None:
        text = 'Напишите название проекта'
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        text = 'Отправте результат'
        update.message.reply_text(text=text, reply_markup=keyboard)
    if not context.user_data.get(START_OVER):
        context.user_data[CREATE_PROJECT_DATA] = {}
    return CREATE_PROJECT

def ask_for_input(update, context):
    context.user_data[CURRENT_ATTRIBUTE] = update.callback_query.data
    text = 'Напишите.'
    update.callback_query.edit_message_text(text=text)
    return TYPING


def save_input(update, context):
    ud = context.user_data
    ud[CREATE_PROJECT_DATA][ud[CURRENT_ATTRIBUTE]] = update.message.text
    ud[START_OVER] = True
    return start_create_project(update, context)


def req_create_project_to_sbcloud(update, context):
    ud = context.user_data
    response = sbcloud_create_project(ud[CREATE_PROJECT_DATA][PROJECT_NAME], ud[HEDEARS])
    if response.status_code == 200:
        text = 'Проект успешно создан'
        buttons = [[
            InlineKeyboardButton(text='Создать ВЦОД', callback_data=str(CREATE_VDPC)),
        ]]
        keyboard = InlineKeyboardMarkup(buttons)

    else:
        text = 'Проект не был создан код ошибки:' + str(response.status_code)
        buttons = [[
            InlineKeyboardButton(text='Создать проект', callback_data=str(CREATE_PROJECT)),
            InlineKeyboardButton(text='Выход', callback_data=str(END))
        ]]
        keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return RESULT_OPERATION
