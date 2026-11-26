# Tabys

**Tabys** (каз. «табыс» — доход, прибыль) — веб-система автоматизации кафе и ресторанов, которая не только считает деньги, но и находит, где они теряются.

Касса, меню и техкарты, склад, QR-оплата и чаевые — плюс модуль «Интеллект»:
- **Аудитор потерь** — ищет перерасход продуктов и аномалии на кассе и объясняет их простыми словами (AI-агент);
- **Прогноз и автозаказ** — прогноз продаж по дням недели и готовый заказ поставщику (ML);
- **Советник по меню** — матрица «популярность × маржа» (ML).

## Команда (группа IT-1 2315)

| Участник | Роль | Зона ответственности |
|---|---|---|
| Sultanhodjaev Ilyat | Team Lead · Frontend | планирование, таск-трекер, React-интерфейс |
| Budon Maxim | Backend · DevOps | FastAPI, PostgreSQL, оплата, Docker, CI/CD |
| Amanzhol Ahmetzhan | ML/AI · QA | прогноз спроса, аномалии, AI-агент, тестирование |

Контакт тимлида: sultanhodjaev.ilyat@gmail.com

## Стек

| Слой | Технологии |
|---|---|
| Frontend | React 18, Vite, React Router, CSS |
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| База данных | PostgreSQL |
| Оплата | Kaspi Pay API (план Б — Freedom Pay sandbox) |
| LLM | OpenAI GPT-4o-mini (tool calling) |
| ML | pandas, scikit-learn (Isolation Forest, регрессия) |
| DevOps | Docker Compose, GitHub Actions, Render / Vercel |

## Структура

```
frontend/   React + Vite
backend/    FastAPI
ml/         модели, ноутбуки, генератор данных
docs/       схемы, Гант, UML, задачи
```

## Ветки

- `main` — стабильная версия, только через Pull Request
- `dev` — разработка
- `feature/<название>` — новые функции, PR в `dev`
