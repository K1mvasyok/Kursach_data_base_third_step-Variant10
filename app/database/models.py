from sqlalchemy import and_
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, ForeignKey, Date
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from config import SQLALCHEMY_URL

engine = create_async_engine(SQLALCHEMY_URL, echo=True)
async_session = AsyncSession(engine)
Base = declarative_base()


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)

class Faculty(Base):
    __tablename__ = 'faculties'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    dean_name = Column(String)

    specializations = relationship('Specialization', back_populates='faculty')

class Specialization(Base):
    __tablename__ = 'specializations'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    faculty_id = Column(Integer, ForeignKey('faculties.id'))

    faculty = relationship('Faculty', back_populates='specializations')
    disciplines = relationship('EducationalDiscipline', back_populates='specialization')
    groups = relationship('Group', back_populates='specialization')

class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    admission_year = Column(Integer)
    group_number = Column(Integer)
    specialization_id = Column(Integer, ForeignKey('specializations.id'))

    specialization = relationship('Specialization', back_populates='groups')
    students = relationship('Student', back_populates='group')

class EducationalDiscipline(Base):
    __tablename__ = 'educational_disciplines'

    id = Column(Integer, primary_key=True)
    semester = Column(Integer)
    name = Column(String)
    specialization_id = Column(Integer, ForeignKey('specializations.id'))
    assessment_type = Column(String)
    hours = Column(Integer)
    discipline_id = Column(Integer, ForeignKey('disciplines.id'))

    discipline = relationship("Discipline", back_populates="educational_discipline")
    specialization = relationship('Specialization', back_populates='disciplines')
    grades = relationship('Grade', back_populates='educational_discipline')

class Discipline(Base):
    __tablename__ = 'disciplines'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    elective_type = Column(String)

    educational_discipline = relationship("EducationalDiscipline", back_populates="discipline")

class Student(Base):
    __tablename__ = 'students'

    student_id = Column(Integer, primary_key=True)
    full_name = Column(String)
    gender = Column(String)
    birth_year = Column(Integer)
    admission_year = Column(Integer)
    group_id = Column(Integer, ForeignKey('groups.id'))

    group = relationship('Group', back_populates='students')
    grades = relationship('Grade', back_populates='student')

class Grade(Base):
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True)
    discipline_id = Column(Integer, ForeignKey('educational_disciplines.id'))
    student_id = Column(Integer, ForeignKey('students.student_id'))
    grade = Column(Integer)
    date = Column(String)
    specialization_id = Column(Integer, ForeignKey('specializations.id'))

    educational_discipline = relationship('EducationalDiscipline', back_populates='grades')
    student = relationship('Student', back_populates='grades')

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)