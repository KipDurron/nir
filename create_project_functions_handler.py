from states.common_states import *

def show(update, context):
    ud = context.user_data
    update.callback_query.edit_message_text(text=ud[HEDEARS])
