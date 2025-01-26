import asyncio
import json

from aiohttp import ClientSession
from dotenv import load_dotenv

from utils.constants import JSON_PATH, teachers_type, classrooms_type, grades_type, plain_text_type
from utils.getting import get_timetable, get_number_of_timetables
from utils.saving import save_timetables, save_timetable
from utils.inserting import add_spaces_to_names


async def main() -> None:
    print('number of timetables: ', num_of_timetables := get_number_of_timetables())
    # getting timetables
    tasks: list[asyncio.Task] = list()  # list to store tasks (getting timetables)
    async with ClientSession() as session:
        for i in range(1, num_of_timetables + 1):
            tasks.append(asyncio.create_task(get_timetable(session, i, TIMETABLES, PLAIN_TEXT, LESSON_NAMES)))  # create tasks for each timetable
        await asyncio.gather(*tasks)

    tasks.clear()  # list to store tasks (saving timetables; see inside of the function)
    
    print('number of lessons', len(LESSON_NAMES))
    
    global TEACHERS_TIMETABLES, CLASSROOMS_TIMETABLES, GRADES_TIMETABLES
    add_spaces_to_names(LESSON_NAMES, TEACHERS_TIMETABLES, CLASSROOMS_TIMETABLES, GRADES_TIMETABLES)  # add spaces to lesson names
    
    filenames: dict[str, list[str]] = dict()  # dictionary to store filenames
    
    # saving teachers' timetables
    path = f'{JSON_PATH}timetables/teachers/'
    tasks.extend(save_timetables(TEACHERS_TIMETABLES, path))
    filenames[path] = [f'{filename}.json' for filename in list(TEACHERS_TIMETABLES.keys())] # add the filenames to the dictionary

    # saving classrooms' timetables
    path = f'{JSON_PATH}timetables/classrooms/'
    tasks.extend(save_timetables(CLASSROOMS_TIMETABLES, path))
    filenames[path] = [f'{filename}.json' for filename in list(CLASSROOMS_TIMETABLES.keys())] # add the filenames to the dictionary
    
    # saving grades' timetables
    path = f'{JSON_PATH}timetables/grades/'
    tasks.extend(save_timetables(GRADES_TIMETABLES, path))
    filenames[path] = [f'{filename}.json' for filename in list(GRADES_TIMETABLES.keys())] # add the filenames to the dictionary
    
    filenames = dict(sorted(filenames.items()))  # sort the filenames
    for path in filenames.keys():
        filenames[path].sort()  # sort the filenames
    tasks.append(asyncio.create_task(save_timetable('filenames', filenames, JSON_PATH)))  # save the filenames to the file (used for creating the main menu in the mobile app)

    # saving plain text
    with open(f'{JSON_PATH}plain_text.json', 'w', encoding='utf-8') as f:
        json.dump(PLAIN_TEXT, f, ensure_ascii=False, indent=4, sort_keys=True)  # save the PLAIN_TEXT dictionary to the file (used for creating PLAIN_TEXT_SOLUTION in other program)
    
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    load_dotenv() 
    
    # tiemetables dictionaries
    TEACHERS_TIMETABLES: teachers_type = dict()
    CLASSROOMS_TIMETABLES: classrooms_type = dict()
    GRADES_TIMETABLES: grades_type = dict()
    PLAIN_TEXT: plain_text_type = dict()  # Variable to store plain text lessons (later exported and used in other program to get PLAIN_TEXT_SOLUTION)
    LESSON_NAMES: set[str] = set() # holds distinct lesson names
    
    TIMETABLES: tuple[teachers_type, classrooms_type, grades_type] = (TEACHERS_TIMETABLES, CLASSROOMS_TIMETABLES, GRADES_TIMETABLES)  # Tuple to store all timetables dictionaries

    asyncio.run(main())   # run the main
