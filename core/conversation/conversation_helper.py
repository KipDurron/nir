from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler
from states.auth_states import *
from states.common_states import *
from states.create_project_states import *
from states.virtual_server_srates import *
from core.functions_handler import auth_functions_handler, create_project_functions_handler, \
    create_server_functions_handler, add_disk_functions_handler


def first_auth_conversation():
    return ConversationHandler(
        entry_points=[CommandHandler('start', auth_functions_handler.start)],
        states={
            SELECTING_ACTION: [MessageHandler(Filters.regex('^Да$'), auth_functions_handler.start_auth),
                               MessageHandler(Filters.regex('^Нет$'), auth_functions_handler.stop_auth)],
            AUTH: [CallbackQueryHandler(auth_functions_handler.ask_for_input, pattern='^(?!' + str(END) + ').*$'),
                   CallbackQueryHandler(auth_functions_handler.req_auth_to_sbcloud, pattern='^' + str(END) + '.*$')],
            TYPING: [MessageHandler(Filters.text, auth_functions_handler.save_input)],
            RESULT_AUTH: [create_project_conversation(),
                          CallbackQueryHandler(auth_functions_handler.start_auth, pattern='^' + str(REPEAT_AUTH) + '$'),
                          CallbackQueryHandler(auth_functions_handler.stop, pattern='^' + str(END) + '$')],
        },

        fallbacks=[CommandHandler('stop', auth_functions_handler.stop)]
    )

def create_project_conversation():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(create_project_functions_handler.start_create_project, pattern='^' + str(CREATE_PROJECT) + '$')],
        states={
            CREATE_PROJECT: [CallbackQueryHandler(create_project_functions_handler.ask_for_input, pattern='^' + str(PROJECT_NAME) + '$'),
                             CallbackQueryHandler(create_project_functions_handler.req_create_project_to_sbcloud, pattern='^' + str(END) + '.*$')],
            TYPING: [MessageHandler(Filters.text, create_project_functions_handler.save_input)],
            RESULT_OPERATION: [create_server_conversation(),
                               CallbackQueryHandler(create_project_functions_handler.start_create_project, pattern='^' + str(CREATE_PROJECT) + '$'),
                               CallbackQueryHandler(auth_functions_handler.stop, pattern='^' + str(END) + '$')],
        },

        fallbacks=[CommandHandler('stop', auth_functions_handler.stop)]
    )


def create_server_conversation():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(create_server_functions_handler.create_vdpc, pattern='^' + str(VM_WARE) + '$|^' + str(KVM) + '$')],
        states={
            START_CREATE_VDPC: [CallbackQueryHandler(create_server_functions_handler.create_vdpc, pattern='^' + str(VM_WARE) + '$|^' + str(KVM) + '$')],

            RESULT_CREATE_VDPC: [
                         CallbackQueryHandler(create_server_functions_handler.start_create_vm_ware_server, pattern='^' + str(START_VM_WARE_SERVER) + '$'),
                         CallbackQueryHandler(auth_functions_handler.stop, pattern='^' + str(END) + '$'),
                         CallbackQueryHandler(create_server_functions_handler.start_dialog_vdpc, pattern='^' + str(REPLAY) + '$')],

            CONFIG_SERVER: [CallbackQueryHandler(create_server_functions_handler.ask_for_input, pattern='^' + str(SERVER_NAME) + '$|^' + str(CPU) + '$' + '$|^' + str(RAM) + '$'),
                            add_disk_conversation(),
                            CallbackQueryHandler(create_server_functions_handler.req_create_server_to_sbcloud, pattern='^' + str(SEND) + '$')],

            SAVE_INPUT: [MessageHandler(Filters.text, create_server_functions_handler.save_input)],

            RESULT_OPERATION: [
                         CallbackQueryHandler(create_server_functions_handler.start_create_vm_ware_server, pattern='^' + str(REPEAT_OPERATION) + '$'),
                         CallbackQueryHandler(auth_functions_handler.stop, pattern='^' + str(END) + '$')],
        },

        fallbacks=[CommandHandler('stop', auth_functions_handler.stop)]
    )

def add_disk_conversation():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(add_disk_functions_handler.start_create_disk, pattern='^' + str(DISK) + '$')],
        states={
            CREATE_DISK: [CallbackQueryHandler(create_project_functions_handler.ask_for_input, pattern='^' + str(PROJECT_NAME) + '$'),
                             CallbackQueryHandler(create_project_functions_handler.req_create_project_to_sbcloud, pattern='^' + str(END) + '.*$')],
            # TYPING: [MessageHandler(Filters.text, create_project_functions_handler.save_input)],
            # RESULT_OPERATION: [create_server_conversation(),
            #                    CallbackQueryHandler(create_project_functions_handler.start_create_project, pattern='^' + str(CREATE_PROJECT) + '$'),
            #                    CallbackQueryHandler(auth_functions_handler.stop, pattern='^' + str(END) + '$')],
        },

        fallbacks=[CommandHandler('stop', auth_functions_handler.stop)]
    )