from states.create_project_states import *
from states.virtual_server_srates import *
from states.common_states import *
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup)
from sbcloud.sbcloud_helper import *

def start_dialog_vdpc(update, context):
    buttons = [[
        InlineKeyboardButton(text='+ ВЦОД VMware', callback_data=str(VM_WARE)),
        InlineKeyboardButton(text='+ ВЦОД KVM', callback_data=str(VM_WARE))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(reply_markup=keyboard)
    return START_CREATE_VDPC



def create_vdpc(update, context):
    ud = context.user_data
    ud[CONTRACT_ID] = get_contract_id(ud[HEDEARS])
    ud[PLAN_ID] = get_plan_id(ud[HEDEARS], ud[CONTRACT_ID])
    type_vdpc = update.callback_query.data
    ud[TYPE_VDPC] = type_vdpc
    if type_vdpc == VM_WARE:
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
    response_vdpc = sbcloud_create_vdpc(ud[VDPC], ud[HEDEARS])
    if response_vdpc.status_code == 200:
        text = "ВЦОД был успешно создан"
        ud[TENANT_ID] = get_vdpc_tenant_id(response_vdpc)
        sbcloud_response_tenant(ud[TENANT_ID], ud[HEDEARS])
        response_network = sbcloud_create_network(ud[HEDEARS])
        text += "\n Сеть была добавлена"
        sbcloud_response_tenant(ud[TENANT_ID], ud[HEDEARS])
        ud[NETWORK_ID] = get_network_id(response_network)
        sbcloud_create_router(ud[NETWORK_ID], ud[HEDEARS])
        text += "\n Роутер был добавлен"
        construct_server_conf(ud)
        if type_vdpc == VM_WARE:
            state_button = START_VM_WARE_SERVER
        else:
            state_button = START_KVM_SERVER
        buttons = [[
            InlineKeyboardButton(text='+ Верт.сервер', callback_data=str(state_button))
        ]]
    else:
        text = "ВЦОД не был создан код ошибки:" + str(response_vdpc.status_code)
        buttons = [[
            InlineKeyboardButton(text='Ещё раз', callback_data=str(REPLAY)),
            InlineKeyboardButton(text='Выйти', callback_data=str(END))
        ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return RESULT_CREATE_VDPC

def construct_server_conf(ud):
    sbcloud_response_tenant(ud[TENANT_ID], ud[HEDEARS])
    ud[ALL_NETWORKS] = get_all_networks(ud[HEDEARS])
    ud[ALL_ROUTERS] = get_all_routers(ud[HEDEARS])
    ud[ALL_OS] = get_all_os(ud[HEDEARS])
    ud[ALL_DISKS] = get_all_disk(ud[HEDEARS])
    # {"name": "server", "configuration": {"cpu": 2, "cores_per_socket": 2, "memory": 2048,
    #                                      "networks": [{"network_id": 433345, "auto_floating": false,
    #                                                    "fixed_ips": [{"subnet_id": 433347}]}],
    #                                      "disks": [{"size": 50, "profile_id": 291}]}, "flavor_id": 0,
    #  "security_groups": [], "os_id": 20017, "is_vmtemplate": false, "software": [20016]}
    ud[SERVER_CONF] = {
        "name": None,
        "configuration": {
            "cpu": None,
            "cores_per_socket": None,
            "memory": None,
            "networks": [],
            "disks": []
        }
        ,"flavor_id": 0
        ,"security_groups": [],
        "os_id": None,
        "is_vmtemplate": False,
        "software": None
    }


def show_conf_server(update, context):
    ud = context.user_data
    text = str(ud[SERVER_CONF])
    buttons = [[
        InlineKeyboardButton(text='Назад', callback_data=str(BACK)),
         ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return SHOWING

def start_create_vm_ware_server(update, context):
    buttons = [[
        InlineKeyboardButton(text='Название', callback_data=str(SERVER_NAME)),
        InlineKeyboardButton(text='CPU', callback_data=str(CPU)),
        InlineKeyboardButton(text='RAM', callback_data=str(RAM))],
        [InlineKeyboardButton(text='+ Диск', callback_data=str(DISK)),
        InlineKeyboardButton(text='Сеть', callback_data=str(NETWORK)),
        InlineKeyboardButton(text='О.С.', callback_data=str(OS))],
        [InlineKeyboardButton(text='Просмотреть', callback_data=str(SHOWING)),
        InlineKeyboardButton(text='Отправить', callback_data=str(SEND))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    text = 'Настройте сервер'
    if update.message is None:
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    return CONFIG_SERVER

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

def ask_for_input(update, context):
    ud = context.user_data
    ud[CURRENT_ATTRIBUTE] = update.callback_query.data
    current_attribute = ud[CURRENT_ATTRIBUTE]
    if current_attribute == SERVER_NAME:
        text = 'Напишите название сервера.'
    elif current_attribute == CPU:
        text = 'Укажите CPU сервера, допустимы натуральные числа от 1 до 32 ядер.'
    elif current_attribute == RAM:
        text = 'Укажите RAM сервера, допустимы натуральные числа от 1 до 132 (ГБ).'
    else:
        text = 'Напишите.'
    update.callback_query.edit_message_text(text=text)
    return SAVE_INPUT

#    ud[SERVER_CONF] = {
#         "name": None,
#         "configuration": {
#             "cpu": None,
#             "cores_per_socket": None,
#             "memory": None,
#             "networks": [],
#             "disks": []
#         }
#         ,"flavor_id": 0
#         ,"security_groups": [],
#         "os_id": None,
#         "is_vmtemplate": False,
#         "software": None
#     }

def save_input(update, context):
    ud = context.user_data
    current_attribute = ud[CURRENT_ATTRIBUTE]
    input = update.message.text
    if current_attribute == SERVER_NAME:
        ud[SERVER_CONF]["name"] = input
    elif current_attribute == CPU:
        if valid_number(1, 32, input):
            ud[SERVER_CONF]["configuration"]["cpu"] = int(input)
            ud[SERVER_CONF]["configuration"]["cores_per_socket"] = int(input)
        else:
            ud[ERROR_MSG] = 'CPU не сохранён, допустимы натуральные числа от 1 до 32 (ядера)'

    elif current_attribute == RAM:
        if valid_number(1, 132, input):
            ud[SERVER_CONF]["configuration"]["memory"] = int(input) * 1024
        else:
            ud[ERROR_MSG] = 'RAM не сохранён, допустимы натуральные числа от 1 Мб до 132 (ГБ)'
    if context.user_data.get(ERROR_MSG):
        show_error(ud[ERROR_MSG], update)
        context.user_data[ERROR_MSG] = False
    return start_create_vm_ware_server(update, context)

def show_error(error_msg, update):
    text = error_msg
    update.message.reply_text(text=text)



def req_create_server_to_sbcloud(update, context):
    ud = context.user_data
    server_conf = ud[SERVER_CONF]
    if valid_server_conf(server_conf):
        response = sbcloud_create_server(server_conf, ud[HEDEARS])
        if response.status_code == 200 or response.status_code == 202:
            text = 'Сервер успешно создан, пока'
            buttons = [[
                InlineKeyboardButton(text='Выход', callback_data=str(END)),
            ]]
        else:
            text = 'Сервер не был создан код ошибки:' + str(response.status_code)
            buttons = [[
                InlineKeyboardButton(text='Исправить', callback_data=str(REPEAT_OPERATION)),
                InlineKeyboardButton(text='Выход', callback_data=str(END))
            ]]
    else:
        text = 'Не все поля заполнены'
        buttons = [[
            InlineKeyboardButton(text='Исправить', callback_data=str(REPEAT_OPERATION)),
            InlineKeyboardButton(text='Выход', callback_data=str(END))
        ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return RESULT_OPERATION

def valid_server_conf(server_conf):
    if server_conf["name"] is None or server_conf["configuration"]["cpu"] is None or server_conf["configuration"]["memory"] is None \
        or server_conf["os_id"] is None or server_conf["is_vmtemplate"] is None or server_conf["software"] is None:
        return False
    else:
        return True


