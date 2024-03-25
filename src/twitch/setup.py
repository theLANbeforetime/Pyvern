from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.type import AuthScope
import twitchAPI.twitch
import json

TARGET_SCOPES = [AuthScope.MODERATOR_READ_FOLLOWERS]

# twitch = await Twitch(APP_ID, APP_SECRET)
class TwitchClient(twitchAPI.twitch.Twitch):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        async def authenticate(self):
            helper = UserAuthenticationStorageHelper(self, TARGET_SCOPES)
            await helper.bind()

        async def on_follow(self, data: any):
            print(data.to_dict())
            with open('live_status.json', 'w') as file:
                json.dump(data.to_dict(), file)
            
        async def open_websocket(self):
            # create the api instance and get user auth either from storage or website
            await self.authenticate()
            # #create eventsub websocket instance and start the client.
            print('Registering event sub...')
            eventsub = EventSubWebsocket(self)
            print('EventSub Registered')
            eventsub.start()
            print('EventSub Starting')
            user = await first(self.get_users(logins='veronyx'))
            print(f'User ID retrieved: ', user.id)
            await eventsub.listen_stream_online(user.id, self.on_follow)
            print('Subscribed to stream online')
            await eventsub.listen_stream_offline(user.id, self.on_follow)
            print('Subscribed to stream offline')

        def run(self):
             self.open_websocket()
              