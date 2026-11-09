"""Наполняет базу тестовыми данными.

Запуск:  docker compose exec backend python -m app.seed
Повторный запуск ничего не дублирует.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Category, Equipment, EquipmentUnit, RentalTerm, User
from app.models.enums import AllowedFor, UnitCondition, UserRole, UserType
from app.security import hash_password

USERS = [
    dict(full_name="Администратор", email="admin@campus.ru", password="Admin12345",
         role=UserRole.ADMIN, user_type=UserType.EMPLOYEE, group_or_department="Отдел оборудования"),
    dict(full_name="Иван Студентов", email="student@campus.ru", password="Student12345",
         role=UserRole.USER, user_type=UserType.STUDENT, group_or_department="ИС-21"),
    dict(full_name="Пётр Сотрудников", email="employee@campus.ru", password="Employee12345",
         role=UserRole.USER, user_type=UserType.EMPLOYEE, group_or_department="Кафедра физики"),
]

CATEGORIES = {
    "Проекторы": "Проекторы для лекций, защит и мероприятий",
    "Камеры": "Фото- и видеокамеры для съёмки",
    "Микрофоны": "Проводные и беспроводные микрофоны",
    "Штативы": "Штативы для камер и осветительных приборов",
    "Лабораторные приборы": "Измерительные приборы для лабораторных работ",
    "Спортивный инвентарь": "Мячи, сетки и другой инвентарь для занятий спортом",
}

EQUIPMENT = [
    ("Проекторы", "Проектор Epson EB-X49", "Epson",
     "Яркость 3600 лм, разрешение XGA, HDMI и VGA. Подходит для аудитории до 40 человек.",
     3, 3000, 200, AllowedFor.ALL, "Предъявить студенческий билет или пропуск", 3),
    ("Проекторы", "Проектор BenQ MW535", "BenQ",
     "Яркость 3600 лм, разрешение WXGA, HDMI. Лёгкий, удобен для переноса.",
     3, 3000, 200, AllowedFor.ALL, "Предъявить студенческий билет или пропуск", 2),
    ("Камеры", "Фотоаппарат Canon EOS 250D", "Canon",
     "Зеркальная камера 24 Мп с объективом 18-55 мм, сумка и карта памяти в комплекте.",
     5, 10000, 500, AllowedFor.ALL, "Предъявить студенческий билет, подписать акт приёма", 2),
    ("Камеры", "Экшн-камера GoPro Hero 11", "GoPro",
     "Видео 5.3K, водонепроницаемый корпус, набор креплений.",
     3, 8000, 400, AllowedFor.ALL, "Предъявить студенческий билет, подписать акт приёма", 2),
    ("Микрофоны", "Микрофон Shure SM58", "Shure",
     "Динамический вокальный микрофон с кабелем XLR 5 м.",
     5, 2000, 100, AllowedFor.ALL, "Предъявить студенческий билет или пропуск", 4),
    ("Микрофоны", "Петличная система Rode Wireless GO II", "Rode",
     "Беспроводная петличная система на два канала, дальность до 200 м.",
     5, 6000, 300, AllowedFor.ALL, "Предъявить студенческий билет или пропуск", 2),
    ("Штативы", "Штатив Manfrotto 055", "Manfrotto",
     "Алюминиевый штатив высотой до 170 см, нагрузка до 9 кг.",
     7, 1500, 100, AllowedFor.ALL, "Предъявить студенческий билет или пропуск", 3),
    ("Лабораторные приборы", "Осциллограф Rigol DS1054Z", "Rigol",
     "Цифровой осциллограф, 4 канала, 50 МГц.",
     7, 15000, 700, AllowedFor.EMPLOYEE, "Только для сотрудников университета, нужна заявка от кафедры", 2),
    ("Лабораторные приборы", "Мультиметр Fluke 117", "Fluke",
     "Цифровой мультиметр с бесконтактным определением напряжения.",
     7, 4000, 200, AllowedFor.ALL, "Предъявить студенческий билет, пройти инструктаж по технике безопасности", 3),
    ("Спортивный инвентарь", "Футбольный мяч Adidas", "Adidas",
     "Мяч размера 5 для тренировок на траве и в зале.",
     3, 0, 50, AllowedFor.ALL, "Предъявить студенческий билет", 5),
    ("Спортивный инвентарь", "Волейбольный набор", "Mikasa",
     "Сетка, антенны и два мяча.",
     3, 1000, 100, AllowedFor.ALL, "Предъявить студенческий билет", 2),
]


def seed(db: Session) -> bool:
    """Добавляет то, чего ещё нет. Возвращает False, если добавлять было нечего."""
    added = False

    # Пользователи: пропускаем тех, чей email уже есть в базе
    existing_emails = set(db.scalars(select(User.email)))
    for item in USERS:
        if item["email"] in existing_emails:
            continue
        data = dict(item)
        password = data.pop("password")
        db.add(User(password_hash=hash_password(password), **data))
        added = True

    # Каталог: добавляем, только если в базе ещё нет ни одной категории
    if db.scalar(select(Category).limit(1)) is None:
        categories = {name: Category(name=name, description=text) for name, text in CATEGORIES.items()}
        db.add_all(categories.values())

        for index, (cat, name, maker, desc, days, deposit, fine, allowed, req, count) in enumerate(EQUIPMENT, start=1):
            equipment = Equipment(category=categories[cat], name=name, manufacturer=maker, description=desc)
            equipment.terms = RentalTerm(
                max_days=days, deposit=deposit, fine_per_day=fine, allowed_for=allowed, requirements=req
            )
            for number in range(1, count + 1):
                condition = UnitCondition.NEW if number == 1 else UnitCondition.GOOD
                db.add(EquipmentUnit(
                    equipment=equipment,
                    inventory_number=f"CG-{index:03d}-{number}",
                    condition=condition,
                ))
            db.add(equipment)
        added = True

    db.commit()
    return added


def main():
    with SessionLocal() as db:
        if seed(db):
            print("Тестовые данные добавлены.")
            print("Админ:      admin@campus.ru / Admin12345")
            print("Студент:    student@campus.ru / Student12345")
            print("Сотрудник:  employee@campus.ru / Employee12345")
        else:
            print("База уже заполнена, ничего не добавлено.")


if __name__ == "__main__":
    main()
