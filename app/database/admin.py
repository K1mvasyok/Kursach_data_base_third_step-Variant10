import pandas as pd
import io
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.fsm.state import State, StatesGroup

from app.database.requests_a import get_all_groups, save_student_to_db, get_group_number_by_id, get_group_number_by_id, save_group_to_db, get_specialization_name_by_id, get_student_semesters, get_student_report
import app.keyboards as kb
from config import ADMIN_TELEGRAM_ID

router_a = Router()

class AddNewStudent(StatesGroup):
    full_name = State()
    gender = State()
    birth_year = State()
    admission_year = State()
    group_id = State()

class AddNewGroup(StatesGroup):
    group_code = State()
    group_admission_year = State()
    group_group_number = State()
    group_specialization_id = State()

class ShowStudent(StatesGroup):
    student_id = State()
    semester = State()

@router_a.message(Command("commands"))
async def Commads(message: Message):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f'Список всех доступных команд\n\n '
                             f'/new_card  - Заполнить новую личную карточку студента\n\n'
                             f'/new_group - Добавить новую группу\n\n'
                             f'/card - Отчёт карточка студента, список предметов и курсовых работ по определенному семестру, с указанием оценок\n\n')                       
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")
        
# Обработка команды /new_card
@router_a.message(Command("new_card"))
async def New_card(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f"Давайте добавим новый карточку студента.\n\nВведите его полное имя:")
        await state.set_state(AddNewStudent.full_name) 
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@router_a.message(AddNewStudent.full_name)
async def Process_new_card_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Выберите пол:", reply_markup=await kb.add_new_student_pol())        
    
@router_a.callback_query(F.data.startswith("new_student_gender"))
async def Process_new_card_gender(query: types.CallbackQuery, state: FSMContext):
    gender = query.data.split(":")[1]
    await state.update_data(gender=gender)
    await query.message.answer(f"Укажите год рождения студента:")
    await state.set_state(AddNewStudent.birth_year) 

@router_a.message(AddNewStudent.birth_year)
async def Process_new_card_birth_year(message: Message, state: FSMContext):
    try:
        birth_year = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный год рождения числом.")
        return
    await state.update_data(birth_year=birth_year)
    await message.answer(f"Укажите год поступления студента:")
    await state.set_state(AddNewStudent.admission_year) 

@router_a.message(AddNewStudent.admission_year)
async def Process_new_card_admission_year(message: Message, state: FSMContext):
    try:
        admission_year = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный год рождения числом.")
        return
    await state.update_data(admission_year=admission_year)
    groups_list = await get_all_groups()
    await message.answer(f"Выберите уже существующую группу студента:", reply_markup=await kb.groups_for_add_student_keyboard(groups_list))
    
@router_a.callback_query(F.data.startswith("new_student_group"))
async def Process_new_card_group(query: types.CallbackQuery, state: FSMContext):
    group_id = int(query.data.split(":")[1])
    await state.update_data(group_id=group_id)
    data = await state.get_data()

    if 'full_name' not in data or 'gender' not in data or 'birth_year' not in data or 'admission_year' not in data:
        await query.message.answer("Ошибка: не найдены необходимые данные в состоянии.")
        await state.clear()
        return

    full_name = data['full_name']
    gender = data['gender']
    birth_year = data['birth_year']
    admission_year = data['admission_year']

    student_data = {
        'full_name': full_name,
        'gender': gender,
        'birth_year': birth_year,
        'admission_year': admission_year,
        'group_id': group_id
    }

    student_id = await save_student_to_db(student_data)
    if student_id is None:
        await query.message.answer("Ошибка: не удалось добавить студента в базу данных.")
        await state.clear()
        return
    await show_new_student(query.message, student_data)
    await state.clear()

async def show_new_student(message: types.Message, data: dict):
    full_name = data.get('full_name', '')
    gender = data.get('gender', '')
    birth_year = data.get('birth_year', '')
    admission_year = data.get('admission_year', '')
    group_id = data.get('group_id', '')
    
    group_number = await get_group_number_by_id(group_id)
    if group_number is None:
        await message.answer("Ошибка: не удалось получить данные о группе из базы данных.")
        return

    text = (f'Карточка студента успешно добавлена!\n\n'
            f'<i>Имя:</i> <b>{full_name}</b>\n'
            f'<i>Пол:</i> <b>{gender}</b>\n'
            f'<i>Год рождения:</i> <b>{birth_year}</b>\n'
            f'<i>Год поступления:</i> <b>{admission_year}</b>\n'
            f'<i>Группа:</i> <b>{group_number}</b>')

    await message.answer(text)

