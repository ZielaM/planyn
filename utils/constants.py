import json


JSON_PATH = 'JSON/'
URL = 'https://www.zsk.poznan.pl/plany_lekcji/2023plany/technikum/plany/'
WEEK_DAYS_NUMBER = 5
LESSONS_NUMBER = 11
RPM = 10  # requests per minute
with open(f'{JSON_PATH}lessons.json', 'r', encoding='utf-8') as f:
    LESSONS: dict[str, str] = json.load(f)  # Constant to replace corrupted lesson names {corrupted_lesson: lesson_name}
with open(f'{JSON_PATH}teachers.json', 'r', encoding='utf-8') as f:
    TEACHERS: dict[str, str] = json.load(f)  # Constant to replace corrupted teacher names {corrupted_teacher: teacher_name}
with open(f'{JSON_PATH}plain_text_solution.json', 'r', encoding='utf-8') as f:
    PLAIN_TEXT_SOLUTION: dict[str, str] = json.load(f)  # Constant to replace plain text lessons {pt_lesson: lesson_data}

teacher_type = list[list[tuple[list[str], str, str] | None]]
classroom_type = list[list[tuple[str, list[str], str] | None]]
grade_type = list[list[list[tuple[str, str, str]] | None]]
timetable = teacher_type | classroom_type | grade_type

teachers_type = dict[str, teacher_type]
classrooms_type = dict[str, classroom_type]
grades_type = dict[str, grade_type]
timetables = teachers_type | classrooms_type | grades_type

plain_text_type = dict[str, dict[str, dict[str, str]]]