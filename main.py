import asyncio
import pandas as pd
import re
import os
import sqlite3
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
#from dotenv import load_dotenv
import io
from keep_alive import keep_alive

keep_alive()

#load_dotenv()

api_id = os.environ.get('ApiId')
api_hash = os.environ.get('ApiHash')
source_chat_username = os.environ.get('SourceUsername')
destination_chat_username = os.environ.get('DestinationUsername')
csv_url = os.environ.get('CsvUrlForMagnetLinks')  # URL to download the CSV file from
session_url = os.environ.get('SessionUrl')  # URL to download the session file from

# Download the CSV file
csv_file_path = 'match_games.csv'
try:
    response = requests.get(csv_url)
    response.raise_for_status()
    with open(csv_file_path, 'wb') as f:
        f.write(response.content)
    print(f"CSV file downloaded and saved as {csv_file_path}")
except requests.exceptions.RequestException as e:
    print(f"Failed to download CSV file: {e}")
    exit(1)

# Verify the CSV file exists and can be read
try:
    match_names_df = pd.read_csv(csv_file_path)
    print("CSV file loaded successfully.")
except Exception as e:
    print(f"Failed to read CSV file: {e}")
    exit(1)

# Download the session file
session_file = 'forward.session'
try:
    session_response = requests.get(session_url)
    session_response.raise_for_status()
    with open(session_file, 'wb') as f:
        f.write(session_response.content)
    print(f"Session file downloaded and saved as {session_file}")

    # Check the size of the session file
    if os.path.getsize(session_file) == 0:
        print("Downloaded session file is empty.")
        exit(1)

    # Print the first few bytes of the session file
    with open(session_file, 'rb') as f:
        content = f.read(10)
        print(f"First 10 bytes of the session file: {content}")

except requests.exceptions.RequestException as e:
    print(f"Failed to download session file: {e}")
    exit(1)

# Ensure the session file exists
if not os.path.exists(session_file):
    print(f"Session file {session_file} does not exist.")
    exit(1)

# Verify the session file content
try:
    conn = sqlite3.connect(session_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables in session file: {tables}")
    conn.close()
except sqlite3.Error as e:
    print(f"Failed to read session file: {e}")
    exit(1)

session = 'forward'
# Initialize the Pyrogram Client with session file
app = Client(session, api_id=api_id, api_hash=api_hash)

magnet_regex = re.compile(r'magnet:\?xt=urn:btih:[a-zA-Z0-9]+.*')

def find_game_name(magnet_url):
    matched_row = match_names_df.loc[match_names_df['magnet_link'].apply(lambda x: x.strip()) == magnet_url.strip()]
    if not matched_row.empty:
        return matched_row.iloc[0]['game_name']
    return None

def entities_to_dict(entities):
    print("Client started successfully.")
    magnet_url_found = None
    
    for entity in entities:
        if entity.url:
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
        entities = message.entities
        magnet_url_found = entities_to_dict(entities) if entities else None
        
        game_name = None
        if magnet_url_found:
            game_name = find_game_name(magnet_url_found)

        #await asyncio.sleep(2)

        #await client.send_message(destination_chat_username, "/deletegame #Botlogfiles")

        #await asyncio.sleep(5)
        
        if game_name:
            await asyncio.sleep(5)
            await client.send_message(destination_chat_username, "/deletegame #Botlogfiles")
            await asyncio.sleep(5)
            await client.send_message(destination_chat_username, f"/newgame {game_name}")
        else:
            await asyncio.sleep(5)
            await client.send_message(destination_chat_username, "/newgame #Botlogfiles")
            await asyncio.sleep(5)
    elif message.media:
        await client.forward_messages(destination_chat_username, message.chat.id, [message.id])
        """await client.forward_messages(
            destination_chat_username,
            from_chat_id=message.chat.id,
            message_id=message.id,
            caption= {game_name} if game_name else message.caption,
            caption_entities=message.caption_entities
        )"""

@app.on_message(filters.chat(source_chat_username))
async def my_handler(client: Client, message: Message):
    if message.from_user and message.from_user.is_self:
        return
    await start_and_forward(client, message)

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        print(f"Error running the client: {e}")
