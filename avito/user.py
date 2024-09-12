from avito.core import AvitoCore
import logging
from httpx import AsyncClient, HTTPStatusError
from utils import AvitoProfile

logging.basicConfig(level=logging.INFO)


class AvitoUser(AvitoCore):
    def __init__(self):
        super().__init__()

    async def get_profile(self):
        async with AsyncClient() as client:
            url = 'https://api.avito.ru/core/v1/accounts/self'
            await self.authenticate()
            response = await client.get(url, headers={'Authorization': f'Bearer {self.auth_cert}'})

            if response.status_code == 200:
                return AvitoProfile(**response.json())
            else:
                raise HTTPStatusError

    async def get_balance(self):
        async with AsyncClient() as client:
            profile = await self.get_profile()
            await self.authenticate()
            url = f'https://api.avito.ru/core/v1/accounts/{profile.id}/balance/'
            response = await client.get(url, headers={'Authorization': f'Bearer {self.auth_cert}'})

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPStatusError


if __name__ == "__main__":
    import asyncio

    user = AvitoUser()
    asyncio.run(user.authenticate())
    print(asyncio.run(user.get_profile()))
    print(asyncio.run(user.get_balance()))