# Обработка команды /new_group
@router_a.message(Command("new_group"))
async def New_group(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer("Давайте добавим новую группу. Введите аббревиатуру:")
        await state.set_state(AddNewGroup.group_code)    
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@router_a.message(AddNewGroup.group_code)
async def Process_new_group_code(message: Message, state: FSMContext):
    await state.update_data(group_code=message.text)
    await message.answer("Укажите год создания группы: ")
    await state.set_state(AddNewGroup.group_admission_year)  
    
@router_a.message(AddNewGroup.group_admission_year)
async def Process_new_group_admission_year(message: Message, state: FSMContext):
    try:
        group_admission_year = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный год рождения числом.")
        return  
    await state.update_data(group_admission_year=group_admission_year)
    await message.answer("Укажите полное название группы: ")
    await state.set_state(AddNewGroup.group_group_number)

@router_a.message(AddNewGroup.group_group_number)
async def Process_new_group_group_number(message: Message, state: FSMContext):
    await state.update_data(group_group_number=message.text)
    await message.answer("Выберете специализацию из списка", reply_markup=await kb.add_new_group_spec())    

@router_a.callback_query(F.data.startswith("select_specialization"))
async def Process_new_card_group(query: types.CallbackQuery, state: FSMContext):
    group_specialization_id = int(query.data.split(":")[1])
    await state.update_data(group_specialization_id=group_specialization_id)
    data = await state.get_data()

    if 'group_code' not in data or 'group_admission_year' not in data or 'group_group_number' not in data or 'group_specialization_id' not in data:
        await query.message.answer("Ошибка: не найдены необходимые данные в состоянии.")
        await state.clear()
        return

    group_code = data['group_code']
    admission_year = data['group_admission_year']
    group_number = data['group_group_number']
    specialization_id = data['group_specialization_id']

    group_data = {
        'code': group_code,
        'admission_year': admission_year,
        'group_number': group_number,
        'specialization_id': specialization_id
    }

    group_id = await save_group_to_db(group_data)
    if group_id is None:
        await query.message.answer("Ошибка: не удалось добавить группу в базу данных.")
        await state.clear()
        return

    await show_new_group(query.message, group_data)
    await state.clear()

async def show_new_group(message: types.Message, data: dict):
    group_code = data.get('code', '')
    admission_year = data.get('admission_year', '')
    group_number = data.get('group_number', '')
    specialization_id = data.get('specialization_id', '')

    specialization_name = await get_specialization_name_by_id(specialization_id)
    if specialization_name is None:
        await message.answer("Ошибка: не удалось получить данные о специализации из базы данных.")
        return

    text = (f'Новая группа успешно добавлена!\n\n'
            f'<i>Код группы:</i> <b>{group_code}</b>\n'
            f'<i>Год поступления:</i> <b>{admission_year}</b>\n'
            f'<i>Номер группы:</i> <b>{group_number}</b>\n'
            f'<i>Специалиальность:</i> <b>{specialization_name}</b>')

    await message.answer(text)
        
# Обработка команды /card
@router_a.message(Command("card"))
async def Check_card(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer("Введите номер зачетной книжки студента:") 
        await state.set_state(ShowStudent.student_id)
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")
        
@router_a.message(ShowStudent.student_id)
async def Process_сheck_card_student_id(message: Message, state: FSMContext):
    try:
        student_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите номер зачетной книжки числом.")
        return  
    await state.update_data(student_id=student_id)
    
    student_semesters = await get_student_semesters(student_id)
    if not student_semesters:
        await message.answer("У студента нет данных о семестрах.")
        await state.clear()
        return

    await message.answer("Выберете семестр, по которому хотите получить отчёт студента:", reply_markup=await kb.show_semesters_for_student_keyboard(student_semesters))
    
@router_a.callback_query(F.data.startswith("action.show_report:"))
async def Process_сheck_card_semester(query: types.CallbackQuery, state: FSMContext):
    try:
        semester = int(query.data.split(":")[1])
        data = await state.get_data()
        student_id = data.get("student_id")

        # Запрашиваем данные о студенте и его оценках за семестр
        student_data = await get_student_report(student_id, semester)

        if student_data:
            
            # Создаем DataFrame из данных
            df = pd.DataFrame([
                {
                    "Дисциплина": discipline[3], 
                    "Вид оценки": discipline[4],
                    "Оценка": discipline[5],
                    "Часы": discipline[6],
                    "Дата": discipline[7],
                } for discipline in student_data
            ], columns=["Дисциплина", "Вид оценки", "Оценка", "Часы", "Дата"])

            # Добавляем информацию о студенте, специализации и группе
            student_info_df = pd.DataFrame([
                {
                    "Номер зачетной книжки студента": student_data[0][1],
                    "ФИО студента": student_data[0][2],
                    "Семестр": semester,
                    "Специализация": student_data[0][8],  
                    "Группа": student_data[0][9] 
                }
            ])
            df = pd.concat([student_info_df, df], ignore_index=True)

            # Создаем Excel-файл
            excel_content = io.BytesIO()
            with pd.ExcelWriter(excel_content, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Sheet1", index=False)
                worksheet = writer.sheets["Sheet1"]
                # Расширяем столбцы по ширине данных
                for i, col in enumerate(df.columns):
                    max_len = df[col].astype(str).apply(len).max()
                    worksheet.set_column(i, i, max_len + 2)

            # Отправляем Excel-файл
            input_file = BufferedInputFile(excel_content.getvalue(), filename=f"report_student_{student_id}_semester_{semester}.xlsx")
            await query.message.answer_document(input_file, caption=f"Отчет по студенту {student_id} за семестр {semester}")
            await state.clear()
        else:
            await query.message.answer(f"Данные о студенте {student_id} за семестр {semester} не найдены.")
            await state.clear()
    except ValueError:
        await query.message.answer("Произошла ошибка при обработке запроса.")
        await state.clear()

