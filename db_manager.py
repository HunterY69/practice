import asyncpg
# SQL-запити для створення таблиць
create_employee_table = """
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    telegram_username TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    role TEXT NOT NULL,
    contact_number TEXT NOT NULL,
    email TEXT NOT NULL,
    location TEXT NOT NULL  
);
"""

create_equipment_table = """
CREATE TABLE IF NOT EXISTS equipment (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    location TEXT NOT NULL,
    status TEXT NOT NULL,
    responsible_person_id INTEGER REFERENCES employees(id) ON DELETE SET NULL
);
"""

create_equipment_movement_table = """
CREATE TABLE IF NOT EXISTS equipment_movements (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES equipment(id) ON DELETE CASCADE,
    from_location TEXT NOT NULL,
    to_location TEXT NOT NULL,
    movement_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
"""

# SQL-запити для отримання даних
get_all_equipment_query = """
SELECT id, name, description, location, status, responsible_person_id
FROM equipment
ORDER BY id;
"""

get_equipment_for_user_query = """
SELECT id, name, description, location, status, responsible_person_id
FROM equipment
WHERE responsible_person_id = $1
ORDER BY id;
"""

get_available_equipment_query = """
SELECT id, name, description, location, status, responsible_person_id
FROM equipment
WHERE status = 'Доступний'
ORDER BY id;
"""

get_employee_by_telegram_id_query = """
SELECT id FROM employees WHERE telegram_id = $1;
"""

# SQL-запит для отримання інформації про відповідального за обладнання працівника
get_responsible_employee_query = """
SELECT e.id, e.telegram_id, e.telegram_username, e.first_name, e.last_name, e.role, e.contact_number, e.email, e.location
FROM employees e
JOIN equipment eq ON eq.responsible_person_id = e.id
WHERE eq.id = $1;
"""

# SQL-запит для оновлення місцезнаходження обладнання
update_equipment_location_query = """
UPDATE equipment
SET location = $1
WHERE id = $2;
"""

# SQL-запит для вставки нового запису про переміщення обладнання
insert_equipment_movement_query = """
INSERT INTO equipment_movements (equipment_id, from_location, to_location, movement_date)
VALUES ($1, $2, $3, $4)
RETURNING id;
"""

# SQL-запит для отримання обладнання за ID
get_equipment_by_id_query = """
SELECT id, name, description, location, status, responsible_person_id
FROM equipment
WHERE id = $1;
"""

# SQL-запит для отримання всіх рухів обладнання
get_all_equipment_movements_query = """
SELECT id, equipment_id, from_location, to_location, movement_date
FROM equipment_movements
ORDER BY id;
"""

update_equipment_status_query = """
UPDATE equipment
SET status = $1
WHERE id = $2;
"""

from config import DB_USER
from config import DB_NAME
from config import DB_PASSWORD
from config import DB_HOST

from models import Equipment, EquipmentMovement, Employee

async def create_tables():
    # Підключення до бази даних
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)

    try:
        # Створення таблиць
        await conn.execute(create_employee_table)
        await conn.execute(create_equipment_table)
        await conn.execute(create_equipment_movement_table)
        print("Таблиці успішно створено.")
    except Exception as e:
        print(f"Помилка при створенні таблиць: {e}")
    finally:
        # Закриття підключення
        await conn.close()

async def get_employee_by_telegram_id(telegram_id: int):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)
    employee = await conn.fetchrow(get_employee_by_telegram_id_query, telegram_id)
    return employee

async def get_all_equipment():
    # Підключення до бази даних
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)

    try:
        rows = await conn.fetch(get_all_equipment_query)
        # Створюємо список об'єктів Equipment
        equipment_list = [Equipment(**row) for row in rows]
        return equipment_list

    except Exception as e:
        print(f"Помилка при отриманні обладнання: {e}")
        return []

    finally:
        # Закриття підключення
        await conn.close()

async def get_available_equipment():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)

    try:
        rows = await conn.fetch(get_available_equipment_query)
        equipment_list = [Equipment(**row) for row in rows]
        return equipment_list

    except Exception as e:
        print(f"Помилка при отриманні обладнання: {e}")
        return []

    finally:
        await conn.close()

