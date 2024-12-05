import json


JSON_PATH = 'JSON/'  # path to the JSON files
URL = 'https://www.zsk.poznan.pl/plany_lekcji/2023plany/technikum/plany/'  # URL to the timetables
WEEK_DAYS_NUMBER = 5
LESSONS_NUMBER = 11
with open(f'{JSON_PATH}lessons.json', 'r', encoding='utf-8') as f:
    LESSONS: dict[str, str] = json.load(f)  # Constant to replace corrupted lesson names {corrupted_lesson: lesson_name}
with open(f'{JSON_PATH}teachers.json', 'r', encoding='utf-8') as f:
    TEACHERS: dict[str, str] = json.load(f)  # Constant to replace corrupted teacher names {corrupted_teacher: teacher_name}
with open(f'{JSON_PATH}plain_text_solution.json', 'r', encoding='utf-8') as f:
    PLAIN_TEXT_SOLUTION: dict[str, str] = json.load(f)  # Constant to replace plain text lessons {pt_lesson: lesson_data}