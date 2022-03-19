import re
from telegram.ext import (CommandHandler, MessageFilter, ConversationHandler,
                          MessageHandler, Filters, CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, constants

from model import get_rank, get_total_participant, store_participant, get_participant, get_number_invitation, get_contest
from keybords import participants_mainmenu_btn_markup
from decorators import participant_only
from campaign import current_active_campaign


class FilterEmail(MessageFilter):

    def filter(self, message):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if (re.fullmatch(regex, message.text)):
            return True
        message.reply_text('enter a valid email address.')
        return False


filter_email_address = FilterEmail()

EMAIL, WALLET_ADDRESS = range(2)


def start_registration_participant(update, context):
    query = update.callback_query
    context.user_data['new_participant'] = {}
    context.bot.edit_message_text(
        chat_id=update.effective_user.id,
        message_id=query.message.message_id,
        text=
        "✏️You are now Registering for Campaign.\n\n to stop the process click /cancel"
    )
    text = f" Your Email address:\n\nEnter pls\n\n This address will be used for future,to reach you."
    next_field(update, context, text)
    return EMAIL


def accept_email_participant(update, context):
    temporay_user_data(context, 'email', update.message.text)
    text = f" Your wallet address:\n\nEnter pls\n\n This address will be used for future,please use the correct format"
    next_field(update, context, text)
    return WALLET_ADDRESS


def accept_wallet_address(update, context):
    temporay_user_data(context, 'wallet_address', update.message.text)
    get_user_detail(update, context)
    store_participant(context.user_data['new_participant'])
    del context.user_data['new_participant']
    show_participant(update, context)
    return ConversationHandler.END


def next_field(update, context, text):
    context.bot.send_message(chat_id=update.effective_user.id, text=text)


def cancel(update, context):
    update.message.reply_text('cancelled.')
    return ConversationHandler.END


def get_user_detail(update, context):
    user = update.effective_user
    username = user.username
    user_id = user.id
    full_name = user.full_name
    temporay_user_data(context, 'username', username)
    temporay_user_data(context, 'user_id', user_id)
    temporay_user_data(context, 'full_name', full_name)


def temporay_user_data(context, key, value):
    context.user_data['new_participant'][key] = value


def show_participant(update, context):
    participant = get_participant(update.effective_user.id)
    link = f"https://t.me/{context.bot.username}?start={participant['user_id']}"
    text = f"👨‍🦱\n\n 👉Full Name: {participant['full_name']}\n👉Email: {participant['email']}\n👉Wallet: {participant['wallet_address']}\n👉Link:{link}"
    context.bot.send_message(chat_id=update.effective_user.id, text=text)


participant_registration_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_registration_participant,
                             pattern='participant')
    ],
    states={
        EMAIL: [
            MessageHandler(
                (Filters.text & (~Filters.command)) & filter_email_address,
                accept_email_participant)
        ],
        WALLET_ADDRESS: [
            MessageHandler(Filters.text & (~Filters.command),
                           accept_wallet_address)
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel)])

btn = ['🏠Home', 'Contests', '🙍Profile', '🌍Share']


def main_menu(update, context):
    if (update.message.text == btn[0]):
        home(update, context)
    if (update.message.text == btn[1]):
        current_active_campaign(update, context)
    if (update.message.text == btn[2]):
        my_profile(update, context)
    if (update.message.text == btn[3]):
        share(update, context)


def home(update, context):
    text = f"Hi {update.effective_user.full_name}!"
    if (get_participant(update.effective_user.id)):
        rank = get_rank(update.effective_user.id)
        text = f"{text}\n\n{rank}"
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=text,
                             reply_markup=participants_mainmenu_btn_markup)

@participant_only
def my_profile(update, context):
    participant = get_participant(update.effective_user.id)
    number_successfull_invitations = get_number_invitation(
        participant['user_id'])
    text = f"👤 User: {participant['full_name']}\n📧 Email: {participant['email']}\n🏦 Wallet:{participant['wallet_address']}\n👥 Total Referral: {number_successfull_invitations}"
    context.bot.send_message(chat_id=update.effective_user.id, text=text)

@participant_only
def share(update, context):
    participant = get_participant(update.effective_user.id)
    campaign = get_contest()
    number_successfull_invitations = get_number_invitation(
        participant['user_id'])
    url = get_share_link(context, participant)
    share_reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('👋 Share Link', url=url)]])
    text = f"Share bot with your Friends and win {campaign['reward']}\n\n👋 Total referrals: {number_successfull_invitations}\n\n<b>Note</b>\nFake,empty or spam users are deleted after checking\n\nYour referral link ⤵️"
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=text,
                             reply_markup=share_reply_markup,
                             parse_mode=constants.PARSEMODE_HTML)


participant_main_menu_handler = MessageHandler(Filters.text(btn), main_menu)


def get_share_link(context, participant):
    url = f"https://t.me/{context.bot.username}?start={participant['user_id']}"
    return f"https://telegram.me/share/url?url={url}"
