from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from states.auth_states import *
from states.common_states import *
from states.create_project_states import *
import auth_functions_handler, create_project_functions_handler

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
        entry_points=[CallbackQueryHandler(create_project_functions_handler.show, pattern='^' + str(CREATE_PROJECT) + '$')],
        states={
            SELECTING_ACTION: [MessageHandler(Filters.regex('^Да$'), auth_functions_handler.start_auth),
                               MessageHandler(Filters.regex('^Нет$'), auth_functions_handler.stop_auth)],
            AUTH: [CallbackQueryHandler(auth_functions_handler.ask_for_input, pattern='^(?!' + str(END) + ').*$'),
                   CallbackQueryHandler(auth_functions_handler.req_auth_to_sbcloud, pattern='^' + str(END) + '.*$')],
            TYPING: [MessageHandler(Filters.text, auth_functions_handler.save_input)],
        },

        fallbacks=[CommandHandler('stop', auth_functions_handler.stop)]
    )