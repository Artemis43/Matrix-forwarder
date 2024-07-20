import asyncio
import pandas as pd
import json
import re
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from keep_alive import keep_alive
keep_alive()

# Credentials
api_id = os.environ.get('id')
api_hash = os.environ.get('hash')
phone_number = os.environ.get('phone')
source_chat_username = os.environ.get('source')
destination_chat_username = os.environ.get('destination')

# Initialize the client
app = Client("R1_forwarder", api_id=api_id, api_hash=api_hash, phone_number=phone_number)

magnet_regex = re.compile(r'magnet:\?xt=urn:btih:[a-zA-Z0-9]+.*')

# Load match_names.csv
match_names_df = pd.read_csv('match_names.csv')

def find_game_name(magnet_url):
    matched_row = match_names_df.loc[match_names_df['magnet_link'] == magnet_url]
    if not matched_row.empty:
        return matched_row.iloc[0]['game_name']
    return None

def entities_to_dict(entities):
    entity_dicts = []
    magnet_url_found = None
    
    for entity in entities:
        entity_dict = {
            'type': str(entity.type),  # Convert to string
            'offset': entity.offset,
            'length': entity.length,
            'url': entity.url if entity.url else None,
            'user': entity.user.id if entity.user else None,
            'language': entity.language if entity.language else None
        }
        
        if entity_dict['url']:
            # Search for magnet URLs along the entire length of the URL
            match = magnet_regex.search(entity_dict['url'])
            if match:
                magnet_url = match.group(0)
                print(f"Magnet URL detected: {magnet_url}")
                game_name = find_game_name(magnet_url)
                if game_name:
                    print(f"Game found: {game_name}")
                    magnet_url_found = magnet_url
                else:
                    print("No game found")
            else:
                print("No magnet URL found")
        
        entity_dicts.append(entity_dict)
    
    return entity_dicts, magnet_url_found

async def start_and_forward(client: Client, message: Message):
    if message.text:
        # Send /stop command to the destination chat
        #await client.send_message(destination_chat_username, "/stop")
        
        # Wait for 5 seconds
        #await asyncio.sleep(5)
        
        # Send /start command to the destination chat
        await client.send_message(destination_chat_username, "/start")
        
        # Wait for another 5 seconds
        await asyncio.sleep(5)
        
        # Extract and restore entities from the text message
        entities = message.entities
        entities_dict, magnet_url_found = entities_to_dict(entities) if entities else (None, None)
        
        # Determine the game name
        game_name = None
        if magnet_url_found:
            game_name = find_game_name(magnet_url_found)
        
        # Send the appropriate message based on whether a game name was found
        if game_name:
            await client.send_message(destination_chat_username, f"/createfolder {game_name}")
        else:
            await client.send_message(destination_chat_username, "/createfolder ConfigFiles")
    elif message.media:
        # Forward the media message untouched
        await client.forward_messages(destination_chat_username, message.chat.id, [message.id])
    
    # Wait for 5 seconds before the next message
    await asyncio.sleep(5)

@app.on_message(filters.chat(source_chat_username))
async def my_handler(client: Client, message: Message):
    # Ignore messages sent by yourself
    if message.from_user and message.from_user.is_self:
        return
    await start_and_forward(client, message)

if __name__ == "__main__":
    app.run()
