import requests
import asyncio

from aiohttp import ClientSession
from bs4 import ResultSet, Tag
from google.generativeai import GenerativeModel

from .inserting import insert_all, insert_data_to_grades
from .correcting import correct_plain_text
from .constants import TEACHERS, LESSONS, URL, timetables_tuple
from bs4 import BeautifulSoup as bs, ResultSet, Tag


def get_number_of_timetables() -> int:
    try: 
        response = requests.get('https://www.zsk.poznan.pl/plany_lekcji/2023plany/technikum/lista.html')  # get the page with timetables list
        response.raise_for_status()
        soup = bs(response.text, 'html.parser') 
        return len(soup.find('div', { "id" : "oddzialy" }).find_all('a')) 
    except requests.exceptions.HTTPError:
        print('Page could not be found')
        print('Number of timetables could not be fetched. Using the default value instead.')
        return 32
    except AttributeError:
        print('div#oddzialy could not be found')
        print('Number of timetables could not be fetched. Using the default value instead.')
        return 32


def get_lesson_details(span: ResultSet[Tag], group: str) -> tuple[str, str, str, str|None]:
    """extracts lesson details from spans

    Args:
        span (ResultSet[Tag]): a result of bs.find_all('span', recursive=False) method. 
        It should contain 3 spans with lesson title {lesson_title-group},
        teacher {teacher_initials} and classroom {classroom_number}
        group (str): group number
        LESSON_NAMES (set[str]): set with lesson names

    Returns:
        tuple[str, str, str, str|None]: returns a tuple with 
        lesson title, teacher, classroom and group in string format
    """
    if group is None and len(span[0].text.split('-')) == 2: # if group is None and there is a group in the lesson title, extract it
        span[0], group = span[0].text.split('-')
    lesson_title: str = w if (w := span[0].text.split('-')[0]) not in LESSONS else LESSONS[w]  # if lesson is corrupted, replace it with correct one
    lesson_teacher: str = w if (w := span[1].text)[0] != '#' else TEACHERS[w]  # if teacher is corrupted, replace it with correct one
    lesson_classroom: str = span[2].text
    return lesson_title, lesson_teacher, lesson_classroom, group


async def get_timetable(session: ClientSession, model: GenerativeModel, i: int, requests_num: dict[str, int], TIMETABLES: timetables_tuple, TEMP_PLAIN_TEXT: dict[str, str], TEMP_SPACED_LESSONS: dict[str, str]) -> None:
    async with session.get(f'{URL}o{i}.html') as response: 
        print(f'\t->getting timetable {asyncio.current_task().get_name()}')
        timetable_html = bs(await response.text(), 'html.parser') 
        grade = timetable_html.find('span', class_='tytulnapis').text.split(' ')[0]  # get the grade
        print(f'\t->got timetable {asyncio.current_task().get_name()} : {grade}')
        row: Tag
        for num_row, row in enumerate(timetable_html.find('table', class_='tabela').find_all('tr')[1:]):  # iterate over the lesson numbers (rows)
            col: Tag
            for num_col, col in enumerate(row.find_all('td')[2:]):  # iterate over the days (columns)
                col_spans: ResultSet[Tag] = col.find_all('span', recursive=False)  # get the data from the table cell
                groups = [col.text[x:x+4] for x in [i for i, letter in enumerate(col.text) if letter == '-']] # get the groups from data
                if len(col_spans) == 0:  # plain text case
                    solution: str | None
                    if col.text == '\xa0':  # skip if empty
                        continue

                    solution = correct_plain_text(col.text, TEMP_PLAIN_TEXT)  # correct the lesson title
                    
                    if solution is None:  # comments (adding only to grade timetables)
                        insert_data_to_grades(col.text, '', '', '',  num_col, num_row, grade, TIMETABLES[2])
                        
                    else: 
                        for span in solution.split('//'): # iterate over the lessons
                            (w[0], group) = w[0].split('-') if len((w := span.split(' '))[0].split('-')) == 2 else (w[0], None) # get the group from the lesson title
                            group = f'-{group}' if group is not None else None
                            insert_all(model, *w, group, num_col, num_row, grade, requests_num, *TIMETABLES, TEMP_SPACED_LESSONS) 

                elif len(col_spans) == 3:  # 1 lesson in the cell case
                    insert_all(model, *get_lesson_details(col_spans, groups[0] if len(groups) != 0 else None), num_col, num_row, grade, requests_num, *TIMETABLES, TEMP_SPACED_LESSONS)
                elif len(col_spans) == 2:  # group lesson case
                    for k, span in enumerate(col_spans):
                        insert_all(model, *get_lesson_details(span.find_all('span'), groups[k] if len(groups) != 0 else None), num_col, num_row, grade, requests_num, *TIMETABLES, TEMP_SPACED_LESSONS)
                elif len(col_spans) == 1:   # group lesson case (half of the class)
                    insert_all(model, *get_lesson_details(col_spans[0].find_all('span', recursive=False), groups[0] if len(groups) != 0 else None), num_col, num_row, grade, requests_num, *TIMETABLES, TEMP_SPACED_LESSONS)
                else:  # more than two groups case
                    it = iter(col_spans)
                    for k, span in enumerate(zip(it, it, it)):
                        insert_all(model, *get_lesson_details(span, groups[k] if len(groups) != 0 else None), num_col, num_row, grade, requests_num, *TIMETABLES, TEMP_SPACED_LESSONS)

