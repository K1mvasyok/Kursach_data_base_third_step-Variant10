from sqlalchemy import select, and_, func
from sqlalchemy.orm import joinedload
from sqlalchemy import insert

from app.database.models import Group, Student, Specialization, EducationalDiscipline, Grade, Discipline
from app.database.models import async_session 

# Запрос на получение всех имющихся групп в бд
async def get_all_groups():
    async with async_session as session:
        async with session.begin():
            result = await session.execute(select(Group))
            groups_list = result.scalars().all()
            return [{'id': group.id, 'code': group.code, 'group_number': group.group_number} for group in groups_list]

# Запрос на добавление студента в бд
async def save_student_to_db(student_data):
    async with async_session as session:      
        new_student = Student(**student_data)
        session.add(new_student)
        await session.commit()
        await session.refresh(new_student)
        return new_student.student_id
        
# Запрос на вывод информации после добавления его в бд
async def get_group_number_by_id(group_id):
    async with async_session as session:
        async with session.begin():
            result = await session.execute(select(Group.group_number).filter(Group.id == group_id))
            group_number = result.scalar()
            return group_number

# Запрос для клавиатуры факультетов
async def get_specializations():
    async with async_session as session:
        result = await session.execute(select(Specialization))
        specializations = result.scalars().all()
        return specializations
    
# Запрос на добавление группы в бд
async def save_group_to_db(group_data: dict) -> int:
    try:
        async with async_session as session:
            new_group = Group(**group_data)
            session.add(new_group)
            await session.commit()
            await session.refresh(new_group)
            return new_group.id
    except Exception as e:
        print(f"Error saving group to database: {e}")
        return None
    
# Запрос на получение номера группы по ее id в бд (вывод информации о новой группе)
async def get_specialization_name_by_id(specialization_id):
    async with async_session as session:
        query = (
            select(Group, Specialization.name)
            .join(Specialization)
            .where(Group.specialization_id == specialization_id)
        )
        result = await session.execute(query)
        group, specialization_name = result.fetchone()
        return specialization_name
    
    
# Запрос для клавиатуры семестров
async def get_student_semesters(student_id):
    async with async_session as session:
        result = await session.execute(
            select(EducationalDiscipline.semester)
            .join(Grade, Grade.discipline_id == EducationalDiscipline.id)
            .where(Grade.student_id == student_id)
            .distinct()
        )
        semesters = result.scalars().all()
        return semesters
    
    
# Запрос для получения данных о студенте и его оценках за определенный семестр
async def get_student_report(student_id, semester):
    try:
        async with async_session as session:
            result = await session.execute(
                select(
                    EducationalDiscipline.semester.label('Выбранный семестр'),
                    Student.student_id.label('Номер зачётной книжки студента'),
                    Student.full_name.label('ФИО студента'),
                    Discipline.name.label('Дисциплина'),
                    EducationalDiscipline.assessment_type.label('Вид оценки'),
                    Grade.grade.label('Оценка'),
                    EducationalDiscipline.hours.label('Часы'),
                    Grade.date.label('Дата получения оценки'),
                    Specialization.name.label('Специализация'),
                    Group.code.label('Группа')
                )
                .join(
                    Grade, EducationalDiscipline.id == Grade.discipline_id
                )
                .join(
                    Student, Grade.student_id == Student.student_id
                )
                .join(
                    Discipline, EducationalDiscipline.discipline_id == Discipline.id
                )
                .join(
                    Specialization, EducationalDiscipline.specialization_id == Specialization.id
                )
                .join(
                    Group, Specialization.id == Group.specialization_id
                )
                .where(
                    and_(
                        Student.student_id == student_id,
                        EducationalDiscipline.semester == semester
                    )
                )
            )
            student_data = result.fetchall()

            if student_data:
                return student_data
            else:
                return None

    except Exception as e:
        print(f"Error in get_student_report: {e}")
        return None
    