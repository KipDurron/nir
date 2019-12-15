from core.functions_handler.add_disk_functions_handler import back_to_conf_server
from states.virtual_server_srates import *
from states.common_states import *
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from sbcloud.sbcloud_helper import *



def select_network(update, context):
    ud = context.user_data
    all_network = ud[ALL_NETWORKS]
    buttons = [[]]
    text = 'Выберите сеть'
    for network in all_network["networks"]:
        buttons[0].append(InlineKeyboardButton(text=str(network['name']) + get_subnets_str(network), callback_data=str(network['id'])))
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return SAVE

def save_network(update, context):
    ud = context.user_data
    all_network = ud[ALL_NETWORKS]
    id_network = int(update.callback_query.data)
    network = get_network_by_id(id_network, all_network["networks"])
    fixed_ips = get_fixed_ips(network)
    ud[SERVER_CONF]["configuration"]["networks"] = [{"network_id":id_network,
                                                     "auto_floating": False,
                                                     "fixed_ips": fixed_ips}]
    return back_to_conf_server(update, context)

def select_os(update, context):
    ud = context.user_data
    all_os = ud[ALL_OS]
    buttons = [[]]
    text = 'Выберите О.С.'
    for os in all_os["products"]:
        buttons[0].append(InlineKeyboardButton(text=str(os['name']), callback_data=str(os['id'])))

    keyboard = InlineKeyboardMarkup(buttons)
    # update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    update.callback_query.edit_message_text(text=text,reply_markup=keyboard)
    return SAVE

def save_os(update, context):
    ud = context.user_data
    os_id = int(update.callback_query.data)
    os = get_os_by_id(os_id, ud[ALL_OS]["products"])
    ud[SERVER_CONF]["os_id"] = os_id
    if not os is None:
        software_id = get_software_id(os)
        ud[SERVER_CONF]["software"] = [software_id]
    else:
        ud[SERVER_CONF]["software"] = []

    return back_to_conf_server(update, context)

