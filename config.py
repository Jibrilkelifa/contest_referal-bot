from decouple import config, Csv

BOT_TOKEN = config('BOT_TOKEN')
BOT_OWNERS = config('BOT_OWNERS', cast=Csv(int))
CHANNEL_GROUP_CHAT_ID = config('CHANNEL_GROUP_CHAT_ID')
DATETIME_FORMAT = config('DATETIME_FORMAT')
TIMIZONE = config('TIMIZONE')