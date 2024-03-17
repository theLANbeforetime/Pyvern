from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.type import AuthScope
from discord.ext import tasks
import logging
import json
import discord
import asyncio
TARGET_SCOPES = [AuthScope.MODERATOR_READ_FOLLOWERS]

# set secrets for auth to twitch/discord from local secrets.json file
with open("secrets.json", "r") as secrets:
    secret_data=json.load(secrets)
    APP_ID = secret_data["twitch_app_id"]
    APP_SECRET = secret_data["twitch_app_secret"]
    DISCORD_TOKEN = secret_data["discord_token"]
    

# create the discord client instance
class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.check_data_loop.start()

    async def on_follow(self, data: any):
        print(data.to_dict())
        with open('live_status.json', 'w') as file:
            json.dump(data.to_dict(), file)
        

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        # create the api instance and get user auth either from storage or website
        twitch = await Twitch(APP_ID, APP_SECRET)
        helper = UserAuthenticationStorageHelper(twitch, TARGET_SCOPES)
        await helper.bind()
        
        #create eventsub websocket instance and start the client.
        eventsub = EventSubWebsocket(twitch)
        print('EventSub Registered')
        eventsub.start()
        print('EventSub Starting')
        user = await first(twitch.get_users(logins='veronyx'))
        print(f'User ID retrieved: ', user.id)
        await eventsub.listen_stream_online(user.id, self.on_follow)
        await eventsub.listen_stream_offline(user.id, self.on_follow)

    @tasks.loop(seconds=10)  # task runs every 10 seconds
    async def check_data_loop(self):
        print('Loop running...')
        channel = self.get_channel(1180815561307996160) #General: 1180815561307996160 Bot-Testing: 1208478666481209416
        print(f'Channel aquired: {channel}')
        with open('live_status.json', 'r') as file:
            json_data=json.load(file)
            print(f'Json data loaded: {json_data}')
            if json_data is not None:
                print('File is not empty. Proceeding...')
                if json_data["subscription"]["type"] is not None:
                    print('Trying to find match with stream.offline')
                    if json_data["subscription"]["type"] == 'stream.offline':
                        print('Match found for stream.offline')
                        async for message in channel.history(limit=50):
                            if "Veronyx is now streaming!" in message.content:
                                print('Deleting message...')
                                await message.delete()
                                print('Message deleted.')
                                break
                    print('stream.offline not found')
                    print('Trying to find match with stream.online')
                    if json_data["subscription"]["type"] == 'stream.online':
                        print('Match found for stream.online')
                        async for message in channel.history(limit=50):
                            if "Veronyx is now streaming!" in message.content:
                                print('Streamer alert already exists skipping creation.')
                                break
                            else:
                                print("Streaming message does not exist, starting message creation.")
                                await channel.send(
                                    f"@here \n :red_circle: **LIVE** \n Veronyx is now streaming! \n https://www.twitch.tv/veronyx"
                                )
                                print("Message created.")
                                break
                    else:
                        print('No subscription types found...')
            else:
                print('File is empty...')

    @check_data_loop.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in
    

client = MyClient(intents=discord.Intents.default())
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

def run():
    # Create discord instance
    print('Starting Discord')
    client.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)

asyncio.run(run())
