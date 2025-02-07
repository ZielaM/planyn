from google.generativeai import GenerativeModel

from .constants import PLAIN_TEXT, SPACED_LESSONS, RPM

def add_spaces(model: GenerativeModel, requests_num: int, lesson_title: str, TEMP_SPACED_LESSONS: dict[str, str]) -> None:
    """Adds spaces to the lesson title
    
    Args:
        lesson_title (str): name of the lesson
        TEMP_SPACED_LESSONS (dict): dictionary with lessons that have spaces
    """
    if lesson_title in SPACED_LESSONS:
        lesson_title = SPACED_LESSONS[lesson_title]
    elif lesson_title in TEMP_SPACED_LESSONS:
        lesson_title = TEMP_SPACED_LESSONS[lesson_title]
    else:
        temp_lesson_title = ''
        if requests_num < RPM:
            print(f'\t\tAdding spaces using Gemini AI to {lesson_title}...')
            temp_lesson_title = model.generate_content(lesson_title).text.strip()
        if lesson_title == temp_lesson_title.replace(' ', ''): 
            TEMP_SPACED_LESSONS[lesson_title] = temp_lesson_title
            lesson_title = temp_lesson_title 
        else:
            print(f'\t\tError: lesson title and spaced lesson title are different (Gemini failed): {temp_lesson_title}')
            while True: 
                temp_lesson_title = input(f'\t\tManually add spaces to {lesson_title}: ') 
                if lesson_title == temp_lesson_title.replace(' ', ''): 
                    TEMP_SPACED_LESSONS[lesson_title] = temp_lesson_title
                    lesson_title = temp_lesson_title 
                    break
                else:
                    print('\t\tError: lesson title and spaced lesson title are different')
    return lesson_title


def correct_plain_text(lesson: str, TEMP_PLAIN_TEXT: dict[str, str]) -> str | None:
    """Corrects the lesson title
    
    Args:
        lesson_title (str): name of the lesson
        TEMP_PLAIN_TEXT (dict): dictionary with lessons that need to be corrected
    """
    solution: str | None
    if lesson in PLAIN_TEXT: 
        solution = PLAIN_TEXT[lesson]
    elif lesson in TEMP_PLAIN_TEXT:
        solution = TEMP_PLAIN_TEXT[lesson]
    else:
        while True: 
            temp_solution = input(f'\t\tWrite correct lesson (example: lesson_title teacher_initials classroom; use // to add grouped lesson; leave empty if unnecessary) {lesson}: ')
            if temp_solution == '':
                TEMP_PLAIN_TEXT[lesson] = None
                solution = None
                break 
            elif (len(temp_solution.split('//')), len(temp_solution.split(' '))) in ((1, 3), (2, 6)): 
                TEMP_PLAIN_TEXT[lesson] = temp_solution
                solution = temp_solution 
                break
            else:
                print('\t\tError: could not parse the input')
    return solution