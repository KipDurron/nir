from core.functions_handler.create_server_functions_handler import start_create_vm_ware_server
from states.create_project_states import *
from states.virtual_server_srates import *
from states.common_states import *
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from sbcloud.sbcloud_helper import *


def back_to_conf_server(update, context):
    """Return to top level conversation."""
    context.user_data[START_DISK] = None
    start_create_vm_ware_server(update, context)
    return BACK

def start_create_disk(update, context):
    ud = context.user_data
    text = 'Настройте диск'
    buttons = [[
        InlineKeyboardButton(text='Тип', callback_data=str(TYPE_DISK)),
        InlineKeyboardButton(text='Объём', callback_data=str(MEMORY_DISK)),
        InlineKeyboardButton(text='Сохранить', callback_data=str(SEND)),
        InlineKeyboardButton(text='Назад', callback_data=str(BACK)),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    if update.message is None:
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)
    if not context.user_data.get(START_DISK):
        context.user_data[CREATE_DISK_DATA] = {"size": None, "profile_id": None}
    return CREATE_DISK

def select_type_disk(update, context):
    ud = context.user_data
    all_disks = ud[ALL_DISKS]
    buttons = [[]]
    text = 'Выберите тип диска'
    for disk in all_disks["storage_profiles"]:
        buttons[0].append(InlineKeyboardButton(text=str(disk['name']), callback_data=str(disk['id'])))
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return SAVE_DISK

def save_type_disk(update, context):
    ud = context.user_data
    id_disk = update.callback_query.data
    ud[CREATE_DISK_DATA]["profile_id"] = int(id_disk)
    ud[START_DISK] = True
    return start_create_disk(update, context)


def ask_for_input(update, context):
    context.user_data[CURRENT_ATTRIBUTE] = update.callback_query.data
    text = 'Укажите ёмкость диска в ГБ (от 50 до 50000).'
    update.callback_query.edit_message_text(text=text)
    return SAVE_DISK


def save_memory(update, context):
    ud = context.user_data
    memory = update.message.text
    if valid_number(50, 50000, memory):
        ud[CREATE_DISK_DATA]["size"] = int(update.message.text)
        ud[START_DISK] = True
    else:
        ud[ERROR_MSG] = 'Недопустимое значение объёма. Укажите целое число от 50 до 50000 ГБ.'
        update.message.reply_text(text=ud[ERROR_MSG])
    return start_create_disk(update, context)

def valid_number(first, last, number):
    try:
        val = int(number)
        if val < first:
            return False
        if val > last:
            return False
        else:
            return True

    except ValueError:
        return False

def save_disk(update, context):
    ud = context.user_data
    disk = ud[CREATE_DISK_DATA]
    if valid_disk(disk):
        text = 'Диск добавлен.'
        ud[SERVER_CONF]["configuration"]["disks"].append(disk)
        ud[START_DISK] = None
        buttons = [[
            InlineKeyboardButton(text='Назад', callback_data=str(BACK)),
        ]]
    else:
        text = 'Диск не добавлен. Пожалуйста, заполните все поля.'
        buttons = [[
            InlineKeyboardButton(text='Повторить', callback_data=str(FAIL)),
        ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return RESULT_OPERATION

def valid_disk(disk):
    try:
        if disk["profile_id"] is None or disk["size"] is None:
            return False
        else:
            return True
    except Exception:
        return False