from distutils.command.config import config

from decouple import config

BOT_TOKEN = config('BOT_TOKEN')
BOT_OWNERS = config('BOT_OWNERS')
CHANNEL_GROUP_CHAT_ID = config('CHANNEL_GROUP_CHAT_ID')
DATETIME_FORMAT = config('DATETIME_FORMAT')