async def get_responsible_employee_for_equipment(equipment_id: int):
    # Підключення до бази даних
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)

    try:
        # Виконання запиту для отримання відповідального працівника
        employee_row = await conn.fetchrow(get_responsible_employee_query, equipment_id)

        if employee_row:
            # Якщо знайшовся відповідальний працівник, створюємо об'єкт Employee
            responsible_employee = Employee(**employee_row)
            return responsible_employee
        else:
            return None

    except Exception as e:
        print(f"Помилка при отриманні відповідального працівника: {e}")
        return None

    finally:
        # Закриття підключення
        await conn.close()

async def update_equipment_location(equipment_id: int, new_location: str):
    """
    Оновлює місцезнаходження обладнання в базі даних.

    :param equipment_id: ID обладнання, місцезнаходження якого потрібно оновити.
    :param new_location: Нове місцезнаходження обладнання.
    """
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)

    try:
        # Виконання запиту на оновлення місцезнаходження обладнання
        result = await conn.execute(update_equipment_location_query, new_location, equipment_id)

        if result == "UPDATE 1":
            print(f"Місцезнаходження обладнання з ID {equipment_id} успішно оновлено.")
        else:
            print(f"Не вдалося оновити місцезнаходження для обладнання з ID {equipment_id}.")
    except Exception as e:
        print(f"Помилка при оновленні місцезнаходження обладнання: {e}")
    finally:
        # Закриття підключення
        await conn.close()

async def insert_equipment_movement(equipment_movement: EquipmentMovement):
    """
    Вставляє новий запис про переміщення обладнання в базу даних.

    :param equipment_movement: Об'єкт EquipmentMovement, що містить інформацію про переміщення.
    :return: ID нового запису, якщо вставка успішна, або None в разі помилки.
    """
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)

    try:
        # Виконання запиту на вставку нового запису
        movement_id = await conn.fetchval(insert_equipment_movement_query,
                                           equipment_movement.equipment_id,
                                           equipment_movement.from_location,
                                           equipment_movement.to_location,
                                           equipment_movement.movement_date)

        if movement_id:
            print(f"Запис про переміщення обладнання успішно додано з ID {movement_id}.")
            return movement_id
        else:
            print("Не вдалося додати запис про переміщення обладнання.")
            return None
    except Exception as e:
        print(f"Помилка при вставці запису про переміщення обладнання: {e}")
        return None
    finally:
        # Закриття підключення
        await conn.close()



async def get_equipment_by_id(equipment_id: int):
    """
    Отримує інформацію про обладнання за його ID.

    :param equipment_id: ID обладнання, яке потрібно отримати.
    :return: Об'єкт Equipment, якщо обладнання знайдено, або None, якщо не знайдено.
    """
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)

    try:
        # Виконання запиту для отримання обладнання за ID
        row = await conn.fetchrow(get_equipment_by_id_query, equipment_id)

        if row:
            # Якщо знайдено обладнання, створюємо об'єкт Equipment
            equipment = Equipment(**row)
            return equipment
        else:
            print(f"Обладнання з ID {equipment_id} не знайдено.")
            return None
    except Exception as e:
        print(f"Помилка при отриманні обладнання за ID: {e}")
        return None
    finally:
        # Закриття підключення
        await conn.close()

async def get_all_equipment_movements():
    """
    Отримує всі записи про рухи обладнання з бази даних.

    :return: Список об'єктів EquipmentMovement, якщо є рухи обладнання, або порожній список, якщо рухів немає.
    """
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)

    try:
        # Виконання запиту для отримання всіх рухів обладнання
        rows = await conn.fetch(get_all_equipment_movements_query)

        # Якщо є результати, створюємо список об'єктів EquipmentMovement
        equipment_movements = [EquipmentMovement(**row) for row in rows]
        return equipment_movements
    except Exception as e:
        print(f"Помилка при отриманні рухів обладнання: {e}")
        return []
    finally:
        # Закриття підключення
        await conn.close()

    async def update_equipment_status(equipment_id: int, new_status: str):
        """
        Оновлює статус обладнання в базі даних.

        :param equipment_id: ID обладнання, для якого потрібно оновити статус.
        :param new_status: Новий статус для обладнання.
        """
        conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST)

        try:
            # Виконання запиту на оновлення статусу
            result = await conn.execute(update_equipment_status_query, new_status, equipment_id)

            if result == "UPDATE 1":
                print(f"Статус обладнання з ID {equipment_id} успішно оновлено на '{new_status}'.")
            else:
                print(f"Не вдалося оновити статус для обладнання з ID {equipment_id}.")
        except Exception as e:
            print(f"Помилка при оновленні статусу обладнання: {e}")
        finally:
            # Закриття підключення
            await conn.close()