import os
import json
import asyncio
from typing_extensions import TypedDict

import google.generativeai as genai

from .constants import RPM, teachers_type, classrooms_type, grades_type


class LessonDict(TypedDict):
    lesson_name_spaced: str


async def add_spaces_to_names_part(model: genai.GenerativeModel, lesson_names: list[str]) -> str: 
    print(f'\t\t->a prompt is being sent: {asyncio.current_task().get_name()}')
    result = await model.generate_content_async(json.dumps(list(lesson_names)), 
                                              generation_config=genai.GenerationConfig(response_mime_type='application/json', 
                                              response_schema=list[LessonDict]))
    print(f'\t\t->a prompt has been resolved: {asyncio.current_task().get_name()}')
    return result


async def add_spaces_to_names(LESSON_NAMES: set[str], TEACHER_TIMETABLES: teachers_type, CLASSROOM_TIMETABLES: classrooms_type, GRADE_TIMETABLES: grades_type) -> None: 
    
    print(f'\t->Sending 15 prompts to gemini...')
    genai.configure(api_key=os.getenv('GEMINI_API_KEY')) 
    model = genai.GenerativeModel('gemini-2.0-flash-exp', system_instruction='Dodaj spacje do nazw lekcji w języku polskim w podanej liście lekcji, twoja odpowiedź powinna zawierać polskie znaki (nie zmieniaj liter, kolejności liter, nie ucinaj liter). Na przykład: "JęzykniemieckiDSDIPRO" -> "Język niemiecki DSD I PRO", "Zajęciazwychowawcą" -> "Zajęcia z wychowawcą", "BazydanychD_DW" -> "Bazy danych D_DW", "SysytemybazdanychD_DW" -> "Systemy baz danych D_DW", "Taborszynowy" -> "Tabor szynowy".')
    # response = model.generate_content(json.dumps(list(LESSON_NAMES)), generation_config=genai.GenerationConfig(response_mime_type='application/json', 
    #                                                                                    response_schema=list[LessonDict]))
    tasks: list[asyncio.Task] = []
    lessons_per_prompt = int(len(LESSON_NAMES)/RPM)
    lesson_list = list(LESSON_NAMES)
    for i in range(RPM - 1):
        tasks.append(asyncio.create_task(add_spaces_to_names_part(model, lesson_list[i*lessons_per_prompt : (i+1)*lessons_per_prompt])))
    tasks.append(asyncio.create_task(add_spaces_to_names_part(model, lesson_list[(i+1)*lessons_per_prompt : ])))
    
    print('\t->parsing gemini response into json...')
    results = [r.text for r in await asyncio.gather(*tasks)]
    SPACED_LESSON_NAMES: dict[str, str] = dict()
    for res in results:
        SPACED_LESSON_NAMES.update({lesson['lesson_name_spaced'].replace(' ', ''): lesson['lesson_name_spaced'] for lesson in json.loads(res)})
    
    # SPACED_LESSON_NAMES: dict[str, str] = {lesson['lesson_name_spaced'].replace(' ', ''): lesson['lesson_name_spaced'] for lesson in json.loads(response.text)}
    
    print('\t->changing lesson names...')
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