import asyncio
import json

from bs4 import BeautifulSoup as bs, ResultSet, Tag
from aiohttp import ClientSession

from utils.getting import get_lesson_details
from utils.saving import save_timetables, save_timetable
from utils.constants import JSON_PATH, LESSONS_NUMBER, PLAIN_TEXT_SOLUTION, URL, WEEK_DAYS_NUMBER  


def insert_data_to_teachers(lesson_title: str, lesson_teacher: str, lesson_classroom: str, group: str, num_col: int, num_row: int, grade: str) -> None:
    """Puts lesson data into TEACHERS_TIMETABLES dictionary in aprioriate place

    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        num_col (int): day of a week
        num_row (int): number of the lesson
        grade (str): just a grade

    Raises:
        ValueError: if the lesson is already in the TEACHERS_TIMETABLES dictionary
        and it's not the same as the new one (except the grade)
    """
    grade = f'{grade}{'' if group is None else group}' # add the group to the grade
    if lesson_teacher not in TEACHERS_TIMETABLES:   # if teacher is not in the TEACHERS_TIMETABLES dictionary, add him
        TEACHERS_TIMETABLES[lesson_teacher] = {day: [None for _ in range(LESSONS_NUMBER)] for day in range(WEEK_DAYS_NUMBER)}  # add LESSONS_NUMBER lessons per day
    if not TEACHERS_TIMETABLES[lesson_teacher][num_col][num_row]:  # if the lesson is empty, put it there
        TEACHERS_TIMETABLES[lesson_teacher][num_col][num_row] = ([grade], lesson_title, lesson_classroom)
    elif TEACHERS_TIMETABLES[lesson_teacher][num_col][num_row][1] == lesson_title \
            and TEACHERS_TIMETABLES[lesson_teacher][num_col][num_row][2] == lesson_classroom:  # if the lesson is the same as the new one, just add the grade
        i: int = 0
        while i < len(TEACHERS_TIMETABLES[lesson_teacher][num_col][num_row][0]) and \
                TEACHERS_TIMETABLES[lesson_teacher][num_col][num_row][0][i] < grade:  # find the place where to put the grade
            i += 1
        TEACHERS_TIMETABLES[lesson_teacher][num_col][num_row][0].insert(i, grade)  # insert the grade
    else:
        raise ValueError(f'Error: {TEACHERS_TIMETABLES[lesson_teacher][num_col][num_row]} != {grade} {lesson_title} {lesson_classroom}')  # if the lesson is different, raise an error


def insert_data_to_classrooms(lesson_title: str, lesson_teacher: str, lesson_classroom: str, group: str, num_col: int, num_row: int, grade: str) -> None:
    """Puts lesson data into CLASSROOMS_TIMETABLES dictionary in aprioriate place

    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        num_col (int): day of a week
        num_row (int): number of the lesson
        grade (str): just a grade

    Raises:
        ValueError: if the lesson is already in the CLASSROOMS_TIMETABLES dictionary and it's not the same as the new one (except the grade)
    """
    grade = f'{grade}{'' if group is None else group}' # add the group to the grade
    if lesson_classroom not in CLASSROOMS_TIMETABLES:  # if classroom is not in the CLASSROOMS_TIMETABLES dictionary, add it
        CLASSROOMS_TIMETABLES[lesson_classroom] = {day: [None for _ in range(LESSONS_NUMBER)] for day in range(WEEK_DAYS_NUMBER)}  # add LESSONS_NUMBER lessons per day
    if not CLASSROOMS_TIMETABLES[lesson_classroom][num_col][num_row]:  # if the lesson is empty, put it there
        CLASSROOMS_TIMETABLES[lesson_classroom][num_col][num_row] = (lesson_teacher, [grade], lesson_title)
    elif CLASSROOMS_TIMETABLES[lesson_classroom][num_col][num_row][2] == lesson_title \
            and CLASSROOMS_TIMETABLES[lesson_classroom][num_col][num_row][0] == lesson_teacher:  # if the lesson is the same as the new one, just add the grade
        i: int = 0
        while i < len(CLASSROOMS_TIMETABLES[lesson_classroom][num_col][num_row][1]) and \
                CLASSROOMS_TIMETABLES[lesson_classroom][num_col][num_row][1][i] < grade:  # find the place where to put the grade
            i += 1
        CLASSROOMS_TIMETABLES[lesson_classroom][num_col][num_row][1].insert(i, grade)  # insert the grade
    else:
        raise ValueError(f'Error: {CLASSROOMS_TIMETABLES[lesson_classroom][num_col][num_row]} != {grade} {lesson_teacher} {lesson_title}')  # if the lesson is different, raise an error


