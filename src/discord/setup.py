from discord.ext import tasks
import logging
import json
import discord


# create the discord client instance
class DiscordClient(discord.Client):

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

    @tasks.loop(seconds=10)  # task runs every 10 seconds
    async def check_data_loop(self):
        logging.info('Loop is running.')
        channel = self.get_channel(1180815561307996160) #General: 1180815561307996160 Bot-Testing: 1208478666481209416
        logging.info(f'Channel aquired: {channel}')
        with open('live_status.json', 'r') as file:
            json_data=json.load(file)
            logging.debug(f'Json data loaded: {json_data}')
            if json_data is not None:
                logging.debug('File is not empty. Proceeding...')
                if json_data["subscription"]["type"] is not None:
                    logging.debug('Trying to find match with stream.offline')
                    if json_data["subscription"]["type"] == 'stream.offline':
                        logging.debug('Match found for stream.offline')
                        async for message in channel.history(limit=50):
                                if "Veronyx is now streaming!" in message.content:
                                    logging.info('Deleting message...')
                                    await message.delete()
                                    logging.info('Message deleted.')
                                    break
                    logging.debug('stream.offline not found')
                    logging.debug('Trying to find match with stream.online')
                    if json_data["subscription"]["type"] == 'stream.online':
                        logging.debug('Match found for stream.online')
                        messages = [message async for message in channel.history(limit=50)]
                        live_notifications = []
                        for message in messages:
                            if "Veronyx is now streaming!" in message.content:
                                live_notifications.append(message)
                        if not live_notifications:
                            logging.info("Streaming message does not exist, starting message creation.")
                            await channel.send(
                                f"@here \n :red_circle: **LIVE** \n Veronyx is now streaming! \n https://www.twitch.tv/veronyx"
                            )
                            logging.info("Message created.")
                        else:
                            logging.debug("Notification exists")
                    else:
                        logging.debug('No subscription types found...')
            else:
                logging.debug('File is empty...')

    @check_data_loop.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in