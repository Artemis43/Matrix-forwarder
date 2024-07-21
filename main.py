import os
from pyrogram import Client, filters
from keep_alive import keep_alive
keep_alive()

# Replace these with your own values
api_id = '26141034'
api_hash = 'bae00b7eecb7d2492f549e44cee5658e'
session_string = 'Amelia/Amelia.session'
source_chat_id = '@TheRescue_Team'
destination_chat_id = '@Hidden_in_matrix'

# Create a Pyrogram Client using the session string
app = Client(session_string, api_id=api_id, api_hash=api_hash)

@app.on_message(filters.chat(source_chat_id))
async def forward_messages(client, message):
    # Forward the message to the destination chat
    await message.forward(destination_chat_id)

# Run the bot
app.run()
