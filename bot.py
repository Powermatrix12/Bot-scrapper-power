from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, MONGO_URI
import time
import pymongo

# Initialize MongoDB client
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client['media_scraper_db']
collection = db['media']

# Initialize the bot
bot = Client("MediaScraperBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command
@bot.on_message(filters.command("start") & filters.user(OWNER_ID))
async def start(client, message):
    await message.reply("Hello! Send /scrape @anybot to start scraping media.")

# Scrape command
@bot.on_message(filters.command("scrape") & filters.user(OWNER_ID))
async def scrape(client, message):
    if len(message.command) < 2:
        await message.reply("Please provide a bot username to scrape media from.")
        return

    target_bot = message.command[1]
    await message.reply(f"Starting to scrape media from {target_bot}...")

    async for media in bot.iter_history(target_bot):
        try:
            if media.media:
                # Save to MongoDB
                collection.insert_one({"media_id": media.message_id, "chat_id": media.chat.id, "type": media.media})
                await message.reply(f"Saved {media.media} with message_id {media.message_id}")
                time.sleep(1)  # Avoiding rate limits
        except FloodWait as e:
            time.sleep(e.value)
        except Exception as e:
            await message.reply(f"Error: {e}")

    await message.reply("Scraping completed!")

bot.run()
