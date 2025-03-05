import logging
import asyncio
import time
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from db_manager import create_tables, get_employee_by_telegram_id, get_all_equipment, get_available_equipment, get_responsible_employee_for_equipment, update_equipment_location, insert_equipment_movement, get_equipment_by_id, get_all_equipment_movements, update_equipment_status as update_equipment_status_db

# Встановлюємо токен бота
from config import API_TELEGRAM_TOKEN as API_TOKEN
from models import EquipmentMovement

LOCATIONS = "Аудиторія 3.333", "Інженерна кімната", "Co-working-зона", "Виробнича зона", "Ремонтна майстерня", "Внутрішній дворик"

STATUS_LIST = "Доступний", "Зайнятий"

# Налаштовуємо логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Функція для команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("start called")
    await update.message.reply_text(
        'Привіт! Я бот для обліку обладнання. Використовуй команди, щоб дізнатися інформацію про обладнання. /help')
    await create_tables()
    print(update.message.from_user.id)

# Функція для команди /equipment
async def equipment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    employee = await get_employee_by_telegram_id(update.message.chat.id)
    await update.message.reply_text("Ось список обладнання")

    if employee:
        equipment_list = await get_all_equipment()
        for equipment in equipment_list:
            print(equipment)
            responsible_employee = await get_responsible_employee_for_equipment(equipment.id)
            message = (f"Назва: {equipment.name}\n"
                      f"Опис: {equipment.description}\n"
                      f"Місцезнаходження: {equipment.location}\n"
                      f"Статус: {equipment.status}\n"
                      f"Відповідальний: {responsible_employee.first_name} {responsible_employee.last_name}\n"
                      f"Контакти: @{responsible_employee.telegram_username}\n"
                      f"Phone: {responsible_employee.contact_number}\n"
                      f"Mail: {responsible_employee.email}")
            if equipment.status == 'Доступний':
                keyboard = [
                    [
                        InlineKeyboardButton("Перемістити обладнання", callback_data=f"move_{equipment.id}"),
                        InlineKeyboardButton("Змінити статус", callback_data=f"upd_status_{equipment.id}")
                     ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(message, reply_markup=reply_markup)
            else:
                keyboard = [
                    [
                        InlineKeyboardButton("Змінити статус", callback_data=f"upd_status_{equipment.id}")
                     ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(message, reply_markup=reply_markup)
    else:
        equipment_list = await get_available_equipment()
        for equipment in equipment_list:
            print(equipment)
            responsible_employee = await get_responsible_employee_for_equipment(equipment.id)
            await update.message.reply_text(f"Назва: {equipment.name}\n"
                                            f"Опис: {equipment.description}\n"
                                            f"Відповідальний: {responsible_employee.first_name} {responsible_employee.last_name}\n"
                                            f"Зв'язатися @{responsible_employee.telegram_username}\n")

async def move_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(query.data)
    await query.answer()

    # Отримуємо ID обладнання з callback_data
    equipment_id = query.data.split("_")[1]

    # Отримуємо список доступних локацій
    locations = LOCATIONS

    # Розбиваємо локації на групи по 2 або 3 елементи
    rows = [locations[i:i + 3] for i in range(0, len(locations), 3)]
    # Створюємо клавіатуру для вибору локації
    keyboard = [
        [InlineKeyboardButton(location, callback_data=f"movee_to_{equipment_id}_{location}") for location in row]
        for row in rows
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Відправляємо повідомлення з вибором локацій
    await query.edit_message_text("Оберіть нову локацію для переміщення обладнання:", reply_markup=reply_markup)

# Обробка натискання на вибір локації
async def move_to_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    print(query.data)
    await query.answer()

    # Отримуємо ID обладнання та локації з callback_data
    data = query.data.split("_")
    equipment_id = data[2]
    location = data[3]
    print(equipment_id, location)

    # Переміщуємо обладнання в нову локацію
    # Функція для оновлення місця обладнання
    await move_equipment_to_location(int(equipment_id), location)

    await query.edit_message_text(f"Обладнання переміщено на нову локацію {location}.")


# Функція для переміщення обладнання на нову локацію (реалізуємо її за потребою)
async def move_equipment_to_location(equipment_id, location):
    equipment_location = await get_equipment_by_id(equipment_id)
    await insert_equipment_movement(EquipmentMovement(equipment_id=equipment_id, from_location=equipment_location.location, to_location=location, movement_date=datetime.now()))
    await update_equipment_location(equipment_id, location)
    print(f"Переміщення обладнання з ID {equipment_id} на локацію {location}")
    pass

async def equipment_movements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movements = await get_all_equipment_movements()
    employee = await get_employee_by_telegram_id(update.message.chat.id)
    if employee:
        message = "Ось список усіх рухів обладнання\n\n"
        for movement in movements:
            equipment = await get_equipment_by_id(movement.equipment_id)
            message += (f"Обладнання: {equipment.name}\n"
                        f"Переміщено із {movement.from_location}\n"
                        f"до {movement.to_location}\n"
                        f"Дата переміщення: {movement.movement_date}\n")
            message += "\n"
        await update.message.reply_text(message)

async def update_equipment_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(query.data)
    await query.answer()

    equipment_id = query.data.split("_")[2]

    status_options = STATUS_LIST

    keyboard = [
        [InlineKeyboardButton(status, callback_data=f"update_status_{equipment_id}_{status}") for status in
         status_options]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Оновіть статус обладнання:", reply_markup=reply_markup)

async def update_equipment_status_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("UPDATE STATUS TO")
    query = update.callback_query
    print(query.data)
    await query.answer()

    equipment_id = query.data.split("_")[2]
    new_status = query.data.split("_")[3]

    await update_equipment_status_db(int(equipment_id), new_status)
    await query.edit_message_text(f"Статус успішно оновлено на {new_status}")

# Функція для команди /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
    Видає список команд доступних користувачу
    :param update:
    :param context:
    :return:
    '''
    print("help command called")
    help_text = (
        "Доступні команди:\n"
        "/start - Привітання\n"
        "/equipment - Список доступного обладнання\n"
        "/movements - Інформація про переміщення обладнання\n"
        "/help - Показати цю допомогу"
    )
    await update.message.reply_text(help_text)


# Основна функція для запуску
def main():
    # Створюємо об'єкт Application та передаємо токен
    application = Application.builder().token(API_TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("equipment", equipment))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("movements", equipment_movements))

    application.add_handler(CallbackQueryHandler(move_equipment, pattern="^move_"))
    application.add_handler(CallbackQueryHandler(move_to_location, pattern="^movee_to_"))
    application.add_handler(CallbackQueryHandler(update_equipment_status, pattern="^upd_status_"))
    application.add_handler(CallbackQueryHandler(update_equipment_status_to, pattern="^update_status_"))

    # Запускаємо бота
    application.run_polling()

# Запуск основної асинхронної функції
if __name__ == '__main__':
    asyncio.run(main())