def insert_data_to_grades(lesson_title: str, lesson_teacher: str, lesson_classroom: str, group: str, num_col: int, num_row: int, grade: str) -> None:
    """Puts lesson data into GRADES_TIMETABLES dictionary in aprioriate place

    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        num_col (int): day of a week
        num_row (int): number of the lesson
        grade (str): just a grade

    Raises:
        None
    """
    if grade not in GRADES_TIMETABLES:  # if grade is not in the GRADES_TIMETABLES dictionary, add it
        GRADES_TIMETABLES[grade] = {day: [None for _ in range(LESSONS_NUMBER)] for day in range(WEEK_DAYS_NUMBER)}  # add LESSONS_NUMBER lessons per day
    if not GRADES_TIMETABLES[grade][num_col][num_row]:  # if the lesson is empty, put it there
        GRADES_TIMETABLES[grade][num_col][num_row] = [(f'{lesson_title}{'' if group is None else group}', lesson_teacher, lesson_classroom)]
    else:
        GRADES_TIMETABLES[grade][num_col][num_row].append((f'{lesson_title}{group}', lesson_teacher, lesson_classroom))


async def get_timetable(session: ClientSession, i: int) -> None:
    async with session.get(f'{URL}o{i}.html') as response:  # get the timetable
        timetable_html = bs(await response.text(), 'html.parser')  # parse the timetable
        grade = timetable_html.find('span', class_='tytulnapis').text.split(' ')[0]  # get the grade
        print(grade)  # print the grade so we know the progress
        row: Tag
        for num_row, row in enumerate(timetable_html.find('table', class_='tabela').find_all('tr')[1:]):  # iterate over the lesson numbers (rows)
            col: Tag
            for num_col, col in enumerate(row.find_all('td')[2:]):  # iterate over the days (columns)
                col_spans: ResultSet[Tag] = col.find_all('span', recursive=False)  # get the spans from the column (the data is stored in spans, exept the plain text)
                groups = [col.text[x:x+4] for x in [i for i, letter in enumerate(col.text) if letter == '-']] # get the groups from corrupted data (it's stored in plain text)
                if len(col_spans) == 0:  # if there are no spans, it's a plain text
                    if col.text == '\xa0':  # if the text is empty just skip it
                        continue
                    if grade not in PLAIN_TEXT:  # if the grade is not in the PLAIN_TEXT dictionary, add it 
                        # (it isn't used directly in the program, but it's useful for creating PLAIN_TEXT_SOLUTION)
                        PLAIN_TEXT[grade] = dict()
                    if num_col not in PLAIN_TEXT[grade]:  # if the day is not in the PLAIN_TEXT dictionary, add it in number format (same as above)
                        PLAIN_TEXT[grade][num_col] = dict()
                    PLAIN_TEXT[grade][num_col][num_row] = col.text  # add the plain text to the PLAIN_TEXT dictionary 

                    if col.text not in PLAIN_TEXT_SOLUTION:  # if the plain text is not in the PLAIN_TEXT_SOLUTION dictionary, raise an error (if so probably the file is outdated)
                        raise ValueError(f'Error: {grade}/{num_col}/{num_row}: {col.text} not in PLAIN_TEXT_SOLUTION')
                    if PLAIN_TEXT_SOLUTION[col.text] is None:  # if the plain text solution is None, skip it (I considered it an unnecessary data)
                        continue
                    else:  # if the plain text is in the PLAIN_TEXT_SOLUTION dictionary, iterate over the spans and put the data in the dictionaries
                        for span in PLAIN_TEXT_SOLUTION[col.text].split('//'):
                            group = span.split(' ')[0].split('-')[1] if len(span.split(' ')[0].split('-')) == 2 else None
                            insert_data_to_teachers(*(w := (*span.split(' '), group)), num_col, num_row, grade)
                            insert_data_to_classrooms(*w, num_col, num_row, grade)
                            insert_data_to_grades(*w, num_col, num_row, grade)

                elif len(col_spans) == 3:  # if there are 3 spans, put the data in the Dictionaries (the default case)
                    insert_data_to_teachers(*(w := get_lesson_details(col_spans, groups[0] if len(groups) != 0 else None)), num_col, num_row, grade)
                    insert_data_to_classrooms(*w, num_col, num_row, grade)
                    insert_data_to_grades(*w, num_col, num_row, grade)
                elif len(col_spans) == 2:  # if there are 2 spans, iterate over it and put the data in the Dictionaries (group lesson case)
                    for k, span in enumerate(col_spans):
                        insert_data_to_teachers(*(w := get_lesson_details(span.find_all('span'), groups[k] if len(groups) != 0 else None)), num_col, num_row, grade)
                        insert_data_to_classrooms(*w, num_col, num_row, grade)
                        insert_data_to_grades(*w, num_col, num_row, grade)
                elif len(col_spans) == 1:   # if there is only one span, it's a group lesson with one group (half of the class case)
                    insert_data_to_teachers(*(w := get_lesson_details(col_spans[0].find_all('span', recursive=False), groups[0] if len(groups) != 0 else None)), num_col, num_row, grade)
                    insert_data_to_classrooms(*w, num_col, num_row, grade)
                    insert_data_to_grades(*w, num_col, num_row, grade)
                else:  # if there are more than 3 spans, iterate over it, organize spans into groups of 3 and put the data in the Dictionaries (more than two groups case)
                    it = iter(col_spans)
                    for k, span in enumerate(zip(it, it, it)):
                        insert_data_to_teachers(*(w := get_lesson_details(span, groups[k] if len(groups) != 0 else None)), num_col, num_row, grade)
                        insert_data_to_classrooms(*w, num_col, num_row, grade)
                        insert_data_to_grades(*w, num_col, num_row, grade)


