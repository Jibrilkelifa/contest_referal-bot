from functools import wraps
import config


def bot_owner_only(func):

    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        chat_id = update.effective_user.id
        if (str(chat_id) in config.BOT_OWNERS):
            func(update, context, *args, **kwargs)
        else:
            update.message.reply_text(
                '❌You are not owner of the bot.stop giving me commands.')

    return wrapper


def admins_only(func):

    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        admin_list = []
        for admin in context.bot.get_chat_administrators(
                update.message.chat.id):
            admin_list.append(admin.user.id)

        if (update.effective_user.id in admin_list
                or update.effective_user.is_bot):
            func(update, context, *args, **kwargs)
        else:
            update.message.reply_text(
                '❌You are not admin of any group.stop giving me commands.')

    return wrapper
