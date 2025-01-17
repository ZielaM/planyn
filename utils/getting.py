from aiohttp import ClientSession
from bs4 import ResultSet, Tag

from utils.inserting import insert_all
from .constants import PLAIN_TEXT_SOLUTION, TEACHERS, LESSONS, URL
from bs4 import BeautifulSoup as bs, ResultSet, Tag


def get_lesson_details(span: ResultSet[Tag], group: str) -> tuple[str, str, str, str|None]:
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
    if group is None and len(span[0].text.split('-')) == 2: 
        span[0], group = span[0].text.split('-')
    lesson_title: str = w if (w := span[0].text.split('-')[0]) not in LESSONS else LESSONS[w]  # if lesson is corrupted, replace it with correct one
    lesson_teacher: str = w if (w := span[1].text)[0] != '#' else TEACHERS[w]  # if teacher is corrupted, replace it with correct one
    lesson_classroom: str = span[2].text
    return lesson_title, lesson_teacher, lesson_classroom, group


async def get_timetable(session: ClientSession, i: int, TIMETABLES: tuple, PLAIN_TEXT: dict) -> None:
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
                            insert_all(*span.split(' '), group, num_col, num_row, grade, *TIMETABLES)  # insert the data to the dictionaries

                elif len(col_spans) == 3:  # if there are 3 spans, put the data in the Dictionaries (the default case)
                    insert_all(*get_lesson_details(col_spans, groups[0] if len(groups) != 0 else None), num_col, num_row, grade, *TIMETABLES)
                elif len(col_spans) == 2:  # if there are 2 spans, iterate over it and put the data in the Dictionaries (group lesson case)
                    for k, span in enumerate(col_spans):
                        insert_all(*get_lesson_details(span.find_all('span'), groups[k] if len(groups) != 0 else None), num_col, num_row, grade, *TIMETABLES)
                elif len(col_spans) == 1:   # if there is only one span, it's a group lesson with one group (half of the class case)
                    insert_all(*get_lesson_details(col_spans[0].find_all('span', recursive=False), groups[0] if len(groups) != 0 else None), num_col, num_row, grade, *TIMETABLES)
                else:  # if there are more than 3 spans, iterate over it, organize spans into groups of 3 and put the data in the Dictionaries (more than two groups case)
                    it = iter(col_spans)
                    for k, span in enumerate(zip(it, it, it)):
                        insert_all(*get_lesson_details(span, groups[k] if len(groups) != 0 else None), num_col, num_row, grade, *TIMETABLES)

