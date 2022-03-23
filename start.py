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


start_command_handler = CommandHandler('start', start)
