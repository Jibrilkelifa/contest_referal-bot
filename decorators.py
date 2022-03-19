from functools import wraps
import config
from model import get_participant
from telegram import ReplyKeyboardRemove


def bot_owner_only(func):

    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        chat_id = update.effective_user.id
        if (str(chat_id) in config.BOT_OWNER):
            func(update, context, *args, **kwargs)
        else:
            update.message.reply_text(
                '❌You are not owner of the bot.stop giving me commands.')

    return wrapper


def participant_only(func):

    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        if (get_participant(update.effective_user.id)):
            func(update, context, *args, **kwargs)
        else:
            context.bot.send_message(
                chat_id=update.effective_user.id,
                text=
                "⚠️Not available until you register on live referral contest!",
            )

    return wrapper
