from email import message

import telegram
from model import (get_contest, update_contest, get_total_participant,
                   get_total_invitation, update_contest_message_id,
                   delete_contest, truncate_all_tables, award, get_participant)
from keybords import participants_btn_markup, admin_btn_markup
import datetime
import config
import pytz
from constants import FINISHED, STARTED, NOT_STARTED_YET
from telegram.ext import (CallbackQueryHandler)
from constants import STARTED, NOT_STARTED_YET, FINISHED


def current_active_campaign(update, context):
    contest_detail, campaign_status = participant_campaign_detail()
    if (campaign_status == STARTED and contest_detail):
        text = f"{contest_detail}"
        if (get_participant(update.effective_user.id)):
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=text,
                                     parse_mode=telegram.ParseMode.HTML)
        else:
            context.bot.send_message(chat_id=update.effective_user.id,
                                     text=text,
                                     reply_markup=participants_btn_markup,
                                     parse_mode=telegram.ParseMode.HTML)
    else:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text="⚠️No live referral contest campaign at the moment!",
        )


def campaign_detail():
    contest = get_contest()
    if (contest):
        total_participant = get_total_participant()
        total_invitation = get_total_invitation()
        return f"{contest['info']}\n\n🏆<b>Number of winners:</b> {contest['number_winners']}\n🎁<b>Prize:</b> {contest['reward']}\n⏳<b>Start date:</b> {contest['start_date_time']} {config.TIMIZONE}\n⏳<b>End date:</b> {contest['end_date_time']} {config.TIMIZONE}\n-------------------\n🧵<b>Status:</b>{contest['status']}\n👬<b>TotalParticipants:</b>{total_participant}\n👬<b>Total Invitation:</b>{total_invitation}", contest[
            'id'], contest['status']

    return 0, 0, 0


def participant_campaign_detail():
    contest = get_contest()
    if (contest):
        total_participant = get_total_participant()
        total_invitation = get_total_invitation()
        return f"{contest['info']}\n\n🏆<b>Number of winners:</b> {contest['number_winners']}\n🎁<b>Prize:</b> {contest['reward']}\n⏳<b>Start date:</b> {contest['start_date_time']} {config.TIMIZONE}\n⏳<b>End date:</b> {contest['end_date_time']} {config.TIMIZONE}", contest[
            'status']

    return 0, 0


def update_status_campaign(context):
    contest = get_contest()
    if (contest):
        # 0 not started 1 started 2 finished
        start_time = datetime.datetime.strptime(contest['start_date_time'],
                                                config.DATETIME_FORMAT)
        end_time = datetime.datetime.strptime(contest['end_date_time'],
                                              config.DATETIME_FORMAT)
        now = datetime.datetime.now(pytz.timezone(config.TIMIZONE))
        now = datetime.datetime.strptime(now.strftime(config.DATETIME_FORMAT),
                                         config.DATETIME_FORMAT)
        if (start_time < now):
            if (contest['status'] == NOT_STARTED_YET):
                update_contest(contest['id'], STARTED)
                campaign, camapign_id, campaign_status = campaign_detail()
                text = f"🚀 The campaign is started.\n\n{campaign}"
                context.bot.edit_message_text(
                    chat_id=config.BOT_OWNER,
                    message_id=contest['message_id'],
                    text=text,
                    parse_mode=telegram.ParseMode.HTML)
                post_start_campaign(context)
        if (end_time < now):
            if (contest['status'] == STARTED):
                update_contest(contest['id'], FINISHED)
                post_end_campaign(context)
                send_end_campaign_notification_admin(context)
    else:
        print("zero campaign from scheduler")


def update_campaign_message_id(contest_id, message_id):
    update_contest_message_id(contest_id, message_id)


def delete_stop_discard_award_campaign(update, context):
    query = update.callback_query
    btn = query.data
    if (btn == 'delete_campaign'):
        delete_campaign(update, context)
    if (btn == 'winners_campaign'):
        winners_campaign(update, context)


def delete_campaign(update, context):
    contest = get_contest()
    query = update.callback_query

    if (contest['status'] == NOT_STARTED_YET or contest['status'] == FINISHED):
        query = update.callback_query
        truncate_all_tables()
        text = f"⭕the campaign is deleted successfully.\n\n{query.message.text}"
        context.bot.edit_message_text(chat_id=update.effective_user.id,
                                      message_id=query.message.message_id,
                                      text=text)
    else:
        text = f"⭕the campaign is already started you cant delete it.wait till it end.\n\n{query.message.text}"
        context.bot.edit_message_text(chat_id=update.effective_user.id,
                                      message_id=query.message.message_id,
                                      text=text)


