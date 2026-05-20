# API Keys
API_KEY="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"
TOKEN_BOT="8868858321:AAFLEjdOOpVx2yclRygma3ASpxnV4S7heoM"

# user ID to whom error messages are sent
ADMIN_ID = 123456789

# User IDs to which the bot will react "specially" in chat
SPECIAL_IDS=[]

# Maximum number of attempts to send an AI request
MAX_TRY=2

# AI model for text generation
MODEL="deepseek/deepseek-v4-flash:free"

# AI model for image recognition
MODEL_IM="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"

# The second model for image recognition, which will be used for the second and subsequent attempts
MODEL_IM2="google/gemma-4-31b-it:free"

# Allow the admin (ADMIN_ID) to describe the image themselves if the AI ​​was unable to do so
ADMIN_DESCRIP_IM=False

# Whitelist config 
WHITELIST_PRIVATE=False # Is whitelisting enabled for private messages
WHITELIST=[ADMIN_ID, 123456789] # User IDs in the whitelist
NO_WHITELIST_M="Sorry, but you can't use this bot in private messages because you are not on the whitelist." # The message sent to the user if they are not on the whitelist. Leave blank if you do not want this message to be sent.
WHITELIST_CHAT=True # Is whitelisting enabled for chat
WHITE_CHATS=[-1234567890123, -3210987654321] # Chat IDs in the whitelist

# If these lines are in the message, the bot will not respond.
PHRASE_BLOCKLIST=[]

# Will the bot analyze and respond to each photo that is in the same media group
REPLY_ALL_PHOTO = False

# Chance of response, a number from 0 to 1 (0 - will never respond, 1 - always responds)
CHANCE_COMMENTS=1 # a chance to leave a comment under the post
CHANCE_REPLY=0.7 # chance to reply if the user replied to the bot's message
CHANCE_CHAT=1 # a chance to reply to a random message in chat

# Maximum number of attempts to send an AI request
MAX_TRY=2
