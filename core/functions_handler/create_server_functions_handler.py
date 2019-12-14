from states.create_project_states import *
from states.virtual_server_srates import *
from states.common_states import *
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
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
    {"name": "server", "configuration": {"cpu": 2, "cores_per_socket": 2, "memory": 2048,
                                         "networks": [{"network_id": 433345, "auto_floating": false,
                                                       "fixed_ips": [{"subnet_id": 433347}]}],
                                         "disks": [{"size": 50, "profile_id": 291}]}, "flavor_id": 0,
     "security_groups": [], "os_id": 20017, "is_vmtemplate": false, "software": [20016]}
    ud[SERVER_CONF] = {
        "name": None,
        "configuration": {
            "cpu": None,
            "cores_per_socket": None,
            "memory": None,
            "networks": [],
            "disks": [],
            "flavor_id": 0
        }
    }


def start_create_vm_ware_server(update, context):
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
    return start_create_vm_ware_server(update, context)


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
