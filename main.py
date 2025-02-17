import asyncio
import os

from aiohttp import ClientSession
from dotenv import load_dotenv
import google.generativeai as genai

from utils.constants import JSON_PATH, SPACED_LESSONS, PLAIN_TEXT, teachers_type, classrooms_type, grades_type
from utils.getting import get_timetable, get_number_of_timetables
from utils.saving import save_timetables, save_timetable

async def main() -> None:
    print('Searching for timetables to get...')
    print('Found: ', num_of_timetables := get_number_of_timetables(), ' timetables...')
    
    # establishing connection with Gemini
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash-exp', system_instruction='dodaj spacje do nazwy lekcji')  # model for adding spaces to the lesson titles
    requests_num = {'num': 0}
    
    # getting timetables
    print('Getting data from timetables...')
    tasks: list[asyncio.Task] = list()  # list to store tasks (getting timetables)
    async with ClientSession() as session:
        for i in range(1, num_of_timetables + 1):
            tasks.append(asyncio.create_task(get_timetable(session, model, i, requests_num, TIMETABLES, TEMP_PLAIN_TEXT, TEMP_SPACED_LESSONS)))  # create tasks for each timetable
        await asyncio.gather(*tasks)
    print('Got all timetables...')
    
    tasks.clear()  # list to store tasks (saving timetables; see inside of the function)
    
    print('Saving timetables to files...')
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

    # saving updated SPACED_LESSONS
    if TEMP_SPACED_LESSONS:
        global SPACED_LESSONS
        SPACED_LESSONS.update(TEMP_SPACED_LESSONS)
        SPACED_LESSONS = dict(sorted(SPACED_LESSONS.items()))  # sort the SPACED_LESSONS
        tasks.append(asyncio.create_task(save_timetable('spaced_lessons', SPACED_LESSONS, JSON_PATH)))  # save the SPACED_LESSONS to the file (used for creating the main menu in the mobile app)
    
    # saving plain text
    if TEMP_PLAIN_TEXT:
        global PLAIN_TEXT
        PLAIN_TEXT.update(TEMP_PLAIN_TEXT)
        PLAIN_TEXT = dict(sorted(PLAIN_TEXT.items()))  # sort the PLAIN_TEXT
        tasks.append(asyncio.create_task(save_timetable('plain_text', PLAIN_TEXT, JSON_PATH)))  # save the TEMP_PLAIN_TEXT to the file (used for creating the main menu in the mobile app)
    
    await asyncio.gather(*tasks)
    print('Done!')


if __name__ == '__main__':
    load_dotenv() 
    
    # tiemetables dictionaries
    TEACHERS_TIMETABLES: teachers_type = dict()
    CLASSROOMS_TIMETABLES: classrooms_type = dict()
    GRADES_TIMETABLES: grades_type = dict()
    TEMP_PLAIN_TEXT: dict[str, str] = dict()  # Variable to store plain text lessons (later exported and used in other program to get PLAIN_TEXT_SOLUTION)
    TEMP_SPACED_LESSONS = dict()
    
    TIMETABLES: tuple[teachers_type, classrooms_type, grades_type] = (TEACHERS_TIMETABLES, CLASSROOMS_TIMETABLES, GRADES_TIMETABLES)  # Tuple to store all timetables dictionaries

    asyncio.run(main())   # run the main
