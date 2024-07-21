import asyncio
import pandas as pd
import re
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from keep_alive import keep_alive
keep_alive()

api_id = os.environ.get('id')
api_hash = os.environ.get('hash')
session_string = 'Amelia/Amelia'
source_chat_username = os.environ.get('source')
destination_chat_username = os.environ.get('destination')

# Initialize the client
app = Client(session_string, api_id=api_id, api_hash=api_hash)

magnet_regex = re.compile(r'magnet:\?xt=urn:btih:[a-zA-Z0-9]+.*') #[a-zA-Z0-9]

# Load match_names.csv
try:
    match_names_df = pd.read_csv('match_names.csv')
except Exception as e:
    print(f"Error reading match_names.csv: {e}")
    raise

def find_game_name(magnet_url):
    matched_row = match_names_df.loc[match_names_df['magnet_link'].apply(lambda x: x.strip()) == magnet_url.strip()]
    if not matched_row.empty:
        return matched_row.iloc[0]['game_name']
    return None

def entities_to_dict(entities):
    magnet_url_found = None
    
    for entity in entities:
        if entity.url:
            # Search for magnet URLs along the entire length of the URL
            match = magnet_regex.search(entity.url)
            if match:
                magnet_url = match.group(0)
                print(f"Magnet URL detected: {magnet_url}")
                game_name = find_game_name(magnet_url)
                if game_name:
                    print(f"Game found: {game_name}")
                    magnet_url_found = magnet_url
                    break  # Stop searching after finding the first valid magnet URL
                else:
                    print("No game found")
            else:
                print("No magnet URL found")
    
    return magnet_url_found

async def start_and_forward(client: Client, message: Message):
    if message.text:
        # Send /start command to the destination chat
        await client.send_message(destination_chat_username, "/start")

        # Extract and restore entities from the text message
        entities = message.entities
        magnet_url_found = entities_to_dict(entities) if entities else None
        
        # Determine the game name
        game_name = None
        if magnet_url_found:
            game_name = find_game_name(magnet_url_found)

        await asyncio.sleep(5)
        
        # Send the appropriate message based on whether a game name was found
        if game_name:
            await client.send_message(destination_chat_username, f"/createfolder {game_name}")
        else:
            await client.send_message(destination_chat_username, "/createfolder Wasted")
    elif message.media:
        # Forward the media message untouched
        await client.forward_messages(destination_chat_username, message.chat.id, [message.id])

@app.on_message(filters.chat(source_chat_username))
async def my_handler(client: Client, message: Message):
    # Ignore messages sent by yourself
    if message.from_user and message.from_user.is_self:
        return
    await start_and_forward(client, message)

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        print(f"Error running the client: {e}")
