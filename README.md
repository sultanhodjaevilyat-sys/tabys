# Tabys

[![CI](https://github.com/sultanhodjaevilyat-sys/tabys/actions/workflows/ci.yml/badge.svg)](https://github.com/sultanhodjaevilyat-sys/tabys/actions/workflows/ci.yml)

**Tabys** (каз. «табыс» — доход, прибыль) — веб-система автоматизации кафе и ресторанов, которая не только считает деньги, но и находит, где они теряются.

Касса, меню и техкарты, склад, оплата подписки — плюс модуль «Интеллект»:
- **Аудитор потерь** — ищет перерасход продуктов относительно техкарт и аномалии на кассе;
- **Прогноз и автозаказ** — прогноз продаж по дням недели и готовый заказ поставщику;
- **Советник по меню** — матрица «популярность × маржа» (метод Касаваны–Смита);
- **AI-ассистент владельца** — агент на Gemini с вызовом функций (tool calling): сам достаёт данные из БД и отвечает простыми словами;
- **PaySystem** — подписка на Tabys через Stripe Checkout (тестовый режим) + webhook;
- **3D-модель** рабочего места кассира на главной (three.js): вращается сама, крутится мышкой.

## Ссылки

| Что | Где |
|---|---|
| Дизайн в Figma (дизайн-система + 8 desktop + 3 mobile экрана) | https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz |
| Архитектура и UML (компоненты, ER, sequence, навигация) | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Вопросы к защите и инструкция «что, где, как добавлять» | [docs/GRILL_ME.md](docs/GRILL_ME.md) |
| Задачи команды | [docs/milestone2-tasks.md](docs/milestone2-tasks.md) |

## Команда (группа IT-1 2315)

| Участник | Роль | Зона ответственности |
|---|---|---|
| Sultanhodjaev Ilyat | Team Lead · Frontend | планирование, таск-трекер, React-интерфейс, 3D |
| Budon Maxim | Backend · DevOps | FastAPI, PostgreSQL, оплата Stripe, Docker |
| Amanzhol Ahmetzhan | ML/AI · QA | прогноз спроса, аудитор, AI-агент, тестирование |

Контакт тимлида: sultanhodjaev.ilyat@gmail.com

## Стек

| Слой | Технологии |
|---|---|
| Frontend | React 18, Vite, React Router 6, three.js, CSS |
| Backend | Python 3.10+, FastAPI, SQLAlchemy 2 |
| База данных | SQLite (локально по умолчанию) / PostgreSQL 16 (Docker) |
| AI-агент | Google Gemini API (function calling) |
| Оплата | Stripe Checkout, mode=subscription, webhook |
| DevOps | Docker Compose |

## Запуск на компьютере

Нужны **Python 3.10+** и **Node.js 18+**.

**1. Бэкенд** (терминал 1):
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # вставьте ключи GEMINI_API_KEY и STRIPE_SECRET_KEY (можно пусто — будет демо-режим)
uvicorn app.main:app --reload
```
API: http://localhost:8000/docs — при первом запуске база заполняется тестовыми данными (8 недель продаж).

**2. Фронтенд** (терминал 2):
```bash
cd frontend
npm install
npm run dev
```
Сайт: http://localhost:5173

**PostgreSQL вместо SQLite:** `docker compose up db`, затем в `backend/.env`:
`DATABASE_URL=postgresql+psycopg2://tabys:tabys@localhost:5432/tabys`

## Тесты

```bash
cd backend
pip install -r requirements.txt httpx
python -m unittest -v      # 11 unit-тестов аналитики + 8 тестов API
```
Те же тесты и сборка фронтенда автоматически запускаются в GitHub Actions при каждом push и Pull Request.

## Страницы

| Маршрут | Страница |
|---|---|
| `/` | Главная + 3D-модель + сравнение с iiko / Paloma / Rosta |
| `/dashboard` | Панель владельца: выручка, чеки, food cost, потери |
| `/menu` | Меню и техкарты (себестоимость, маржа) |
| `/warehouse` | Склад, прогноз на 7 дней, заказ поставщикам |
| `/audit` | Аудитор потерь: склад и касса |
| `/insights` | Матрица меню 2×2 |
| `/assistant` | AI-ассистент (чат) |
| `/pricing` | Тарифы, оплата через Stripe |
| `/billing/success` | Подтверждение подписки |
| `*` | 404 |

## Как работают ключевые части

**AI-агент** (`backend/app/agent.py`): вопрос + описание 6 функций → Gemini решает, какую функцию вызвать → бэкенд выполняет её на данных БД → Gemini пишет ответ с цифрами. Без ключа — демо-режим (функция выбирается по ключевым словам), помечается в интерфейсе.

**Оплата** (`backend/app/billing.py`): `POST /api/billing/checkout` создаёт Stripe Checkout Session → пользователь платит тестовой картой `4242 4242 4242 4242` → webhook `checkout.session.completed` (или проверка `/api/billing/verify`) ставит подписке статус `active`.

**Формулы** (`backend/app/analytics.py`):
- себестоимость = Σ (норма по техкарте × цена ингредиента);
- перерасход = факт расхода − продажи × норма; сигнал при > 5 %;
- касса: удаления после пречека на 100 чеков, сигнал если в 2+ раза чаще коллег;
- прогноз = среднее по такому же дню недели за 4 недели × тренд (2 последние недели / 2 предыдущие);
- заказ = прогноз × техкарта × 1,15 − остаток;
- матрица меню: популярность ≥ 70 % от средней доли, маржа ≥ средневзвешенной.

## База данных

`ingredients`, `dishes`, `recipe_items` (техкарта, связь многие-ко-многим блюдо↔ингредиент), `employees`, `sales`, `stock_usage`, `cash_operations`, `subscriptions`. Описание связей — в `backend/app/models.py`.

## Ветки

- `main` — стабильная версия, только через Pull Request
- `dev` — разработка
- `feature/<название>` — новые функции, PR в `dev`
