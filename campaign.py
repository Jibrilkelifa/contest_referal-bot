from model import get_contest
from keybords import participants_btn_markup


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
        return f"⭐⭐Campaign⭐⭐\n\n📓 Description:{contest['info']}\n👑 Number of Winners:{contest['number_winners']}\n🎁 Reward:{contest['reward']}\n🕐 Start Time:{contest['start_date_time']}\n🕐 End Time:{contest['end_date_time']}"
    return False
