Курсовая работа по базам данных варианта 10 

Решением является создание телеграмм бота, который взаимодействует с базой данных, позволяет добавлять, редактировать, удалять каждое поле из 6 таблиц
А также удобный пользовательский интерфейс

Реализован бот на библиотеке aiogramm 3.2 и sqlachemy 

Структура бота:

run - файл отвечающий за запуск бота 

models - описание базы данных, добавление асинхронного контекста для взамойдействия с данными

handlers - файл реагирующий на взаимодействия с ботом от действий пользователя 

admin - файл реагирующий на взаимодейтсвие с ботом от действия администратора (в т.ч. и выход отчётов) 

reuests и requests_a - файлы для запросов к базе данных 

keyboards - файл для создания различных инлайн клавиатур с данными из бд

Задание: БД «Текущая успеваемость»
  На факультете по специальности обучаются несколько групп студентов. Для каждой 
специальности определен список предметов, курсовых работ. Для каждого предмета, курсовой работы 
и практики известно в каком семестре (семестрах) они преподаются, а также вид аттестации (экзамен, 
зачет) для каждого семестра. Необходимо иметь возможность заполнять личные карточки студента. 
Личная карточка содержит список предметов за семестр с указанием оценок.
  Выходные документы:
1. Личная карточка студента. Для конкретного студента выдать список предметов и курсовых 
работ за определенный курс обучения (2 семестра) с указанием оценок.
2. Для каждой специальности вывести список экзаменов, зачетов, курсовых по дисциплинам в 
определенном семестре.
3. Учебный план – набор дисциплин для специальностей.