def stop_campaign(update, context):
    query = update.callback_query
    contest = get_contest()
    update_contest(contest['id'], FINISHED)
    text = f"⭕the campaign is stoped successfully.for more options use the campaign button.\n\n{query.message.text}"
    context.bot.edit_message_text(chat_id=update.effective_user.id,
                                  message_id=query.message.message_id,
                                  text=text)


def winners_campaign(update, context):
    contest = get_contest()
    header = "<b>📢 List of Winners for the campaign! 📢</b>"

    l = award()
    if (l):
        winners = "Username\t\t\t\tWallet\n"
        campaign_number_winner = contest['number_winners']
        list_winners = l[:int(campaign_number_winner)]
        for (index, winner) in enumerate(list_winners):
            winners = winners + f"<b>{index+1}</b>@{winner[0]['username']}\t\t\t\t{winner[0]['wallet_address']}\n"
        winners = f"{winners}"
    else:
        winners = "⚠️ There are no participants and no winners for this campaign."

    text = f"{header}\n\n{winners}"
    context.bot.send_message(chat_id=config.BOT_OWNER,
                             text=text,
                             parse_mode=telegram.ParseMode.HTML)


def discard_campaign(update, context):
    truncate_all_tables()
    query = update.callback_query
    text = f"⭕Every thing that is related to this campaign is deleted.\n\n{query.message.text}"
    context.bot.edit_message_text(chat_id=update.effective_user.id,
                                  message_id=query.message.message_id,
                                  text=text)


delete_stop_discard_award_campaign_handler = CallbackQueryHandler(
    delete_stop_discard_award_campaign,
    pattern='delete_campaign|stop_campaign|winners_campaign|discard_campaign')


def post_end_campaign(context):
    contest = get_contest()
    header = "<b>📢 Referral contest campaign has ENDED! 📢</b>"

    l = award()
    if (l):
        congra = "Congratulations! Expect prizes on wallets that you provided shortly."
        winners = "Behold the winners🥇\n\n"
        campaign_number_winner = contest['number_winners']
        list_winners = l[:int(campaign_number_winner)]
        for (index, winner) in enumerate(list_winners):
            winners = winners + f"{index+1}. @{winner[0]['username']} with {winner[1]} points\n"
        winners = f"{winners}\n{congra}"
    else:
        winners = "⚠️ There are no participants and no winners for this campaign."

    note = f"For participating in future referral contest campaigns address to @{context.bot.username} 👈"
    text = f"{header}\n\n{winners}\n\n{note}"
    context.bot.send_message(chat_id=config.CHANNEL_GROUP_CHAT_ID,
                             text=text,
                             parse_mode=telegram.ParseMode.HTML)


def post_start_campaign(context):
    contest = get_contest()
    header = "<b>📢 New referral contest campaign has STARTED! 📢</b>"
    description = contest['info']
    bottom = f"🏆<b>Number of winners:</b> {contest['number_winners']}\n🎁<b>Prize:</b> {contest['reward']}\n⏳<b>Start date:</b> {contest['start_date_time']} {config.TIMIZONE}\n⏳<b>End date:</b> {contest['end_date_time']} {config.TIMIZONE}"
    note = f"For participating in this and future referral contest campaigns address to @{context.bot.username} 👈"
    text = f"{header}\n\n{description}\n\n{bottom}\n\n{note}"
    context.bot.send_message(chat_id=config.CHANNEL_GROUP_CHAT_ID,
                             text=text,
                             parse_mode=telegram.ParseMode.HTML)


def send_end_campaign_notification_admin(context):
    contest = get_contest()
    header = "<b>📢 Referral contest campaign has ENDED! 📢</b>"

    l = award()
    if (l):
        winners = "Username\t\t\t\tWallet\n"
        campaign_number_winner = contest['number_winners']
        list_winners = l[:int(campaign_number_winner)]
        for (index, winner) in enumerate(list_winners):
            winners = winners + f"{index+1}.@{winner[0]['username']}\t\t\t\t{winner[0]['wallet_address']}\n"
        winners = f"{winners}"
    else:
        winners = "⚠️ There are no participants and no winners for this campaign."

    # note = f"For participating in future referral contest campaigns address to @{context.bot.username} 👈"
    text = f"{header}\n\n{winners}"
    context.bot.send_message(chat_id=config.BOT_OWNER,
                             text=text,
                             parse_mode=telegram.ParseMode.HTML)
