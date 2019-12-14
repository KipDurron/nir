from states.create_project_states import *
from states.virtual_server_srates import *
from states.common_states import *
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from sbcloud.sbcloud_helper import *



def start_create_disk(update, context):
    ud = context.user_data
    text = 'Настройте диск'
    buttons = [[
        InlineKeyboardButton(text='Тип', callback_data=str(SERVER_NAME)),
        InlineKeyboardButton(text='Память', callback_data=str(CPU)),
        InlineKeyboardButton(text='Назад', callback_data=str(BACK)),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    if update.message is None:
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)
    if not context.user_data.get(START_OVER):
        context.user_data[CREATE_PROJECT_DATA] = {}
    return CREATE_DISK

def ask_for_input(update, context):
    context.user_data[CURRENT_ATTRIBUTE] = update.callback_query.data
    text = 'Напишите.'
    update.callback_query.edit_message_text(text=text)
    return TYPING


def save_input(update, context):
    ud = context.user_data
    ud[CREATE_PROJECT_DATA][ud[CURRENT_ATTRIBUTE]] = update.message.text
    ud[START_OVER] = True
    return start_create_disk(update, context)


def req_create_project_to_sbcloud(update, context):
    ud = context.user_data
    response = sbcloud_create_project(ud[CREATE_PROJECT_DATA][PROJECT_NAME], ud[HEDEARS])
    if response.status_code == 200:
        text = 'Проект успешно создан'
        ud[PROJECT_ID] = get_field_from_response_project(response, 'id')
        ud[ORG_ID] = get_field_from_response_project(response, 'org_id')
        buttons = [[
            InlineKeyboardButton(text='+ ВЦОД VMware', callback_data=str(VM_WARE)),
            InlineKeyboardButton(text='+ ВЦОД KVM', callback_data=str(VM_WARE))
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