async def main() -> None:
    # getting timetables
    tasks: list[asyncio.Task] = list()  # list to store tasks (getting timetables)
    async with ClientSession() as session:
        for i in range(1, 32):
            tasks.append(asyncio.create_task(get_timetable(session, i)))  # create tasks for each timetable
        await asyncio.gather(*tasks)

    tasks.clear()  # list to store tasks (saving timetables; see inside of the function)
    
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
    # tiemetables dictionaries
    TEACHERS_TIMETABLES: dict[str, dict[str, list[tuple[list[str], str, str]]]] = dict()    # Variable to store teachers timetables {teacher: {day: [lesson1, lesson2, ...]}}
    CLASSROOMS_TIMETABLES: dict[str, dict[str, list[tuple[str, list[str], str]]]] = dict()  # Variable to store classrooms timetables {classroom: {day: [lesson1, lesson2, ...]}}
    GRADES_TIMETABLES: dict[str, dict[str, list[list[tuple[str, str, str]]]]] = dict()      # Variable to store grades timetables {grade: {day: [lesson1, lesson2, ...]}}
    PLAIN_TEXT: dict[str, dict[str, dict[str, str]]] = dict()                               # Variable to store plain text lessons (later exported and used in other program to get PLAIN_TEXT_SOLUTION)
    # {grade: {day: {lesson: lesson_text}}}

    asyncio.run(main())   # run the main
