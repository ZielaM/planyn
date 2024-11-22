from bs4 import BeautifulSoup as bs, ResultSet, Tag
import json
from aiohttp import ClientSession
import asyncio
import aiofiles
import os

async def save_timetable(teacher: str, timetable: dict[str, list[tuple[list[str], str, str]]]) -> None:
    """Saves the timetable to the file

    Args:
        teacher (str): teacher initials
        timetable (dict[str, dict[str, list[list[str]]]): timetable to save
    """
    async with aiofiles.open(f'./JSON/timetables/{teacher}.json', 'w', encoding='utf-8') as f:
        await f.write(json.dumps(timetable, ensure_ascii=False, indent=4)) # save the timetable to the file
    
def get_lesson_details(span: ResultSet[Tag]) -> tuple[str, str, str]:
    """extracts lesson details from spans

    Args:
        span (ResultSet[Tag]): a result of bs.find_all('span', recursive=False) method. 
        It should contain 3 spans with lesson title {lesson_title-group}, teacher {teacher_initials} and classroom {classroom_number}

    Returns:
        tuple[str, str, str]: returns a tuple with lesson title, teacher and classroom in string format
    """
    lesson_title: str = span[0].text.split('-')[0] if span[0].text not in LESSONS else LESSONS[span[0].text] # if lesson is corrupted, replace it with correct one
    lesson_teacher: str = span[1].text if span[1].text[0] != '#' else TEACHERS[span[1].text] # if teacher is corrupted, replace it with correct one
    lesson_classroom: str = span[2].text 
    return lesson_title, lesson_teacher, lesson_classroom

def put_data(lesson_title: str, lesson_teacher: str, lesson_classroom: str, num_col: int, num_row: int, grade: str) -> None:
    """Puts lesson data into PLANY dictionary in aprioriate place

    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        num_col (int): day of a week
        num_row (int): number of the lesson
        grade (str): just a grade

    Raises:
        ValueError: if the lesson is already in the PLANY dictionary and it's not the same as the new one (except the grade)
    """
    if lesson_teacher not in PLANY: # if teacher is not in the PLANY dictionary, add him
        PLANY[lesson_teacher] = {day: [None for _ in range(11)] for day in WEEK} # add 11 lessons per day
    if not PLANY[lesson_teacher][WEEK[num_col]][num_row]: # if the lesson is empty, put it there
        PLANY[lesson_teacher][WEEK[num_col]][num_row] = ([grade], lesson_title, lesson_classroom)
    elif PLANY[lesson_teacher][WEEK[num_col]][num_row][1] == lesson_title \
        and PLANY[lesson_teacher][WEEK[num_col]][num_row][2] == lesson_classroom: # if the lesson is the same as the new one, just add the grade
        # grades_list: list[str] = PLANY[lesson_teacher][WEEK[num_col]][num_row][0]
        i: int = 0
        while i < len(PLANY[lesson_teacher][WEEK[num_col]][num_row][0]) and \
            PLANY[lesson_teacher][WEEK[num_col]][num_row][0][i] < grade: # find the place where to put the grade
            i += 1
        PLANY[lesson_teacher][WEEK[num_col]][num_row][0].insert(i, grade) # insert the grade
    else:
        raise ValueError(f'Error: {PLANY[lesson_teacher][WEEK[num_col]][num_row]} != {grade} {lesson_title} {lesson_classroom}') # if the lesson is different, raise an error
                
