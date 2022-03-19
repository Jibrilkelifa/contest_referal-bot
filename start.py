from telegram import ReplyKeyboardRemove
from telegram.ext import CommandHandler
from invitation import create_invitation, get_invitation
from campaign import current_active_campaign
from model import get_participant
from participants import home


def start(update, context):
    if (context.args):
        #get invited user
        create_invitation(update, context)

    else:
        home(update, context)

    # if (get_participant(update.effective_user.id)):
    #     context.bot.send_message(chat_id=update.effective_user.id,
    #                              text='Hello, 👋 Welcome back.!')
    # else:
    #     context.bot.send_message(chat_id=update.effective_user.id,
    #                              text='Hello, 👋 Welcome back.!',
    #                              reply_markup=ReplyKeyboardRemove())
    #     current_active_campaign(update, context)


start_command_handler = CommandHandler('start', start)
