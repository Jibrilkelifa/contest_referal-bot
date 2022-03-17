import telegram
from telegram.ext import (Filters, CommandHandler, MessageHandler,
                          ConversationHandler, CallbackQueryHandler)

from model import store_contest
import datetime
import pytz
from keybords import admin_btn_markup, admin_btn, campaign_create_btn_markup, submit_discard_btn_markup
from decorators import bot_owner_only
from model import get_contest
from participants import next_field
import config
from campaign import campaign_detail


@bot_owner_only
def admin(update, context):
    context.bot.send_message(chat_id=update.effective_user.id,
                             text='Hello, 👋 Welcome back.!',
                             reply_markup=admin_btn_markup)


admin_command_handler = CommandHandler('admin', admin)


@bot_owner_only
def campaign(update, context):
    campaign_detail_text = campaign_detail()
    if (campaign_detail_text):
        text = f"{campaign_detail_text}"
        context.bot.send_message(chat_id=update.effective_user.id, text=text)
    else:
        #create new campaign
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="NO Campaign.",
                                 reply_markup=campaign_create_btn_markup)


campaign_btn_handler = MessageHandler(Filters.text(admin_btn[0]), campaign)

INFO, START_DATE_TIME, END_DATE_TIME, REWARD, NUMBER_WINNERS, SUBMIT_DISCARD = range(
    6)


def temporay_user_data(context, key, value):
    context.user_data['new_contest'][key] = value


def create_contest_again(update, context):
    context.user_data['new_contest'] = {}
    context.bot.edit_message_text(
        chat_id=update.effective_user.id,
        message_id=update.message.message_id,
        text=
        "✏️You are now creating Campaign.\n\n to stop the process click /cancel"
    )
    next_field(update, context, '1.Enter  description for the Campaign?')
    return INFO


def create_contest(update, context):
    query = update.callback_query
    context.user_data['new_contest'] = {}
    context.bot.edit_message_text(
        chat_id=update.effective_user.id,
        message_id=query.message.message_id,
        text=
        "✏️You are now creating Campaign.\n\n to stop the process click /cancel"
    )
    next_field(update, context, '1.Enter  description for the Campaign?')
    return INFO


def accept_info(update, context):
    temporay_user_data(context, 'info', update.message.text)
    next_field(update, context, '2. Enter prize for the winners?')
    return REWARD


def accept_reward(update, context):
    temporay_user_data(context, 'reward', update.message.text)
    next_field(update, context, '3. Enter the number of winners?')
    return NUMBER_WINNERS


def accept_number_winners(update, context):
    temporay_user_data(context, 'number_winners', update.message.text)
    format = date_time_format()
    next_field(
        update, context,
        f'4. Enter start date of the campaign?\n\n use this format <b> {format}</b>'
    )
    return START_DATE_TIME


def accept_start_datetime(update, context):
    start_time = update.message.text
    context.user_data['new_contest']['start_date_time'] = start_time
    format = date_time_format()
    next_field(
        update, context,
        f'4. Enter End date of the campaign?\n\n use this format <b> {format}</b>'
    )
    return END_DATE_TIME


def accept_end_datetime(update, context):
    end_time = update.message.text
    context.user_data['new_contest']['end_date_time'] = end_time
    check_out_campaign(update, context)
    return SUBMIT_DISCARD


def submit(update, context):
    query = update.callback_query
    contest = context.user_data['new_contest']
    del context.user_data['new_contest']
    contest_detail = f"👉Description:{contest['info']}\n👉Number of Winners:{contest['number_winners']}\n👉Reward:{contest['reward']}\n👉Session:{contest['start_date_time']} -- {contest['end_date_time']}"
    store_contest(contest)
    context.bot.edit_message_text(
        chat_id=update.effective_user.id,
        message_id=query.message.message_id,
        text=f"✅the campaign created successfully.\n\n{contest_detail}")
    return ConversationHandler.END


def discard(update, context):
    query = update.callback_query
    contest = context.user_data['new_contest']
    del context.user_data['new_contest']
    contest_detail = f"👉Description:{contest['info']}\n👉Number of Winners:{contest['number_winners']}\n👉Reward:{contest['reward']}\n👉Session:{contest['start_date_time']} -- {contest['end_date_time']}"
    context.bot.edit_message_text(
        chat_id=update.effective_user.id,
        message_id=query.message.message_id,
        text=f"❌you discard the campign.\n\n{contest_detail}")
    return ConversationHandler.END


def check_out_campaign(update, context):
    contest = context.user_data['new_contest']
    contest_detail = f"👉Description:{contest['info']}\n👉Number of Winners:{contest['number_winners']}\n👉Reward:{contest['reward']}\n👉Session:{contest['start_date_time']} -- {contest['end_date_time']}"
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=contest_detail,
                             parse_mode=telegram.constants.PARSEMODE_HTML,
                             reply_markup=submit_discard_btn_markup)


def next_field(update, context, text):
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=text,
                             parse_mode=telegram.constants.PARSEMODE_HTML)


def cancel(update, context):
    del context.user_data['new_contest']
    update.message.reply_text('cancelled.')
    return ConversationHandler.END


def date_time_format():
    #now in  CET timezone utc+1
    now = datetime.datetime.now(pytz.timezone('CET'))
    return now.strftime(config.DATETIME_FORMAT)


new_contest_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(create_contest, pattern='create_new_campaign')
    ],
    states={
        INFO: [MessageHandler(Filters.text & (~Filters.command), accept_info)],
        REWARD:
        [MessageHandler(Filters.text & (~Filters.command), accept_reward)],
        NUMBER_WINNERS: [
            MessageHandler(Filters.text & (~Filters.command),
                           accept_number_winners)
        ],
        START_DATE_TIME: [
            MessageHandler(Filters.text & (~Filters.command),
                           accept_start_datetime)
        ],
        END_DATE_TIME: [
            MessageHandler(Filters.text & (~Filters.command),
                           accept_end_datetime)
        ],
        SUBMIT_DISCARD: [
            CallbackQueryHandler(submit, pattern='submit_campaign'),
            CallbackQueryHandler(discard, pattern='discard_campaign')
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel)])
