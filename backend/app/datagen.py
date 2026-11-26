"""Генератор тестовых данных кафе (чистый Python, без БД).

Создаёт 8 недель продаж, фактический расход склада и кассовые операции.
Специально «подкладывает» две проблемы, которые должен найти Аудитор:
  1) перерасход говядины в вечерние смены вторника и четверга;
  2) кассир с подозрительно большим числом удалений после пречека.
"""
import random
from typing import Optional
from datetime import date, datetime, timedelta

INGREDIENTS = [
    # id, name, unit, cost_per_unit (₸), stock, supplier
    (1, "Говядина", "кг", 4000, 70.0, "Мясной двор"),
    (2, "Баранина", "кг", 4500, 45.0, "Мясной двор"),
    (3, "Курица", "кг", 1800, 20.0, "Алель Агро"),
    (4, "Мука", "кг", 350, 40.0, "Цесна"),
    (5, "Рис", "кг", 700, 25.0, "Цесна"),
    (6, "Картофель", "кг", 250, 35.0, "Овощебаза №1"),
    (7, "Лук", "кг", 200, 20.0, "Овощебаза №1"),
    (8, "Морковь", "кг", 220, 15.0, "Овощебаза №1"),
    (9, "Сыр", "кг", 3800, 6.0, "Молочный край"),
    (10, "Молоко", "л", 450, 30.0, "Молочный край"),
    (11, "Кофе зерно", "кг", 9000, 4.0, "Coffee Lab"),
    (12, "Чай", "кг", 5000, 3.0, "Coffee Lab"),
    (13, "Салат Романо", "кг", 1600, 9.0, "Овощебаза №1"),
    (14, "Сливочный сыр", "кг", 4200, 3.0, "Молочный край"),
]

DISHES = [
    # id, name, category, price (₸), emoji, base daily demand
    (1, "Бешбармак", "Горячее", 3900, "🍲", 14),
    (2, "Лагман", "Горячее", 2600, "🍜", 22),
    (3, "Плов", "Горячее", 2400, "🍛", 25),
    (4, "Манты (5 шт)", "Горячее", 2200, "🥟", 20),
    (5, "Шашлык из баранины", "Гриль", 3500, "🍢", 12),
    (6, "Бургер Tabys", "Гриль", 2900, "🍔", 18),
    (7, "Цезарь с курицей", "Салаты", 2500, "🥗", 15),
    (8, "Самса", "Выпечка", 700, "🥐", 30),
    (9, "Капучино", "Напитки", 1200, "☕", 35),
    (10, "Чай казахский", "Напитки", 900, "🫖", 28),
    (11, "Чизкейк", "Десерты", 1800, "🍰", 8),
    (12, "Борщ", "Горячее", 1900, "🥣", 6),
]

# Техкарты: dish_id -> [(ingredient_id, qty per portion)]
RECIPES = {
    1: [(1, 0.25), (4, 0.10), (7, 0.05)],
    2: [(1, 0.12), (4, 0.15), (6, 0.05), (8, 0.04), (7, 0.03)],
    3: [(2, 0.12), (5, 0.15), (8, 0.08), (7, 0.04)],
    4: [(1, 0.10), (2, 0.05), (4, 0.12), (7, 0.05)],
    5: [(2, 0.30), (7, 0.08)],
    6: [(1, 0.15), (4, 0.08), (9, 0.03), (7, 0.02)],
    7: [(3, 0.12), (13, 0.10), (9, 0.02)],
    8: [(2, 0.05), (4, 0.08), (7, 0.03)],
    9: [(11, 0.018), (10, 0.15)],
    10: [(12, 0.006), (10, 0.05)],
    11: [(14, 0.10), (4, 0.03), (10, 0.02)],
    12: [(1, 0.06), (6, 0.08), (8, 0.04), (7, 0.03)],
}

EMPLOYEES = [
    (1, "Айгерим", "Кассир"),
    (2, "Ерлан", "Кассир"),
    (3, "Дана", "Официант"),
    (4, "Тимур", "Официант"),
]

WEEKDAY_FACTOR = [0.85, 0.9, 0.95, 1.0, 1.25, 1.45, 1.3]  # пн..вс


def generate(today: Optional[date] = None, weeks: int = 8, seed: int = 42) -> dict:
    rnd = random.Random(seed)
    today = today or date.today()
    start = today - timedelta(days=weeks * 7)
    sales, usage, cash_ops = [], [], []
    order_id = 0
    sale_id = 0
    for d in range(weeks * 7):
        day = start + timedelta(days=d)
        wf = WEEKDAY_FACTOR[day.weekday()]
        trend = 1 + 0.004 * d  # медленный рост
        day_expected = {}  # ingredient -> expected usage
        evening_beef = 0.0
        for dish_id, _n, _c, price, _e, base in DISHES:
            qty = max(0, int(rnd.gauss(base * wf * trend, base * 0.15)))
            # раскладываем по сменам и заказам
            for _ in range(qty):
                shift = "вечер" if rnd.random() < 0.55 else "день"
                if rnd.random() < 0.45 or order_id == 0:
                    order_id += 1
                hour = rnd.randint(17, 22) if shift == "вечер" else rnd.randint(10, 16)
                emp = rnd.choice([1, 2])
                sale_id += 1
                sales.append({
                    "id": sale_id,
                    "order_id": order_id,
                    "dish_id": dish_id,
                    "qty": 1,
                    "price": price,
                    "sold_at": datetime(day.year, day.month, day.day, hour, rnd.randint(0, 59)),
                    "employee_id": emp,
                    "shift": shift,
                })
                for ing_id, q in RECIPES[dish_id]:
                    day_expected[ing_id] = day_expected.get(ing_id, 0) + q
                    if ing_id == 1 and shift == "вечер":
                        evening_beef += q
        # фактический расход = техкарта ± шум (естественная потеря 1–3 %)
        for ing_id, exp in day_expected.items():
            actual = exp * (1 + rnd.uniform(0.01, 0.03))
            if ing_id == 1 and day.weekday() in (1, 3):  # вторник, четверг
                actual += evening_beef * 0.35  # «пропадает» 35 % вечерней говядины
            usage.append({"ingredient_id": ing_id, "qty": round(actual, 3), "date": day})
        # кассовые операции: удаления позиций после пречека, скидки
        for emp_id, _name, role in EMPLOYEES:
            if role != "Кассир":
                continue
            base_voids = 0.4 if emp_id == 1 else 1.6  # Ерлан удаляет в 4 раза чаще
            n = sum(1 for _ in range(4) if rnd.random() < base_voids / 4 * 2)
            for _ in range(n):
                cash_ops.append({
                    "kind": "удаление после пречека",
                    "amount": rnd.choice([700, 1200, 2200, 2600, 3500, 3900]),
                    "employee_id": emp_id,
                    "created_at": datetime(day.year, day.month, day.day, rnd.randint(11, 22), rnd.randint(0, 59)),
                })
    return {
        "ingredients": [dict(zip(["id", "name", "unit", "cost", "stock", "supplier"], r)) for r in INGREDIENTS],
        "dishes": [dict(zip(["id", "name", "category", "price", "emoji", "base"], r)) for r in DISHES],
        "recipes": [{"dish_id": d, "ingredient_id": i, "qty": q} for d, items in RECIPES.items() for i, q in items],
        "employees": [dict(zip(["id", "name", "role"], r)) for r in EMPLOYEES],
        "sales": sales,
        "usage": usage,
        "cash_ops": cash_ops,
    }
