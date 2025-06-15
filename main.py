import asyncio
from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN
from database import Database
from scraper import fetch_ads

# Initialize bot and database
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
db = Database()

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Handler for the /start command."""
    user_id = event.sender_id
    db.add_user(user_id)
    await event.reply('Welcome to the Ikman.lk Ad Tracker Bot!\n\n'
                      'Use /subscribe <keyword> to start tracking ads.\n'
                      'Use /unsubscribe <keyword> to stop tracking.\n'
                      'Use /keywords to see your current subscriptions.')

@bot.on(events.NewMessage(pattern='/subscribe'))
async def subscribe(event):
    """Handler for the /subscribe command."""
    try:
        keyword = event.text.split(maxsplit=1)[1]
        user_id = event.sender_id
        db.subscribe(user_id, keyword)
        await event.reply(f"You have subscribed to '{keyword}'. Sending existing ads...")

        ads = fetch_ads(keyword)
        if not ads:
            await event.reply(f"No initial ads found for '{keyword}'.")
            return

        for ad in ads:
            ad_id = ad.get('id')
            if ad_id and not db.has_seen_ad(ad_id):
                ad_title = ad.get('title')
                ad_url = ad.get('url')
                ad_image = ad.get('image_url')
                ad_price = ad.get('price')
                ad_location = ad.get('location')
                ad_timestamp = ad.get('timeStamp')

                message = (f"**{keyword}**\n\n"
                           f"**Title:** {ad_title}\n"
                           f"**Price:** {ad_price}\n"
                           f"**Location:** {ad_location}\n"
                           f"**Posted:** {ad_timestamp}\n\n"
                           f"**Link:** {ad_url}")
                try:
                    if ad_image:
                        await bot.send_file(user_id, ad_image, caption=message)
                    else:
                        await bot.send_message(user_id, message)
                except Exception as e:
                    print(f"Failed to send message to {user_id}: {e}")
                
                db.add_seen_ad(ad_id)

    except IndexError:
        await event.reply("Please provide a keyword to subscribe. Usage: /subscribe <keyword>")

@bot.on(events.NewMessage(pattern='/unsubscribe'))
async def unsubscribe(event):
    """Handler for the /unsubscribe command."""
    try:
        keyword = event.text.split(maxsplit=1)[1]
        user_id = event.sender_id
        db.unsubscribe(user_id, keyword)
        await event.reply(f"You have unsubscribed from '{keyword}'.")
    except IndexError:
        await event.reply("Please provide a keyword to unsubscribe. Usage: /unsubscribe <keyword>")

@bot.on(events.NewMessage(pattern='/keywords'))
async def list_keywords(event):
    """Handler for the /keywords command."""
    user_id = event.sender_id
    keywords = db.get_user_keywords(user_id)
    if keywords:
        message = "Your current subscriptions:\n" + "\n".join(f"- {kw}" for kw in keywords)
    else:
        message = "You are not subscribed to any keywords."
    await event.reply(message)

async def check_for_new_ads():
    """Periodically checks for new ads and notifies users."""
    while True:
        print("Checking for new ads...")
        all_keywords = db.get_all_subscriptions()
        for keyword in all_keywords:
            ads = fetch_ads(keyword)
            for ad in ads:
                ad_id = ad.get('id')
                if ad_id and not db.has_seen_ad(ad_id):
                    ad_title = ad.get('title')
                    ad_url = ad.get('url')
                    ad_image = ad.get('image_url')
                    ad_price = ad.get('price')
                    ad_location = ad.get('location')
                    ad_timestamp = ad.get('timeStamp')

                    message = (f"**New Ad Found for '{keyword}'**\n\n"
                               f"**Title:** {ad_title}\n"
                               f"**Price:** {ad_price}\n"
                               f"**Location:** {ad_location}\n"
                               f"**Posted:** {ad_timestamp}\n\n"
                               f"**Link:** {ad_url}")
                    
                    users_to_notify = db.get_users_for_keyword(keyword)
                    for user_id in users_to_notify:
                        try:
                            if ad_image:
                                await bot.send_file(user_id, ad_image, caption=message)
                            else:
                                await bot.send_message(user_id, message)
                        except Exception as e:
                            print(f"Failed to send message to {user_id}: {e}")
                    db.add_seen_ad(ad_id)
        
        # Wait for 5 minutes before the next check
        await asyncio.sleep(300)

def main():
    """Main function to run the bot."""
    print("Bot started...")
    loop = asyncio.get_event_loop()
    loop.create_task(check_for_new_ads())
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
