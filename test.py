import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs

async def foo(cs: aiohttp.ClientSession, i: int) -> None:
    async with cs.get(f'https://www.zsk.poznan.pl/plany_lekcji/2023plany/technikum/plany/o{i}.html') as response:
        print(i, response.status, bs(await response.text(), 'html.parser').find('span', class_ = 'tytulnapis').text.split(' ')[0])
    

async def main():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(1, 32):
            tasks.append(asyncio.create_task(foo(session, i)))
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())