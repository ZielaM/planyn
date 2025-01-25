import asyncio
import json
import os
import shutil

import aiofiles

from utils.constants import timetable, timetables


def save_timetables(timetables: timetables, directory: str) -> list[asyncio.Task]:
    tasks: list[asyncio.Task] = [] 
    
    shutil.rmtree(directory) if os.path.exists(directory) else None
    os.makedirs(directory)
    for timetable_name in timetables:
        tasks.append(asyncio.create_task(save_timetable(timetable_name, timetables[timetable_name], directory)))
    return tasks


async def save_timetable(timetable_name: str, timetable: timetable, directory: str) -> None:
    async with aiofiles.open(f'{directory}{timetable_name}.json', 'w', encoding='utf-8') as f:
        await f.write(json.dumps(timetable, ensure_ascii=False, indent=4))   
 