async def get_timetable(session: ClientSession, i: int) -> None:
    async with session.get(f'{URL}o{i}.html') as response: # get the timetable
        timetable_html = bs(await response.text(), 'html.parser') # parse the timetable
        grade = timetable_html.find('span', class_ = 'tytulnapis').text.split(' ')[0] # get the grade
        print(grade) # print the grade so we know the progress
        row: Tag
        for num_row, row in enumerate(timetable_html.find('table', class_='tabela').find_all('tr')[1:]): # iterate over the lesson numbers (rows)
            col: Tag
            for num_col, col in enumerate(row.find_all('td')[2:]): # iterate over the days (columns)
                col_spans: ResultSet[Tag] = col.find_all('span', recursive=False) # get the spans from the column (the data is stored in spans, exept the plain text)
                if len(col_spans) == 0: # if there are no spans, it's a plain text
                    if col.text == '\xa0': # if the text is empty just skip it
                        continue 
                    if grade not in PLAIN_TEXT: # if the grade is not in the PLAIN_TEXT dictionary, add it 
                                                # (it isn't used directly in the program, but it's useful for creating PLAIN_TEXT_SOLUTION)
                        PLAIN_TEXT[grade] = dict()
                    if num_col not in PLAIN_TEXT[grade]: # if the day is not in the PLAIN_TEXT dictionary, add it in number format (same as above)
                        PLAIN_TEXT[grade][num_col] = dict()
                    PLAIN_TEXT[grade][num_col][num_row] = col.text # add the plain text to the PLAIN_TEXT dictionary 
                    
                    if col.text not in PLAIN_TEXT_SOLUTION: # if the plain text is not in the PLAIN_TEXT_SOLUTION dictionary, raise an error (if so probably the file is outdated)
                        raise ValueError(f'Error: {grade}/{WEEK[num_col]}/{num_row}: {col.text} not in PLAIN_TEXT_SOLUTION')
                    if PLAIN_TEXT_SOLUTION[col.text] is None: # if the plain text solution is None, skip it (I considered it an unnecessary data)
                        continue
                    else: # if the plain text is in the PLAIN_TEXT_SOLUTION dictionary, iterate over the spans and put the data in the PLANY dictionary
                        for span in PLAIN_TEXT_SOLUTION[col.text].split('/'): 
                            put_data(*span.split(' '), num_col, num_row, grade)
                    
                elif len(col_spans) == 3: # if there are 3 spans, put the data in the PLANY dictionary (the default case)
                    put_data(*get_lesson_details(col_spans), num_col, num_row, grade)
                elif len(col_spans) == 2: # if there are 2 spans, iterate over it and put the data in the PLANY dictionary (group lesson case)
                    for span in col_spans:
                        put_data(*get_lesson_details(span.find_all('span')), num_col, num_row, grade)
                elif len(col_spans) == 1: # if there is only one span, it's a group lesson with one group (half of the class case)
                    put_data(*get_lesson_details(col_spans[0].find_all('span', recursive=False)), num_col, num_row, grade)
                else: # if there are more than 3 spans, iterate over it, organize spans into groups of 3 and put the data in the PLANY dictionary (more than two groups case)
                    it = iter(col_spans)
                    for span in zip(it, it, it):
                        put_data(*get_lesson_details(span), num_col, num_row, grade)
    
async def main() -> None:
    # getting timetables
    tasks: list[asyncio.Task] = list() # list to store tasks
    async with ClientSession() as session:
        for i in range(1, 32):
            tasks.append(asyncio.create_task(get_timetable(session, i))) # create tasks for each timetable
        await asyncio.gather(*tasks)
        
    # saving timetables
    tasks: list[asyncio.Task] = list() # list to store tasks
    if not os.path.exists('./JSON/timetables'): # if the folder doesn't exist, create it
        os.makedirs('./JSON/timetables')
    for teacher in PLANY:
        tasks.append(asyncio.create_task(save_timetable(teacher, PLANY[teacher]))) # create tasks for each timetable
    await asyncio.gather(*tasks)
    
    with open('./JSON/plain_text.json', 'w', encoding='utf-8') as f:
        json.dump(PLAIN_TEXT, f, ensure_ascii=False, indent=4, sort_keys=True) # save the PLAIN_TEXT dictionary to the file (used for creating PLAIN_TEXT_SOLUTION in other program)
                    
if __name__ == '__main__':
    # Constants
    URL = 'https://www.zsk.poznan.pl/plany_lekcji/2023plany/technikum/plany/' # URL to the timetables
    WEEK = ['poniedzialek', 'wtorek', 'środa', 'czwartek', 'piątek'] 
    PLANY: dict[str, dict[str, list[tuple[list[str], str, str]]]] = dict() # Constant to store teachers timetables {teacher: {day: [lesson1, lesson2, ...]}}
    PLAIN_TEXT: dict[str, dict[str, dict[str, str]]] = dict() # Constant to store plain text lessons (later exported and used in other program to get PLAIN_TEXT_SOLUTION) 
                                                            # {grade: {day: {lesson: lesson_text}}}
    with open('./JSON/lessons.json', 'r', encoding='utf-8') as f:
        LESSONS: dict[str, str] = json.load(f) # Constant to replace corrupted lesson names {corrupted_lesson: lesson_name}
    with open('./JSON/teachers.json', 'r', encoding='utf-8') as f:
        TEACHERS: dict[str, str] = json.load(f) # Constant to replace corrupted teacher names {corrupted_teacher: teacher_name}
    with open('./JSON/plain_text_solution.json', 'r', encoding='utf-8') as f:
        PLAIN_TEXT_SOLUTION: dict[str, str] = json.load(f) # Constant to replace plain text lessons {pt_lesson: lesson_data}
        
    asyncio.run(main())  # run the main
    