from datetime import datetime

# Модель для працівників
class Employee:
    def __init__(self, id: int, telegram_id: int, telegram_username: str, first_name: str, last_name: str,
                 role: str, contact_number: str, email: str, location: str):
        """
        Ініціалізація об'єкта працівника.

        :param id: Унікальний ідентифікатор працівника.
        :param telegram_id: Унікальний ID працівника в Telegram.
        :param telegram_username: Ім'я користувача працівника в Telegram.
        :param first_name: Ім'я працівника.
        :param last_name: Призвище працівника.
        :param role: Роль працівника в компанії.
        :param contact_number: Контактний номер телефону працівника.
        :param email: Адреса електронної пошти працівника.
        :param location: Місцезнаходження працівника (офіс, відділ тощо).
        """
        self.id = id
        self.telegram_id = telegram_id
        self.telegram_username = telegram_username
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.contact_number = contact_number
        self.email = email
        self.location = location

    def __repr__(self):
        """
        Представлення об'єкта працівника у вигляді рядка.

        :return: Рядок, що містить усі атрибути працівника.
        """
        return f"Employee(id={self.id}, telegram_id={self.telegram_id}, telegram_username={self.telegram_username}, " \
               f"first_name={self.first_name}, last_name={self.last_name}, role={self.role}, contact_number={self.contact_number}, " \
               f"email={self.email}, location={self.location})"


# Модель для обладнання
class Equipment:
    def __init__(self, id: int, name: str, description: str, location: str, status: str, responsible_person_id: int):
        """
        Ініціалізація об'єкта обладнання.

        :param id: Унікальний ідентифікатор обладнання.
        :param name: Назва обладнання.
        :param description: Опис обладнання.
        :param location: Місцезнаходження обладнання (де знаходиться обладнання).
        :param status: Статус обладнання (наприклад, "використовується", "доступне").
        :param responsible_person_id: Ідентифікатор працівника, відповідального за обладнання.
        """
        self.id = id
        self.name = name
        self.description = description
        self.location = location
        self.status = status
        self.responsible_person_id = responsible_person_id

    def __repr__(self):
        """
        Представлення об'єкта обладнання у вигляді рядка.

        :return: Рядок, що містить усі атрибути обладнання.
        """
        return f"Equipment(id={self.id}, name={self.name}, description={self.description}, location={self.location}, " \
               f"status={self.status}, responsible_person_id={self.responsible_person_id})"


# Модель для переміщень обладнання
class EquipmentMovement:
    def __init__(self, equipment_id: int, from_location: str, to_location: str, movement_date: datetime, id: int = None):
        """
        Ініціалізація об'єкта для переміщення обладнання.

        :param id: Унікальний ідентифікатор переміщення.
        :param equipment_id: Ідентифікатор обладнання, яке переміщується.
        :param from_location: Початкове місцезнаходження обладнання.
        :param to_location: Кінцеве місцезнаходження обладнання.
        :param movement_date: Дата переміщення.
        """
        self.id = id
        self.equipment_id = equipment_id
        self.from_location = from_location
        self.to_location = to_location
        self.movement_date = movement_date

    def __repr__(self):
        """
        Представлення об'єкта переміщення обладнання у вигляді рядка.

        :return: Рядок, що містить усі атрибути переміщення обладнання.
        """
        return f"EquipmentMovement(id={self.id}, equipment_id={self.equipment_id}, from_location={self.from_location}, " \
               f"to_location={self.to_location}, movement_date={self.movement_date})"
