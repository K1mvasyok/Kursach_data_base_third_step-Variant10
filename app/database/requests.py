from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, selectinload

from app.database.models import EducationalDiscipline, Discipline, Specialization, Faculty
from app.database.models import async_session 

# Запрос для получения списка семестров из базы данных
async def get_semesters():
    async with async_session as session:
        query = select(EducationalDiscipline.semester).distinct()
        result = await session.execute(query)
        semesters = [str(row[0]) for row in result.all()] 
        return semesters
    
# Запрос для получения дисциплин по выбранному семестру
async def get_disciplines_by_semester(semester):
    try:
        async with async_session as session:
            query = (
                select(EducationalDiscipline, Discipline, Specialization)
                .join(Discipline, EducationalDiscipline.discipline_id == Discipline.id)
                .join(Specialization, EducationalDiscipline.specialization_id == Specialization.id)
                .options(selectinload(EducationalDiscipline.specialization))
                .where(EducationalDiscipline.semester == semester)
            )
            result = await session.execute(query)
            disciplines = result.all()
            return disciplines
    except Exception as e:
        print(f"Error in get_disciplines_by_semester: {e}")
        return None

# Запрос для получения учебного плана по выбранной специальности
async def get_educational_plan(specialty_id):
    async with async_session as session:
        query = (
            select(EducationalDiscipline)
            .options(
                selectinload(EducationalDiscipline.discipline),
                selectinload(EducationalDiscipline.specialization)
            )
            .filter(EducationalDiscipline.specialization_id == specialty_id)
        )
        educational_plan = await session.execute(query)
        return educational_plan.scalars().all()

# Запрос для клавиатуры списка факультетов
async def get_faculties():
    async with async_session as session:
        result = await session.execute(select(Faculty))
        return result.scalars().all()

# Запрос для вывода подробной информации о факультете по его id
async def get_faculties_for_id(faculties_id):
    async with async_session as session:
        result = await session.execute(select(Faculty).options(selectinload(Faculty.specializations)).filter(Faculty.id == faculties_id))
        return result.scalar()

# Запрос на добавление нового факультета в базу данных
async def save_faculty_to_db(faculty_data):
    async with async_session as session:
        new_faculty = Faculty(**faculty_data)
        session.add(new_faculty)
        await session.commit()
        return True

# Запрос для удаления факультета из базы данных
async def delete_faculty_from_db(faculty_id):
    async with async_session as session:
        faculty = await session.get(Faculty, faculty_id)
        if faculty:
            await session.delete(faculty)
            await session.commit()
            return True
        else:
            return False
    
# Запросы для изменения факультета в базе данных
async def update_faculty_name(faculty_id, new_name):
    async with async_session as session:
        statement = update(Faculty).where(Faculty.id == faculty_id).values(name=new_name)
        await session.execute(statement)
        await session.commit()

async def update_faculty_dean(faculty_id, new_dean):
    async with async_session as session:
        statement = update(Faculty).where(Faculty.id == faculty_id).values(dean_name=new_dean)
        await session.execute(statement)
        await session.commit()

# Запрос на получение специальности по ее id
async def get_specialization_by_id(specialization_id):
    async with async_session as session:
        result = await session.execute(select(Specialization).where(Specialization.id == specialization_id))
        specialization = result.scalar()
        return specialization