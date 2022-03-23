from telegram import ReplyKeyboardMarkup
from model import get_invitation, store_invitation, store_new_member, update_invitation, delete_invitation, get_member
import config
from keybords import invitation_check_btn_markup
from telegram.ext import CallbackQueryHandler, ChatMemberHandler
from campaign import current_active_campaign
from telegram import Update, Chat, ChatMember, ParseMode, ChatMemberUpdated
from participants import home


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
    #new invited
    if (not get_invitation(update.effective_user.id)):
        store_invitation(invitation)
        #second send the channel/group to Join
        channel_group = context.bot.get_chat(config.CHANNEL_GROUP_CHAT_ID)
        text = f"👉 Join our microcap discussion group and make sure to solve the captcha for it to count. You will also gain an opportunity to participate in our regular referral contests and win prizes! Plus you'll help the person that referred you to be one step closer to win the event that is live at the moment!\n\nOur group 👉 @{channel_group.username}"
        context.bot.send_message(chat_id=update.effective_user.id, text=text)
    #already invited
    if (get_invitation(update.effective_user.id)):
        #redirect to home
        home(update, context)


def members_membership_status(update, context):
    result = extract_status_change(update.chat_member)
    member = update.chat_member.new_chat_member.user
    invitation = get_invitation(member.id)
    if result is None:
        return
    if (invitation):
        was_member, is_member = result
        if (was_member and not is_member):
            #delete the invitation
            delete_invitation(update.chat_member.new_chat_member.user.id)
            cause_member = update.chat_member.from_user
            # cause_member {'is_bot': False, 'last_name': 'Yesuf', 'first_name': 'Siraj', 'username': 'sirajyesuf2', 'language_code': 'en', 'id': 2079061914}
            # cause_member {'id': 660783114, 'is_bot': True, 'first_name': 'The Join Captcha Bot', 'username': 'join_captcha_bot'}
            # print("cause_member", cause_member)
            if (cause_member.is_bot):
                context.bot.send_message(
                    chat_id=invitation['ref_user_id'],
                    text=f"❌{member.full_name} can't solve the captcha!")
            else:
                context.bot.send_message(
                    chat_id=invitation['ref_user_id'],
                    text=f"❌{member.full_name} left the group!")

        if (not was_member and is_member):
            #is member in the past
            if (not is_old_member(member)):
                #update the status of the invitation
                if (rule_for_referal_point(context, member)):
                    #update the invitation status to true
                    update_invitation(member.id)
                    #store the user as new member
                    store_new_member({'user_id': member.id})

                    #send notification to the referral user
                    context.bot.send_message(
                        chat_id=invitation['ref_user_id'],
                        text=
                        f"✅{update.effective_user.full_name} has been verified as your referral!"
                    )
                    #sucess message
                    text = f"✅You have successfully joined the group!"
                    context.bot.send_message(chat_id=update.effective_user.id,
                                             text=text)
                else:
                    #delete invitation
                    delete_invitation(update.effective_user.id)
                    #store the user as new member
                    store_new_member({'user_id': member.id})
            else:
                #delete invitation
                delete_invitation(update.effective_user.id)
                #send notification to the referre
                context.bot.send_message(
                    chat_id=invitation['ref_user_id'],
                    text=
                    f"❌{update.effective_user.full_name} has already joined the group in the past!"
                )


members_membership_status_handler = ChatMemberHandler(
    members_membership_status, ChatMemberHandler.CHAT_MEMBER)


def rule_for_referal_point(context, inv_user):
    photos = context.bot.get_user_profile_photos(user_id=inv_user.id, limit=1)
    username = inv_user.username
    return photos.total_count and username
    # return True


def is_old_member(inv_user):
    return get_member(inv_user.id)
