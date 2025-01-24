import requests

from aiohttp import ClientSession
from bs4 import ResultSet, Tag

from utils.inserting import insert_all
from .constants import PLAIN_TEXT_SOLUTION, TEACHERS, LESSONS, URL
from bs4 import BeautifulSoup as bs, ResultSet, Tag


def get_number_of_timetables() -> int:
    """Returns the number of timetables

    Returns:
        int: number of timetables
    """
    response = requests.get('https://www.zsk.poznan.pl/plany_lekcji/2023plany/technikum/lista.html')  # get the page with timetables list
    soup = bs(response.text, 'html.parser') 
    return len(soup.find('div', { "id" : "oddzialy" }).find_all('a')) 


def get_lesson_details(span: ResultSet[Tag], group: str, LESSON_NAMES: set[str]) -> tuple[str, str, str, str|None]:
    """extracts lesson details from spans

    Args:
        span (ResultSet[Tag]): a result of bs.find_all('span', recursive=False) method. 
        It should contain 3 spans with lesson title {lesson_title-group},
        teacher {teacher_initials} and classroom {classroom_number}
        group (str): group number

    Returns:
        tuple[str, str, str, str|None]: returns a tuple with lesson title,
        teacher, classroom and group number in string format
    """
    if group is None and len(span[0].text.split('-')) == 2: # if group is None and there is a group in the lesson title, extract it
        span[0], group = span[0].text.split('-')
    lesson_title: str = w if (w := span[0].text.split('-')[0]) not in LESSONS else LESSONS[w]  # if lesson is corrupted, replace it with correct one
    lesson_teacher: str = w if (w := span[1].text)[0] != '#' else TEACHERS[w]  # if teacher is corrupted, replace it with correct one
    lesson_classroom: str = span[2].text
    LESSON_NAMES.add(lesson_title)
    return lesson_title, lesson_teacher, lesson_classroom, group


async def get_timetable(session: ClientSession, i: int, TIMETABLES: tuple, PLAIN_TEXT: dict, LESSON_NAMES: set[str]) -> None:
    async with session.get(f'{URL}o{i}.html') as response: 
        timetable_html = bs(await response.text(), 'html.parser') 
        grade = timetable_html.find('span', class_='tytulnapis').text.split(' ')[0]  # get the grade
        print(grade)  # print the grade so we know the progress
        row: Tag
        for num_row, row in enumerate(timetable_html.find('table', class_='tabela').find_all('tr')[1:]):  # iterate over the lesson numbers (rows)
            col: Tag
            for num_col, col in enumerate(row.find_all('td')[2:]):  # iterate over the days (columns)
                col_spans: ResultSet[Tag] = col.find_all('span', recursive=False)  # get the data from the table cell
                groups = [col.text[x:x+4] for x in [i for i, letter in enumerate(col.text) if letter == '-']] # get the groups from data
                if len(col_spans) == 0:  # plain text case
                    if col.text == '\xa0':  # skip if empty
                        continue
                    if grade not in PLAIN_TEXT:
                        PLAIN_TEXT[grade] = dict()
                    if num_col not in PLAIN_TEXT[grade]:
                        PLAIN_TEXT[grade][num_col] = dict()
                    PLAIN_TEXT[grade][num_col][num_row] = col.text # add the plain text to PLAIN_TEXT 

                    if col.text not in PLAIN_TEXT_SOLUTION:  # print an error and continue in case of missing substitution
                        print(f'Error: {grade}/{num_col}/{num_row}: {col.text} not in PLAIN_TEXT_SOLUTION')
                        continue
                    if PLAIN_TEXT_SOLUTION[col.text] is None:  # unnecessary data
                        continue
                    else: 
                        for span in PLAIN_TEXT_SOLUTION[col.text].split('//'): # iterate over the lessons
                            group = span.split(' ')[0].split('-')[1] if len(span.split(' ')[0].split('-')) == 2 else None # get the group from the lesson title
                            LESSON_NAMES.add((w := span.split(' '))[0].split('-')[0]) 
                            insert_all(*w, group, num_col, num_row, grade, *TIMETABLES) 

                elif len(col_spans) == 3:  # 1 lesson in the cell case
                    insert_all(*get_lesson_details(col_spans, groups[0] if len(groups) != 0 else None, LESSON_NAMES), num_col, num_row, grade, *TIMETABLES)
                elif len(col_spans) == 2:  # group lesson case
                    for k, span in enumerate(col_spans):
                        insert_all(*get_lesson_details(span.find_all('span'), groups[k] if len(groups) != 0 else None, LESSON_NAMES), num_col, num_row, grade, *TIMETABLES)
                elif len(col_spans) == 1:   # group lesson case (half of the class)
                    insert_all(*get_lesson_details(col_spans[0].find_all('span', recursive=False), groups[0] if len(groups) != 0 else None, LESSON_NAMES), num_col, num_row, grade, *TIMETABLES)
                else:  # more than two groups case
                    it = iter(col_spans)
                    for k, span in enumerate(zip(it, it, it)):
                        insert_all(*get_lesson_details(span, groups[k] if len(groups) != 0 else None, LESSON_NAMES), num_col, num_row, grade, *TIMETABLES)

