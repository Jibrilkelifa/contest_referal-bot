from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

admin_btn = [
    ['Campaign'],
]

admin_btn_markup = ReplyKeyboardMarkup(admin_btn, resize_keyboard=True)

campaign_btn = [
    [
        InlineKeyboardButton("STOP", callback_data=0),
    ],
]
campaign_btn_markup = InlineKeyboardMarkup(campaign_btn)

campaign_create_btn = [[
    InlineKeyboardButton('Create New Campaign',
                         callback_data='create_new_campaign')
]]

campaign_create_btn_markup = InlineKeyboardMarkup(campaign_create_btn)

participants_btn = [[
    InlineKeyboardButton('Click to Participate', callback_data='participant')
]]
participants_btn_markup = InlineKeyboardMarkup(participants_btn)

invitation_check_btn = [[
    InlineKeyboardButton('✅Check', callback_data='check_joining')
]]

invitation_check_btn_markup = InlineKeyboardMarkup(invitation_check_btn)

participants_mainmenu_btn = [['🙍My Profile', '🌍Share']]
participants_mainmenu_btn_markup = ReplyKeyboardMarkup(
    participants_mainmenu_btn, resize_keyboard=True)

submit_discard_btn = [[
    InlineKeyboardButton('✅ Submit', callback_data='submit_campaign'),
    InlineKeyboardButton('❌ Discard', callback_data='discard_campaign')
]]

submit_discard_btn_markup = InlineKeyboardMarkup(submit_discard_btn)