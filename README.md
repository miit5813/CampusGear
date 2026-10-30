# CampusGear
<<<<<<< HEAD

Сервис аренды кампусного оборудования университета: каталог, бронирование, согласование администратором, выдача и возврат, штрафы и уведомления.

## Ключевой сценарий

Каталог оборудования → Карточка устройства → Выбор периода аренды → Заявка → Одобрение администратором → Личный кабинет с активной арендой и статусом возврата.

## Стек

- **Frontend:** HTML, CSS, JavaScript (ES-модули, fetch), Bootstrap 5
- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic
- **БД:** PostgreSQL
- **Авторизация:** JWT, роли `user` / `admin`
- **Документация API:** Swagger UI, генерируется FastAPI автоматически (`/docs`)
- **Инфраструктура:** Docker Compose

## Структура репозитория

```
campusgear/
├── backend/
│   └── app/
│       ├── routers/    # эндпоинты API
│       ├── models/     # модели БД (SQLAlchemy)
│       ├── schemas/    # схемы запросов и ответов (Pydantic)
│       └── services/   # бизнес-логика
├── frontend/
│   ├── css/            # стили
│   ├── js/             # скрипты (api.js, main.js, ...)
│   └── pages/          # страницы сайта
├── docs/               # ER-диаграмма, пользовательские сценарии
├── docker-compose.yml
└── README.md
```

## Быстрый старт

Требуется: Docker и Python 3.

```bash
# 1. Настройки окружения
cp .env.example .env
cp backend/.env.example backend/.env

# 2. База данных и backend
docker compose up -d --build

# 3. Frontend (простой статический сервер)
cd frontend
python -m http.server 5173
```

- Сайт: http://localhost:5173
- API: http://localhost:8000/api/health
- Swagger-документация: http://localhost:8000/docs

Backend без Docker:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Git-процесс

- Ветки: `main` (стабильная), `develop`, `feature/<название>`
- Коммиты по Conventional Commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `chore:`
- Слияние в `develop` через Pull Request

## Прогресс

См. [ROADMAP.md](ROADMAP.md).

## Лицензия

MIT
=======
Сервис по выдачи университетского оборудования
>>>>>>> 0b56307052bc38389560fc05d1dad54fb712352a
