# Архитектура Tabys

Диаграммы написаны на Mermaid — GitHub рисует их прямо на этой странице.

## 1. Компоненты системы

```mermaid
flowchart LR
  U[Владелец кафе<br/>браузер] -->|HTTP| FE[Frontend<br/>React + Vite + three.js]
  FE -->|/api/*  JSON| BE[Backend<br/>FastAPI]
  BE -->|SQLAlchemy| DB[(PostgreSQL / SQLite)]
  BE -->|analytics.py| INT[Модуль «Интеллект»<br/>аудитор · прогноз · матрица]
  BE -->|function calling| G[Google Gemini API]
  BE -->|Checkout Session| S[Stripe]
  S -->|webhook checkout.session.completed| BE
```

## 2. База данных (ER-диаграмма)

```mermaid
erDiagram
  DISHES ||--o{ RECIPE_ITEMS : "техкарта"
  INGREDIENTS ||--o{ RECIPE_ITEMS : "входит в"
  DISHES ||--o{ SALES : "продаётся"
  EMPLOYEES ||--o{ SALES : "пробивает"
  INGREDIENTS ||--o{ STOCK_USAGE : "расход"
  EMPLOYEES ||--o{ CASH_OPERATIONS : "удаления"

  DISHES {
    int id PK
    string name
    string category
    int price
  }
  INGREDIENTS {
    int id PK
    string name
    string unit
    float cost
    float stock
    string supplier
  }
  RECIPE_ITEMS {
    int id PK
    int dish_id FK
    int ingredient_id FK
    float qty
  }
  SALES {
    int id PK
    int order_id
    int dish_id FK
    int employee_id FK
    int qty
    int price
    datetime sold_at
  }
  STOCK_USAGE {
    int id PK
    int ingredient_id FK
    float qty
    date date
  }
  EMPLOYEES {
    int id PK
    string name
    string role
  }
  CASH_OPERATIONS {
    int id PK
    int employee_id FK
    string kind
    int amount
    datetime created_at
  }
  SUBSCRIPTIONS {
    int id PK
    string plan
    string status
    string stripe_session_id UK
  }
```

## 3. Как работает AI-агент (sequence)

```mermaid
sequenceDiagram
  actor O as Владелец
  participant FE as React (чат)
  participant BE as FastAPI /api/agent/chat
  participant G as Gemini
  participant A as analytics.py + БД
  O->>FE: «Где я теряю деньги?»
  FE->>BE: POST {message, history}
  BE->>G: вопрос + описание 6 функций (tools)
  G-->>BE: functionCall get_stock_losses()
  BE->>A: stock_losses(...)
  A-->>BE: Говядина +6,8 % ≈ 106 200 ₸
  BE->>G: functionResponse (результат)
  G-->>BE: functionCall get_cashier_anomalies()
  BE->>A: cashier_anomalies(...)
  A-->>BE: Ерлан ×4 к коллегам
  BE->>G: functionResponse
  G-->>BE: текст ответа с цифрами и советами
  BE-->>FE: {answer, tools_used, mode}
  FE-->>O: ответ + «🔧 аудит склада, аудит кассы»
```

## 4. Как работает оплата (sequence)

```mermaid
sequenceDiagram
  actor O as Владелец
  participant FE as React /pricing
  participant BE as FastAPI
  participant S as Stripe
  participant DB as БД
  O->>FE: «Оформить подписку» (Бизнес)
  FE->>BE: POST /api/billing/checkout {plan}
  BE->>S: checkout.Session.create(mode=subscription)
  S-->>BE: session.id, session.url
  BE->>DB: subscriptions: status=pending
  BE-->>FE: {url}
  FE->>S: переход на страницу оплаты
  O->>S: карта 4242 4242 4242 4242
  S->>BE: webhook checkout.session.completed (подпись проверяется)
  BE->>DB: status=active
  S-->>FE: redirect /billing/success?session_id=...
  FE->>BE: GET /api/billing/verify
  BE->>S: Session.retrieve (на случай, если webhook не дошёл)
  BE-->>FE: подписка active
```

## 5. Навигация по сайту

```mermaid
flowchart TD
  H[/ Главная + 3D/] --> D[/dashboard/]
  H --> AS[/assistant/]
  D --> AU[/audit/]
  D --> AS
  N[Navbar] --> D & M[/menu/] & W[/warehouse/] & AU & I[/insights/] & AS & PR[/pricing/]
  PR -->|Stripe| BS[/billing/success/]
  X[любой другой адрес] --> NF[404]
```

## 6. Дизайн

Figma: https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz — страница «Дизайн-система» (цвета-переменные, 9 стилей текста, компоненты Button, Chip, Badge, StatCard, FeatureCard, IncidentCard, NavBar, Footer), «Desktop 1440» (8 экранов), «Mobile 390» (3 экрана).
