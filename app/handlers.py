import pandas as pd
import io
from datetime import datetime 

from aiogram import F, Router
from aiogram.types import Message, BufferedInputFile
from aiogram import types
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.keyboards as kb

from app.database.requests import get_disciplines_by_semester, get_educational_plan, get_faculties_for_id, delete_faculty_from_db, save_faculty_to_db, update_faculty_name, update_faculty_dean, get_specialization_by_id 

router_u = Router()

class AddNewFaculty(StatesGroup):
    faculty_name = State()
    faculty_dean_name = State()

class EditFaculty(StatesGroup):
    name = State()
    dean = State()
    faculty_id = State()

@router_u.message(CommandStart())
async def Cmd_start(message: types.Message):
    await message.answer(f'Привет 👋🏼,\nЯ - чат-бот дирекции\n\n'
                             f'Я могу показать: \n\n'
                             f'• Список дисциплин по определеному семестру \n\n'  
                             f'• Получение документа учебный план специальности (учебный план)\n\n'
                             f'• Введение списка институтов\n\n'                            
                             # Добавление/Изменение/Удаление
                             f'• Введение списка специальностей')
    await message.answer(f'🔮 Главное меню', reply_markup=await kb.menu())
        
# Обработка кнопки Дисциплины
@router_u.message(F.text == '📖 Дисциплины')
async def Discipline(message: Message):
    await message.answer(f'Выберите семестр, чтобы увидеть дисциплины:', reply_markup=await kb.semesters_for_practices())

@router_u.callback_query(F.data.startswith("practices_semester:"))
async def show_disciplines_by_semester(query: types.CallbackQuery):
    semester = int(query.data.split(":")[1])
    disciplines = await get_disciplines_by_semester(semester) 
    discipline_info = [f'{discipline[0].name} для {discipline[0].specialization.code}' for discipline in disciplines]
    await query.message.answer(f'Семестр: {semester}\n\nДисциплины:\n{", ".join(discipline_info)}', reply_markup=await kb.return_to_menu())

# Обработка кнопки Учебный план   
@router_u.message(F.text == '📅 Учебный план')
async def Educational_plan(message: Message):
    await message.answer(f'Выберите специальность, чтобы получить учебный план:', reply_markup=await kb.specialties())

@router_u.callback_query(F.data.startswith("specialty_for_education:"))
async def Educational_plan_handler(query: types.CallbackQuery):
    specialty_id = int(query.data.split(":")[1])
    await educational_plan_for_specialty(query.message, specialty_id)

