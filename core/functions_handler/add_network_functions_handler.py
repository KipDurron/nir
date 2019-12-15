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


