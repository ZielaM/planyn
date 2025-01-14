from bs4 import ResultSet, Tag
from .constants import TEACHERS, LESSONS


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


