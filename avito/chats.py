from distutils.command.clean import clean

from avito.user import AvitoUser
import logging
from httpx import AsyncClient, HTTPStatusError
from utils import ChatsInfo

logging.basicConfig(level=logging.INFO)


class AvitoChats(AvitoUser):

    def __init__(self):
        super().__init__()
        self.chat_ids = list()

    async def get_chats(self):
        async with AsyncClient() as client:
            await self.authenticate()
            profile = await self.get_profile()
            url = f'https://api.avito.ru/messenger/v2/accounts/{profile.id}/chats'

            response = await client.get(url, headers={'Authorization': f'Bearer {self.auth_cert}'})

            if response.status_code == 200:
                data = response.json()
                print(data)
                chats = ChatsInfo(**data)
                self.chat_ids = [
                    {chat['id']: chat['users'][1]['name']}
                    for chat in chats.chats if chat['users']
                ]
                return chats
            else:
                raise HTTPStatusError(response=response)

    async def send_message(self, chat_id: str, text: str):
        async with AsyncClient() as client:
            await self.authenticate()
            profile = await self.get_profile()

            url = f'https://api.avito.ru/messenger/v1/accounts/{profile.id}/chats/{chat_id}/messages'
            data = {
                "message": {
                "text": text
                },
                "type": "text"
            }
            response = await client.post(url, json=data, headers={'Authorization': f'Bearer {self.auth_cert}'})
            if response.status_code == 200:
                return True
            else:
                return False

if __name__ == "__main__":
    import asyncio

    chats = AvitoChats()
    asyncio.run(chats.authenticate())
    asyncio.run(chats.get_chats())
    #asyncio.run(chats.send_message(chat_id='u2i-LK173UEiNsbuL0zr1T13eQ', text='test!!!'))
    print(chats.chat_ids)
