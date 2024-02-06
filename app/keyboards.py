from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from app.database.requests import get_semesters, get_faculties
from app.database.requests_a import get_specializations

async def menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Дисциплины"), KeyboardButton(text="📚 Специальности")],
            [KeyboardButton(text="🎓 Институты"), KeyboardButton(text="📅 Учебный план")],], 
        resize_keyboard=True, input_field_placeholder="Выберите пункт ниже")

# Клавиатура для выбора пола при добавлении нового студента
async def add_new_student_pol():
    buttons = [[
    {"text": "Мужской", "callback_data": "new_student_gender:Male"},
    {"text": "Женский", "callback_data": "new_student_gender:Female"},]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для выбора группы при добавлении нового студента
async def groups_for_add_student_keyboard(groups_list):
    keyboard = [[InlineKeyboardButton(text=f"{group['group_number']}", callback_data=f'new_student_group:{group["id"]}')] for group in groups_list]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для выбора специальности при добавлении новой группы
async def add_new_group_spec():
    specializations = await get_specializations()
    buttons = [[InlineKeyboardButton(text=specialization.name, callback_data=f"select_specialization:{specialization.id}")] for specialization in specializations]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клалавиатура для выбора семестра 
async def semesters_for_practices():
    semesters = await get_semesters()
    buttons = [InlineKeyboardButton(text=f"Семестр {semester}", callback_data=f"practices_semester:{semester}") for semester in semesters]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# Клавиатура для выбора специальности при получении плана обучения
async def specialties():
    specializations = await get_specializations()
    buttons = [[InlineKeyboardButton(text=specialization.name, callback_data=f"specialty_for_education:{specialization.id}")] for specialization in specializations]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для выбора факультета
async def faculties():
    faculties_list = await get_faculties() 
    buttons = [[InlineKeyboardButton(text=faculty.name, callback_data=f"action.faculties_start:{faculty.id}")] for faculty in faculties_list]  
    return InlineKeyboardMarkup(inline_keyboard=buttons)
    
# Клавиатура для действий с факультетами
async def faculties_keyboard_act(faculties_id):
    buttons = [
        InlineKeyboardButton(text="Добавить", callback_data=f"action.faculties.add_{faculties_id}"),
        InlineKeyboardButton(text="Изменить", callback_data=f"action.faculties.editstart_{faculties_id}"),
        InlineKeyboardButton(text="Удалить", callback_data=f"action.faculties.delete_{faculties_id}")]
    return InlineKeyboardMarkup(inline_keyboard=[buttons, [InlineKeyboardButton(text= "🏡 Вернуться в меню", callback_data="return_to_menu")]])

# Клавиатура для действий с факультетами при редактировании факультета
async def faculties_keyboard_act_edit(faculty_id):
    buttons = [
        [InlineKeyboardButton(text="Изменить название", callback_data=f"action.faculties.editname_{faculty_id}")],
        [InlineKeyboardButton(text="Изменить декана", callback_data=f"action.faculties.editdean_{faculty_id}")],
        [InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для выбора специальности при работе со специальностями
async def specialties_all():
    specializations = await get_specializations()
    buttons = [[InlineKeyboardButton(text=specialization.name, callback_data=f"action.specialtystart:{specialization.id}")] for specialization in specializations]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для действий со специальностями
async def specialties_keyboard_act(specialties_id):
    buttons = [
        InlineKeyboardButton(text="Добавить", callback_data=f"action.specialties.add_{specialties_id}"),
        InlineKeyboardButton(text="Изменить", callback_data=f"action.specialties.editstart_{specialties_id}"),
        InlineKeyboardButton(text="Удалить", callback_data=f"action.specialties.delete_{specialties_id}")]
    return InlineKeyboardMarkup(inline_keyboard=[buttons, [InlineKeyboardButton(text= "🏡 Вернуться в меню", callback_data="return_to_menu")]])

# Клавиатура для выбора семестров для отчета о студенте
async def show_semesters_for_student_keyboard(student_semesters):
    buttons = [[InlineKeyboardButton(text=f"Семестр {semester}", callback_data=f"action.show_report:{semester}")] for semester in student_semesters]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для возврата в меню
async def return_to_menu():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]])
