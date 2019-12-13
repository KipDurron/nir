from states.create_project_states import *
from states.virtual_server_srates import *
from states.common_states import *
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from sbcloud.sbcloud_helper import *


def create_vdpc(update, context):
    ud = context.user_data
    ud[CONTRACT_ID] = get_contract_id(ud[HEDEARS])
    ud[PLAN_ID] = get_plan_id(ud[HEDEARS], ud[CONTRACT_ID])
    if update.callback_query.data == VM_WARE:
        hypervisor_id = 'vsphere'
    else:
        hypervisor_id = 'openstack'
    ud[VDPC] = {
        'hypervisor_id': hypervisor_id,
        'create_immediately': True,
        'name': 'vsphere VDC for project' + str(ud[PROJECT_ID]),
        'project_id': ud[PROJECT_ID],
        'contract_id': ud[CONTRACT_ID],
        'org_id': str(ud[ORG_ID]),
        'plan_id': ud[PLAN_ID],
        'rts_status': "pending",
        'rts_type': "vdc"
    }
    response = sbcloud_create_vdpc(ud[VDPC], ud[HEDEARS])
    if response.status_code == 200:
        text = "ВЦОД был успешно создан"
        buttons = [[
            InlineKeyboardButton(text='+ Верт.сервер', callback_data=str(START_VERTUAL_SERVER))
        ]]
    else:
        text = "ВЦОД не был создан код ошибки:" + str(response.status_code)
        buttons = [[
            InlineKeyboardButton(text='Ещё раз', callback_data=str(FAIL)),
            InlineKeyboardButton(text='Выйти', callback_data=str(END))
        ]]
    update.callback_query.edit_message_text(text=text)
    return RESULT_CREATE_VDPC

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
            InlineKeyboardButton(text='ВЦОД VMware', callback_data=str(VM_WARE)),
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
