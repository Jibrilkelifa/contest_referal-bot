import telegram
from telegram.ext import (Filters, CommandHandler, MessageHandler,
                          ConversationHandler, CallbackQueryHandler)

from model import store_contest
import datetime
import pytz
from keybords import admin_btn_markup, admin_btn, campaign_create_btn_markup, submit_discard_btn_markup, campaign_btn__delete_markup, campaign_btn__stop_markup, campaign_finished_btn_markup
from decorators import bot_owner_only
from model import get_contest, get_participant_by_username, get_list_invited_by_referre
from participants import next_field
import config
from constants import NOT_STARTED_YET, STARTED, FINISHED
from campaign import campaign_detail, update_campaign_message_id


@bot_owner_only
def admin(update, context):
    context.bot.send_message(chat_id=update.effective_user.id,
                             text='Hello, 👋 Welcome back.!',
                             reply_markup=admin_btn_markup)


admin_command_handler = CommandHandler('admin', admin)


@bot_owner_only
def campaign(update, context):
    campaign_detail_text, campaign_id, campaign_status = campaign_detail()
    if (campaign_detail_text):
        text = f"{campaign_detail_text}"
        if (campaign_status == NOT_STARTED_YET):
            btn = campaign_btn__delete_markup
            note = "Note:\n✔️ press the Delete button to remove this one  and create new campaign"
            resp = context.bot.send_message(chat_id=update.effective_user.id,
                                            text=f"{text}\n\n{note}",
                                            reply_markup=btn,
                                            parse_mode=telegram.ParseMode.HTML)
            update_campaign_message_id(campaign_id, resp.message_id)

        if (campaign_status == FINISHED):
            btn = campaign_finished_btn_markup
            note = "Note:\n✔️ press the Winners button to see list of winners.\n✔️ press the Delete button to delete the campaign and related data"
            resp = context.bot.send_message(chat_id=update.effective_user.id,
                                            text=f"{text}\n\n{note}",
                                            reply_markup=btn,
                                            parse_mode=telegram.ParseMode.HTML)
            update_campaign_message_id(campaign_id, resp.message_id)
        if (campaign_status == STARTED):
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=f"{text}",
                                     parse_mode=telegram.ParseMode.HTML)

    else:
        #create new campaign
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text="❗zero campaign. use the button below to create new one.",
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
    # contest_detail = f"{contest['info']}\n{contest['number_winners']}\n{contest['reward']}\n{contest['start_date_time']}\n{contest['end_date_time']}"
    contest_detail = f"{contest['info']}\n\n🏆<b>Number of winners:</b> {contest['number_winners']}\n🎁<b>Prize:</b> {contest['reward']}\n⏳<b>Start date:</b> {contest['start_date_time']} {config.TIMIZONE}\n⏳<b>End date:</b> {contest['end_date_time']} {config.TIMIZONE}"

    store_contest(contest)
    context.bot.edit_message_text(
        chat_id=update.effective_user.id,
        message_id=query.message.message_id,
        text=
        f"✅the campaign created successfully.Click the Campaign button for more Detail.\n\n{contest_detail}",
        parse_mode=telegram.ParseMode.HTML)
    campaign(update, context)
    return ConversationHandler.END


def discard(update, context):
    query = update.callback_query
    contest = context.user_data['new_contest']
    del context.user_data['new_contest']
    # contest_detail = f"{contest['info']}\n{contest['number_winners']}\n{contest['reward']}\n{contest['start_date_time']}\n{contest['end_date_time']}"
    contest_detail = f"{contest['info']}\n\n🏆<b>Number of winners:</b> {contest['number_winners']}\n🎁<b>Prize:</b> {contest['reward']}\n⏳<b>Start date:</b> {contest['start_date_time']} {config.TIMIZONE}\n⏳<b>End date:</b> {contest['end_date_time']} {config.TIMIZONE}"
    context.bot.edit_message_text(
        chat_id=update.effective_user.id,
        message_id=query.message.message_id,
        text=f"❌you discard the campign.\n\n{contest_detail}",
        parse_mode=telegram.ParseMode.HTML)
    return ConversationHandler.END


def check_out_campaign(update, context):
    contest = context.user_data['new_contest']
    contest_detail = f"{contest['info']}\n\n🏆<b>Number of winners:</b> {contest['number_winners']}\n🎁<b>Prize:</b> {contest['reward']}\n⏳<b>Start date:</b> {contest['start_date_time']} {config.TIMIZONE}\n⏳<b>End date:</b> {contest['end_date_time']} {config.TIMIZONE}"
    context.bot.send_message(chat_id=update.effective_user.id,
                             text=contest_detail,
                             reply_markup=submit_discard_btn_markup,
                             parse_mode=telegram.ParseMode.HTML)


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
    now = datetime.datetime.now(pytz.timezone(config.TIMIZONE))
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


#get list of members of invited member by specific referre
@bot_owner_only
def get_list_invited_member(update, context):
    try:
        participant = get_participant_by_username(
            update.message.text.split(" ")[1])
        l = []
        for inv in get_list_invited_by_referre(participant['user_id']):
            user = context.bot.get_chat(chat_id=inv['inv_user_id'])
            l.append(user.username)
        text = f"☑️list of invited members by @{participant['username']}\n\n"
        if (l):
            for inv in l:
                text = text + f"@{inv}\n"
            context.bot.send_message(chat_id=config.BOT_OWNER, text=text)
        else:
            context.bot.send_message(chat_id=config.BOT_OWNER,
                                     text=text + '❗zero invited users.')
    except (IndexError,TypeError) as e:
        context.bot.send_message(
            chat_id=config.BOT_OWNER,
            text='❌ please only use one space b/n the command and the username')


get_list_invited_member_command_handler = CommandHandler(
    'invited', get_list_invited_member)
