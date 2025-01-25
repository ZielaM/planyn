import os
import json
from typing_extensions import TypedDict

import google.generativeai as genai

from .constants import LESSONS_NUMBER, WEEK_DAYS_NUMBER


def generate_structure(key: str, timetable: dict) -> None:
    """Generates a structure for a timetable

    Args:
        timetable (dict): dictionary with timetables

    Returns:
        dict: generated structure
    """
    if key not in timetable: # new timetable if there isn't one
        timetable[key] = [[None for _ in range(LESSONS_NUMBER)] for _ in range(WEEK_DAYS_NUMBER)]  # add LESSONS_NUMBER lessons per day


def insert_data_to_teachers(lesson_title: str, lesson_teacher: str, lesson_classroom: str, group: str, num_col: int, num_row: int, grade: str, TEACHER_TIMETABLES: dict) -> None:
    """Puts lesson data into TEACHER_TIMETABLES dictionary in aprioriate place

    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        num_col (int): day of a week
        num_row (int): number of the lesson
        grade (str): just a grade
        TEACHER_TIMETABLES (dict): dictionary with timetables

    Raises:
        ValueError: if the lesson is already in the TEACHER_TIMETABLES dictionary
        and it's not the same as the new one (except the grade)
    """
    grade = f'{grade}{'' if group is None else group}' # add the group to the grade
    generate_structure(lesson_teacher, TEACHER_TIMETABLES) 
    if not TEACHER_TIMETABLES[lesson_teacher][num_col][num_row]:  # if the lesson is empty, put it there
        TEACHER_TIMETABLES[lesson_teacher][num_col][num_row] = ([grade], lesson_title, lesson_classroom)
    elif TEACHER_TIMETABLES[lesson_teacher][num_col][num_row][1] == lesson_title \
            and TEACHER_TIMETABLES[lesson_teacher][num_col][num_row][2] == lesson_classroom:  # add grade to existing lesson
        i: int = 0
        while i < len(TEACHER_TIMETABLES[lesson_teacher][num_col][num_row][0]) and \
                TEACHER_TIMETABLES[lesson_teacher][num_col][num_row][0][i] < grade:
            i += 1
        TEACHER_TIMETABLES[lesson_teacher][num_col][num_row][0].insert(i, grade)  # insert the grade
    else:
        raise ValueError(f'Error: {TEACHER_TIMETABLES[lesson_teacher][num_col][num_row]} != {grade} {lesson_title} {lesson_classroom}')  # if the lessons are different, raise an error


def insert_data_to_classrooms(lesson_title: str, lesson_teacher: str, lesson_classroom: str, group: str, num_col: int, num_row: int, grade: str, CLASSROOM_TIMETABLES: dict) -> None:
    """Puts lesson data into CLASSROOM_TIMETABLES dictionary in aprioriate place

    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        num_col (int): day of a week
        num_row (int): number of the lesson
        grade (str): just a grade
        CLASSROOM_TIMETABLES (dict): dictionary with timetables

    Raises:
        ValueError: if the lesson is already in the CLASSROOM_TIMETABLES dictionary and it's not the same as the new one (except the grade)
    """
    grade = f'{grade}{'' if group is None else group}' # add the group to the grade
    generate_structure(lesson_classroom, CLASSROOM_TIMETABLES)
    if not CLASSROOM_TIMETABLES[lesson_classroom][num_col][num_row]:  # if the lesson is empty, put it there
        CLASSROOM_TIMETABLES[lesson_classroom][num_col][num_row] = (lesson_teacher, [grade], lesson_title)
    elif CLASSROOM_TIMETABLES[lesson_classroom][num_col][num_row][2] == lesson_title \
            and CLASSROOM_TIMETABLES[lesson_classroom][num_col][num_row][0] == lesson_teacher:  # add grade to existing lesson
        i: int = 0
        while i < len(CLASSROOM_TIMETABLES[lesson_classroom][num_col][num_row][1]) and \
                CLASSROOM_TIMETABLES[lesson_classroom][num_col][num_row][1][i] < grade:
            i += 1
        CLASSROOM_TIMETABLES[lesson_classroom][num_col][num_row][1].insert(i, grade)  # insert the grade
    else:
        raise ValueError(f'Error: {CLASSROOM_TIMETABLES[lesson_classroom][num_col][num_row]} != {grade} {lesson_teacher} {lesson_title}')  # if the lesson is different, raise an error


def insert_data_to_grades(lesson_title: str, lesson_teacher: str, lesson_classroom: str, group: str, num_col: int, num_row: int, grade: str, GRADE_TIMETABLES: dict) -> None:
    """Puts lesson data into GRADE_TIMETABLES dictionary in aprioriate place

    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        num_col (int): day of a week
        num_row (int): number of the lesson
        grade (str): just a grade
        GRADE_TIMETABLES (dict): dictionary with timetables

    Raises:
        None
    """
    generate_structure(grade, GRADE_TIMETABLES)
    if not GRADE_TIMETABLES[grade][num_col][num_row]:  # if the lesson is empty, put it there
        GRADE_TIMETABLES[grade][num_col][num_row] = [(f'{lesson_title}{'' if group is None else group}', lesson_teacher, lesson_classroom)]
    else:
        GRADE_TIMETABLES[grade][num_col][num_row].append((f'{lesson_title}{'' if group is None else group}', lesson_teacher, lesson_classroom))


