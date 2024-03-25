from src.twitch.setup import TwitchClient
from twitchAPI.type import AuthScope
import logging
import json
import discord
from asyncio import Runner
from src.discord.setup import DiscordClient
TARGET_SCOPES = [AuthScope.MODERATOR_READ_FOLLOWERS]

TEST_CHANNEL = 1208478666481209416
GENERAL_CHANNEL = 1180815561307996160

# set secrets for auth to twitch/discord from local secrets.json file
with open("secrets.json", "r") as secrets:
    secret_data=json.load(secrets)
    APP_ID = secret_data["twitch_app_id"]
    APP_SECRET = secret_data["twitch_app_secret"]
    DISCORD_TOKEN = secret_data["discord_token"]

discord_client = DiscordClient(intents=discord.Intents.default())
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
twitch_client = TwitchClient(app_id=APP_ID, app_secret=APP_SECRET, target_app_auth_scope=TARGET_SCOPES)

async def start_twitch():
    print('Starting Twitch')
    await twitch_client.open_websocket()

def start_discord():
    print('Starting Discord Bot')
    discord_client.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.INFO, root_logger=True)

# asyncio.run(start_twitch())
with Runner() as runner:
    runner.run(start_twitch())
    runner.run(start_discord())