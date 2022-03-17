from telegram import ReplyKeyboardMarkup
from model import get_invitation, store_invitation, update_invitation, delete_invitation
import config
from keybords import invitation_check_btn_markup
from telegram.ext import CallbackQueryHandler, ChatMemberHandler
from campaign import current_active_campaign
from telegram import Update, Chat, ChatMember, ParseMode, ChatMemberUpdated


def extract_status_change(chat_member_update):
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get(
        "is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = (old_status in [
        ChatMember.MEMBER,
        ChatMember.CREATOR,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True))
    is_member = (new_status in [
        ChatMember.MEMBER,
        ChatMember.CREATOR,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True))

    return was_member, is_member


def create_invitation(update, context):

    #first store the invitation with status of false
    invitation = {
        'ref_user_id': context.args[0],
        'inv_user_id': update.effective_user.id,
        'status': False
    }
    #create invitation once only
    if (not get_invitation(update.effective_user.id)):
        store_invitation(invitation)
        #second send the channel/group to Join
        channel_group = context.bot.get_chat(config.CHANNEL_GROUP_CHAT_ID)
        text = f"⚠️ You must join our {channel_group.type}\n\n @{channel_group.username}"
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text=text,
                                 reply_markup=invitation_check_btn_markup)


def check(update, context):
    query = update.callback_query
    channel_group = context.bot.get_chat(config.CHANNEL_GROUP_CHAT_ID)
    invitation = get_invitation(update.effective_user.id)
    #verify membership
    status = verify_user_membership(update, context, channel_group)
    if (status == 'left'):
        text = f"❌ First Join the channel pls.\n\n⚠️ You must join our {channel_group.type}\n\n @{channel_group.username}"
        context.bot.edit_message_text(chat_id=update.effective_user.id,
                                      message_id=query.message.message_id,
                                      text=text,
                                      reply_markup=invitation_check_btn_markup)
        # context.bot.send_message(chat_id=update.effective_user.id,
        #                          text='❌first Join/subscribe pls.')
    if (status == 'member'):
        #update the status of the invitation
        if (rule_for_referal_point(context, update.effective_user)):
            update_invitation(invitation['inv_user_id'])
            #send notification to the referal user
            context.bot.send_message(
                chat_id=invitation['ref_user_id'],
                text=
                f"✅ {update.effective_user.full_name} has been verified as your referral.\nGood Luck"
            )
        else:
            #delete invitation
            delete_invitation(update.effective_user.id)
        #sucess message
        text = f"✅ You Successfully Join the channel.\n\n⚠️ You must join our {channel_group.type}\n\n @{channel_group.username}"
        context.bot.edit_message_text(chat_id=update.effective_user.id,
                                      message_id=query.message.message_id,
                                      text=text)
        #current running campaign
        current_active_campaign(update, context)


check_callback_query_handler = CallbackQueryHandler(check,
                                                    pattern='check_joining')


def verify_user_membership(update, context, channel_group):
    member = context.bot.get_chat_member(chat_id=channel_group.id,
                                         user_id=update.effective_user.id)
    return member.status


def members_membership_status(update, context):
    result = extract_status_change(update.chat_member)
    if result is None:
        return
    was_member, is_member = result
    if (was_member and not is_member):
        #delete the invitation
        delete_invitation(update.chat_member.new_chat_member.user.id)

    # cause_name = update.chat_member.from_user.mention_html()
    # member_name = update.chat_member.new_chat_member.user.mention_html()

    # if not was_member and is_member:
    #     update.effective_chat.send_message(
    #         f"{member_name} was added by {cause_name}. Welcome!",
    #         parse_mode=ParseMode.HTML,
    #     )
    # elif was_member and not is_member:
    #     update.effective_chat.send_message(
    #         f"{member_name} is no longer with us. Thanks a lot, {cause_name} ...",
    #         parse_mode=ParseMode.HTML,
    #     )


members_membership_status_handler = ChatMemberHandler(
    members_membership_status, ChatMemberHandler.CHAT_MEMBER)


def rule_for_referal_point(context, inv_user):
    photos = context.bot.get_user_profile_photos(user_id=inv_user.id, limit=1)
    username = inv_user.username
    return photos.total_count and username
