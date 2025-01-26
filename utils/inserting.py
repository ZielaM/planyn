from .constants import LESSONS_NUMBER, WEEK_DAYS_NUMBER, timetable, teachers_type, classrooms_type, grades_type


def generate_structure(key: str, timetable: timetable) -> None:
    """Generates a structure for a timetable

    Args:
        timetable (dict): dictionary with timetables

    Returns:
        dict: generated structure
    """
    if key not in timetable: # new timetable if there isn't one
        timetable[key] = [[None for _ in range(LESSONS_NUMBER)] for _ in range(WEEK_DAYS_NUMBER)]  # add LESSONS_NUMBER lessons per day


def insert_data_to_teachers(lesson_title: str, lesson_teacher: str, lesson_classroom: str, group: str, num_col: int, num_row: int, grade: str, TEACHER_TIMETABLES: teachers_type) -> None:
    """Puts lesson data into TEACHER_TIMETABLES dictionary in aprioriate place

    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        group (str): group of the grade
        num_col (int): day of a week
        num_row (int): number of the lesson
        grade (str): just a grade
        TEACHER_TIMETABLES (teachers_type): dictionary with timetables

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


def insert_data_to_classrooms(lesson_title: str, lesson_teacher: str, lesson_classroom: str, group: str, num_col: int, num_row: int, grade: str, CLASSROOM_TIMETABLES: classrooms_type) -> None:
    """Puts lesson data into CLASSROOM_TIMETABLES dictionary in aprioriate place

    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        group (str): group of the grade
        num_col (int): day of a week
        num_row (int): number of the lesson
        grade (str): just a grade
        CLASSROOM_TIMETABLES (classrooms_type): dictionary with timetables

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


def insert_data_to_grades(lesson_title: str, lesson_teacher: str, lesson_classroom: str, group: str, num_col: int, num_row: int, grade: str, GRADE_TIMETABLES: grades_type) -> None:
    """Puts lesson data into GRADE_TIMETABLES dictionary in aprioriate place

    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        group (str): group of the grade
        num_col (int): day of a week
        num_row (int): number of the lesson
        grade (str): just a grade
        GRADE_TIMETABLES (grades_type): dictionary with timetables
        
    """
    generate_structure(grade, GRADE_TIMETABLES)
    if not GRADE_TIMETABLES[grade][num_col][num_row]:  # if the lesson is empty, put it there
        GRADE_TIMETABLES[grade][num_col][num_row] = [(f'{lesson_title}{'' if group is None else group}', lesson_teacher, lesson_classroom)]
    else:
        GRADE_TIMETABLES[grade][num_col][num_row].append((f'{lesson_title}{'' if group is None else group}', lesson_teacher, lesson_classroom))


def insert_all(lesson_title: str, lesson_teacher: str, lesson_classroom: str, group: str, num_col: int, num_row: int, grade: str, TEACHER_TIMETABLES: teachers_type, CLASSROOM_TIMETABLES: classrooms_type, GRADE_TIMETABLES: grades_type) -> None:
    """Puts lesson data into all dictionaries in aprioriate place
    
    Args:
        lesson_title (str): name of the lesson
        lesson_teacher (str): initials of the teacher
        lesson_classroom (str): number of the classroom
        group (str): group of the grade
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


