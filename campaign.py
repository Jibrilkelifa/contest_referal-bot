from asyncio import constants
from re import L
from model import get_contest, update_contest, get_total_participant, get_total_invitation
from keybords import participants_btn_markup
import datetime
import config
import pytz
from constants import FINISHED, STARTED, NOT_STARTED_YET


def current_active_campaign(update, context):
    contest_detail = campaign_detail()
    if (contest_detail):
        text = f"{contest_detail}"
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=text,
            reply_markup=participants_btn_markup,
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Currently No Active Campaign.stay tunned.",
        )


def campaign_detail():
    contest = get_contest()
    if (contest):
        total_participant = get_total_participant()
        total_invitation = get_total_invitation()
        return f"⭐⭐Campaign⭐⭐\n\n📓 Description:{contest['info']}\n👑 Number of Winners:{contest['number_winners']}\n🎁 Reward:{contest['reward']}\n🕐 Start Time:{contest['start_date_time']}\n🕐 End Time:{contest['end_date_time']}\n-------------------\n🧵Status:{contest['status']}\n👬TotalParticipants:{total_participant}\n👬Total Invitation:{total_invitation}"

    return False


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
                # send notification to the admin
                for admin in config.BOT_OWNERS:
                    context.bot.send_message(
                        chat_id=admin, text="the campaign is now started.")
                #forward the campaign to the group/channel
                # campaign = campaign_detail()
                # text = f"{campaign}\n\n{context.bot.username}"
                # context.bot.send_message(chat_id=config.CHANNEL_GROUP_CHAT_ID,
                #                          text=text)
        if (end_time < now):
            if (contest['status'] == STARTED):
                update_contest(contest['id'], FINISHED)
                for admin in config.BOT_OWNERS:
                    context.bot.send_message(
                        chat_id=admin, text="the campaign is now finished.")
    else:
        print("zero campaign from scheduler")