async def educational_plan_for_specialty(message, specialty_id):
    try:
        educational_plan = await get_educational_plan(specialty_id)
        if educational_plan:
            # Создаем DataFrame из списка
            df = pd.DataFrame([
                {
                    "Semester": discipline.semester,
                    "Discipline_Name": discipline.name,
                    "Assessment_type": discipline.assessment_type,
                    "Hours": discipline.hours,
                } for discipline in educational_plan
            ], columns=["Semester", "Discipline_Name", "Assessment_type", "Hours"])
            
            # Добавляем текущую дату в первую строку данных
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header_df = pd.DataFrame([{"Дата создания файла": current_date}])
            df = pd.concat([header_df, df], ignore_index=True)

            excel_content = io.BytesIO()
            with pd.ExcelWriter(excel_content, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Sheet1", index=False)
                worksheet = writer.sheets["Sheet1"]
                # Расширяем столбцы по ширине данных
                for i, col in enumerate(df.columns):
                    max_len = df[col].astype(str).apply(len).max()
                    worksheet.set_column(i, i, max_len + 2)

            # Отправляем Excel-файл 
            input_file = BufferedInputFile(excel_content.getvalue(), filename="educational_plan.xlsx")
            await message.answer_document(input_file, caption="Учебный план")
        else:
            await message.answer(f"Учебный план для специальности с ID {specialty_id} не найден.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при формировании учебного плана: {e}")
    
# Обработка кнопки Институты    
@router_u.message(F.text == '🎓 Институты')
async def Faculties(message: Message):
    await message.answer(f'Выберите факультет, чтобы внести изменения:', reply_markup=await kb.faculties())

@router_u.callback_query(F.data.startswith("action.faculties_start:"))
async def Faculties_start(query: types.CallbackQuery):
    faculties_id = int(query.data.split(":")[1])
    faculties = await get_faculties_for_id(faculties_id)
    await query.message.answer(f'Подробная информация:\n\nНазвание: {faculties.name}\n\nДиректор: {faculties.dean_name}\n\n', reply_markup= await kb.faculties_keyboard_act(faculties_id))

# Добавление нового института
@router_u.callback_query(F.data.startswith("action.faculties.add_"))
async def Faculties_add(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer(f'Давайте добавим новый институт\n\nВведите название нового института:')
    await state.set_state(AddNewFaculty.faculty_name) 

@router_u.message(AddNewFaculty.faculty_name)
async def Process_new_faculty(message: Message, state: FSMContext):
    await state.update_data(faculty_name=message.text)
    await message.answer(f'Введите ФИО директора института:')
    await state.set_state(AddNewFaculty.faculty_dean_name) 

@router_u.message(AddNewFaculty.faculty_dean_name)
async def Process_new_faculty(message: Message, state: FSMContext):
    await state.update_data(faculty_dean_name=message.text)
    data = await state.get_data()
    
    faculty_name = data['faculty_name']
    faculty_dean_name = data['faculty_dean_name']

    faculty_data = {
        'name': faculty_name,
        'dean_name': faculty_dean_name,
    }
    
    faculty_id = await save_faculty_to_db(faculty_data)
    if faculty_id is not True:
        await message.answer("Ошибка: не удалось добавить факультет в базу данных.")
    await message.answer(f'Новый факультет добавлен:\n\n'
                         f'Название: {faculty_data["name"]}\n'
                         f'Директор: {faculty_data["dean_name"]}\n', reply_markup=await kb.return_to_menu())
    await state.clear()

# Изменение института
@router_u.callback_query(F.data.startswith("action.faculties.editstart_"))
async def Faculties_edit(query: types.CallbackQuery):
    faculties_id = int(query.data.split("_")[1])
    await query.message.answer(f'Выберете какой параметр нужно изменить', reply_markup=await kb.faculties_keyboard_act_edit(faculties_id))    

@router_u.callback_query(F.data.startswith("action.faculties.editname_"))
async def Faculties_edit_name(query: types.CallbackQuery, state: FSMContext):
    faculty_id = int(query.data.split("_")[1])
    await query.message.answer("Введите новое название института:")
    await state.update_data(faculty_id=faculty_id)
    await state.set_state(EditFaculty.name)

@router_u.message(EditFaculty.name)
async def process_edit_name(message: Message, state: FSMContext):
    data = await state.get_data()
    faculty_id = data.get('faculty_id')
    new_name = message.text
    await update_faculty_name(faculty_id, new_name)
    await message.answer(f'Название института успешно изменено на {new_name}')
    await state.clear()

@router_u.callback_query(F.data.startswith("action.faculties.editdean_"))
async def Faculties_edit_dean(query: types.CallbackQuery, state: FSMContext):
    faculty_id = int(query.data.split("_")[1])
    await query.message.answer("Введите новое имя декана:")
    await state.update_data(faculty_id=faculty_id)
    await state.set_state(EditFaculty.dean)
    
@router_u.message(EditFaculty.dean)
async def process_edit_dean(message: Message, state: FSMContext):
    data = await state.get_data()
    faculty_id = data.get('faculty_id')
    new_dean = message.text
    await update_faculty_dean(faculty_id, new_dean)
    await message.answer(f'Имя декана успешно изменено на {new_dean}')
    await state.clear()
    
# Удаление института
@router_u.callback_query(F.data.startswith("action.faculties.delete_"))
async def Faculties_delete(query: types.CallbackQuery):
    faculties_id = int(query.data.split("_")[1])
    result = await delete_faculty_from_db(faculties_id)
    if result is not False:
        await query.message.answer(f"Институт успешно удален из базы данных!")
    else:
        await query.message.answer(f"Ошибка: институт не был удален из базы данных.")
    
# Обработка кнопки Специальности     
@router_u.message(F.text == '📚 Специальности')
async def Specialization(message: Message):
    await message.answer(f'Выберите специальность, чтобы внести изменения:', reply_markup=await kb.specialties_all())

@router_u.callback_query(F.data.startswith("action.specialtystart:"))
async def Specialization_act(query: types.CallbackQuery):
    specialization_id = int(query.data.split(":")[1])
    specialization = await get_specialization_by_id(specialization_id)
    if specialization:
        details_message = (
            f'Подробная информация:\n\n'
            f'Название: {specialization.code}\n'
            f'Директор: {specialization.name}\n'
            f'ID Института: {specialization.faculty_id}'
        )
        await query.message.answer(details_message, reply_markup=await kb.faculties_keyboard_act(specialization.faculty_id))
    else:
        await query.message.answer("Извините, не удалось найти информацию о выбранной специальности.")


@router_u.callback_query(F.data.startswith("return_to_menu"))
async def Return_to_menu(query: types.CallbackQuery):
    await query.message.answer('🔮 Главное меню', reply_markup=await kb.menu())