def insert_all(lesson_title: str, lesson_teacher: str, lesson_classroom: str, group: str, num_col: int, num_row: int, grade: str, TEACHER_TIMETABLES: dict, CLASSROOM_TIMETABLES: dict, GRADE_TIMETABLES: dict) -> None:
    """Puts lesson data into all dictionaries in aprioriate place
    
    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        num_col (int): day of a week
        num_row (int): number of the lesson
        grade (str): just a grade
        TEACHER_TIMETABLES (dict): dictionary with timetables for teachers
        CLASSROOM_TIMETABLES (dict): dictionary with timetables for classrooms
        GRADE_TIMETABLES (dict): dictionary with timetables for grades
    
    Raises:
        ValueError: if the lesson is already in the CLASSROOM_TIMETABLES/TEACHER_TIMETABLES dictionary and it's not the same as the new one (except the grade)
    """
    insert_data_to_teachers(lesson_title, lesson_teacher, lesson_classroom, group, num_col, num_row, grade, TEACHER_TIMETABLES)
    insert_data_to_classrooms(lesson_title, lesson_teacher, lesson_classroom, group, num_col, num_row, grade, CLASSROOM_TIMETABLES)
    insert_data_to_grades(lesson_title, lesson_teacher, lesson_classroom, group, num_col, num_row, grade, GRADE_TIMETABLES)


def add_spaces_to_names(LESSON_NAMES: set[str], TEACHER_TIMETABLES: dict, CLASSROOM_TIMETABLES: dict, GRADE_TIMETABLES: dict): 
    
    class LessonDict(TypedDict):
        lesson_name_spaced: str
    
    genai.configure(api_key=os.getenv('GEMINI_API_KEY')) 
    model = genai.GenerativeModel('gemini-2.0-flash-exp', system_instruction='Dodaj spacje do nazw lekcji w języku polskim w podanej liście lekcji, twoja odpowiedź powinna zawierać polskie znaki (nie zmieniaj liter, kolejności liter, nie ucinaj liter). Na przykład: "JęzykniemieckiDSDIPRO" -> "Język niemiecki DSD I PRO", "Zajęciazwychowawcą" -> "Zajęcia z wychowawcą", "BazydanychD_WD" -> "Bazy danych D_WD", "SysytemybazdanychD_DW" -> "Systemy baz danych D_DW", "Taborszynowy" -> "Tabor szynowy".')
    response = model.generate_content(json.dumps(list(LESSON_NAMES)), generation_config=genai.GenerationConfig(response_mime_type='application/json', 
                                                                                       response_schema=list[LessonDict]))
    print(response.text)
    SPACED_LESSON_NAMES: dict[str, str] = {lesson['lesson_name_spaced'].replace(' ', ''): lesson['lesson_name_spaced'] for lesson in json.loads(response.text)}
    print(SPACED_LESSON_NAMES)
    
    for techer, timetable in TEACHER_TIMETABLES.items():
        for day, lessons in enumerate(timetable):
            for lesson_num, lesson in enumerate(lessons):
                if lesson:
                    TEACHER_TIMETABLES[techer][day][lesson_num] = \
                        (TEACHER_TIMETABLES[techer][day][lesson_num][0], SPACED_LESSON_NAMES[lesson[1].split('-')[0]], \
                            TEACHER_TIMETABLES[techer][day][lesson_num][2])
    
    for classroom, timetable in CLASSROOM_TIMETABLES.items():
        for day, lessons in enumerate(timetable):
            for lesson_num, lesson in enumerate(lessons):
                if lesson:
                    CLASSROOM_TIMETABLES[classroom][day][lesson_num] = \
                        (*CLASSROOM_TIMETABLES[classroom][day][lesson_num][:2], SPACED_LESSON_NAMES[lesson[2].split('-')[0]])
    
    for grade, timetable in GRADE_TIMETABLES.items():
        for day, lessons in enumerate(timetable):
            for lesson_group_num, lesson_group in enumerate(lessons):
                if lesson_group:
                    for lesson_num, lesson in enumerate(lesson_group):
                        if lesson:
                            GRADE_TIMETABLES[grade][day][lesson_group_num][lesson_num] = \
                                (f'{SPACED_LESSON_NAMES[lesson[0].split('-')[0]]}{f'-{w[1]}' if len((w := lesson[0].split('-'))) == 2 else ''}', \
                                    *GRADE_TIMETABLES[grade][day][lesson_group_num][lesson_num][1:])

