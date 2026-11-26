"""Модуль «Интеллект» Tabys: чистые функции над списками словарей.

Все формулы простые и объяснимые — их легко показать на защите.
"""
from collections import defaultdict
from datetime import date, timedelta
from statistics import mean, pstdev

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def _last_date(sales):
    return max(s["sold_at"].date() for s in sales)


def recipe_map(recipes):
    m = defaultdict(list)
    for r in recipes:
        m[r["dish_id"]].append((r["ingredient_id"], r["qty"]))
    return m


def dish_cost(dish_id, recipes, ingredients):
    """Себестоимость порции = Σ (норма по техкарте × цена ингредиента)."""
    cost = {i["id"]: i["cost"] for i in ingredients}
    return round(sum(q * cost[i] for i, q in recipe_map(recipes)[dish_id]), 1)


def dashboard(sales, dishes, recipes, ingredients, days=7):
    end = _last_date(sales)
    start = end - timedelta(days=days - 1)
    prev_start = start - timedelta(days=days)
    cur = [s for s in sales if start <= s["sold_at"].date() <= end]
    prev = [s for s in sales if prev_start <= s["sold_at"].date() < start]
    rev = sum(s["price"] * s["qty"] for s in cur)
    prev_rev = sum(s["price"] * s["qty"] for s in prev) or 1
    orders = len({s["order_id"] for s in cur}) or 1
    costs = {d["id"]: dish_cost(d["id"], recipes, ingredients) for d in dishes}
    food = sum(costs[s["dish_id"]] * s["qty"] for s in cur)
    by_day = defaultdict(int)
    for s in cur:
        by_day[s["sold_at"].date()] += s["price"] * s["qty"]
    return {
        "period": f"{start:%d.%m.%Y} — {end:%d.%m.%Y}",
        "revenue": rev,
        "revenue_change_pct": round((rev - prev_rev) / prev_rev * 100, 1),
        "orders": orders,
        "avg_check": round(rev / orders),
        "food_cost_pct": round(food / rev * 100, 1) if rev else 0,
        "by_day": [{"date": d.isoformat(), "day": WEEKDAYS[d.weekday()], "revenue": v} for d, v in sorted(by_day.items())],
    }


def stock_losses(sales, usage, recipes, ingredients, days=28, threshold_pct=5.0):
    """Аудитор склада.

    Ожидаемый расход = Σ продаж × норма по техкарте.
    Перерасход = фактический расход − ожидаемый. Потеря ₸ = перерасход × цена.
    Сигнал, если перерасход больше порога (по умолчанию 5 %).
    Дополнительно ищем дни недели, где перерасход выше всего.
    """
    end = _last_date(sales)
    start = end - timedelta(days=days - 1)
    rmap = recipe_map(recipes)
    ing = {i["id"]: i for i in ingredients}
    expected = defaultdict(float)
    exp_by_wd = defaultdict(lambda: defaultdict(float))
    for s in sales:
        d = s["sold_at"].date()
        if start <= d <= end:
            for i, q in rmap[s["dish_id"]]:
                expected[i] += q * s["qty"]
                exp_by_wd[i][d.weekday()] += q * s["qty"]
    actual = defaultdict(float)
    act_by_wd = defaultdict(lambda: defaultdict(float))
    for u in usage:
        if start <= u["date"] <= end:
            actual[u["ingredient_id"]] += u["qty"]
            act_by_wd[u["ingredient_id"]][u["date"].weekday()] += u["qty"]
    result = []
    for i, exp in expected.items():
        act = actual.get(i, 0.0)
        over = act - exp
        pct = over / exp * 100 if exp else 0
        wd_over = {wd: act_by_wd[i][wd] - exp_by_wd[i][wd] for wd in range(7)}
        worst = sorted(wd_over, key=wd_over.get, reverse=True)[:2]
        result.append({
            "ingredient_id": i,
            "ingredient": ing[i]["name"],
            "unit": ing[i]["unit"],
            "expected": round(exp, 2),
            "actual": round(act, 2),
            "overuse": round(over, 2),
            "overuse_pct": round(pct, 1),
            "loss_tenge": round(max(over, 0) * ing[i]["cost"]),
            "suspicious": pct > threshold_pct,
            "worst_days": [WEEKDAYS[w] for w in worst if wd_over[w] > 0],
        })
    return sorted(result, key=lambda r: r["loss_tenge"], reverse=True)


def cashier_anomalies(cash_ops, employees, sales, days=28):
    """Аудитор кассы: удаления после пречека на 100 чеков по каждому кассиру.

    Если кассир удаляет минимум в 2 раза чаще коллег (по медиане) — сигнал для проверки.
    """
    end = max(o["created_at"].date() for o in cash_ops)
    start = end - timedelta(days=days - 1)
    emp = {e["id"]: e for e in employees}
    orders = defaultdict(set)
    for s in sales:
        if start <= s["sold_at"].date() <= end:
            orders[s["employee_id"]].add(s["order_id"])
    stats = defaultdict(lambda: {"count": 0, "amount": 0})
    for o in cash_ops:
        if start <= o["created_at"].date() <= end:
            stats[o["employee_id"]]["count"] += 1
            stats[o["employee_id"]]["amount"] += o["amount"]
    rows = []
    for eid, e in emp.items():
        if e["role"] != "Кассир":
            continue
        n_orders = len(orders[eid]) or 1
        st = stats[eid]
        rows.append({
            "employee_id": eid, "employee": e["name"], "voids": st["count"],
            "void_amount": st["amount"], "orders": n_orders,
            "per_100": round(st["count"] / n_orders * 100, 2),
        })
    rates = [r["per_100"] for r in rows]
    mu, sd = mean(rates), pstdev(rates) or 1
    for r in rows:
        others = [x["per_100"] for x in rows if x is not r] or [0]
        r["z"] = round((r["per_100"] - mu) / sd, 2)
        median_others = sorted(others)[len(others) // 2]
        r["vs_others"] = round(r["per_100"] / median_others, 1) if median_others else None
        # при двух-трёх кассирах z-оценка мало что говорит, поэтому главный критерий —
        # «в 2+ раза чаще коллег»; z-оценку показываем как дополнительную метрику
        r["suspicious"] = r["per_100"] >= 2 * median_others and r["per_100"] > 1.0
    return sorted(rows, key=lambda r: r["per_100"], reverse=True)


def forecast(sales, dishes, horizon=7, weeks=4):
    """Прогноз спроса: среднее по такому же дню недели за последние N недель × тренд.

    Тренд = продажи последних 2 недель / предыдущих 2 недель.
    """
    end = _last_date(sales)
    start = end - timedelta(days=weeks * 7 - 1)
    per = defaultdict(lambda: defaultdict(list))  # dish -> weekday -> [qty by date]
    daily = defaultdict(lambda: defaultdict(int))
    for s in sales:
        d = s["sold_at"].date()
        if start <= d <= end:
            daily[s["dish_id"]][d] += s["qty"]
    for dish_id, by_date in daily.items():
        for d, q in by_date.items():
            per[dish_id][d.weekday()].append(q)
    half = end - timedelta(days=13)
    out = []
    for dsh in dishes:
        by_date = daily[dsh["id"]]
        recent = sum(q for d, q in by_date.items() if d >= half)
        older = sum(q for d, q in by_date.items() if d < half) or 1
        trend = max(0.8, min(1.2, recent / older))
        days = []
        for k in range(1, horizon + 1):
            d = end + timedelta(days=k)
            hist = per[dsh["id"]][d.weekday()] or [0]
            days.append({"date": d.isoformat(), "day": WEEKDAYS[d.weekday()], "qty": round(mean(hist) * trend)})
        out.append({"dish_id": dsh["id"], "dish": dsh["name"], "trend": round(trend, 2),
                    "total": sum(x["qty"] for x in days), "days": days})
    return sorted(out, key=lambda r: r["total"], reverse=True)


def purchase_order(fc, recipes, ingredients, safety=0.15):
    """Заказ поставщику = прогноз × техкарта × (1 + страховой запас) − остаток."""
    rmap = recipe_map(recipes)
    need = defaultdict(float)
    for f in fc:
        for i, q in rmap[f["dish_id"]]:
            need[i] += q * f["total"]
    rows = []
    for ing in ingredients:
        n = need.get(ing["id"], 0) * (1 + safety)
        to_buy = max(0.0, n - ing["stock"])
        daily = need.get(ing["id"], 0) / 7 or 0.0001
        rows.append({
            "ingredient_id": ing["id"], "ingredient": ing["name"], "unit": ing["unit"],
            "supplier": ing["supplier"], "stock": ing["stock"], "need_week": round(n, 2),
            "days_left": round(ing["stock"] / daily, 1), "to_buy": round(to_buy, 2),
            "sum_tenge": round(to_buy * ing["cost"]),
        })
    return sorted(rows, key=lambda r: r["days_left"])


def menu_matrix(sales, dishes, recipes, ingredients, days=28):
    """Инженерия меню (метод Касаваны–Смита).

    Популярность высокая, если доля продаж ≥ 70 % от «средней доли» (1/N).
    Маржа высокая, если маржа порции ≥ средневзвешенной марже меню.
    Звезда = обе высокие; Лошадка = популярна, маржа низкая;
    Загадка = маржа высокая, продаж мало; Собака = обе низкие.
    """
    end = _last_date(sales)
    start = end - timedelta(days=days - 1)
    qty = defaultdict(int)
    for s in sales:
        if start <= s["sold_at"].date() <= end:
            qty[s["dish_id"]] += s["qty"]
    total = sum(qty.values()) or 1
    n = len(dishes)
    rows = []
    for d in dishes:
        cost = dish_cost(d["id"], recipes, ingredients)
        rows.append({"dish_id": d["id"], "dish": d["name"], "emoji": d.get("emoji", ""),
                     "price": d["price"], "cost": cost, "margin": round(d["price"] - cost),
                     "sold": qty[d["id"]], "share": qty[d["id"]] / total,
                     "food_cost_pct": round(cost / d["price"] * 100, 1)})
    avg_margin = sum(r["margin"] * r["sold"] for r in rows) / total
    pop_line = 0.7 / n
    advice = {
        "Звезда": "Держать цену и место в меню, следить за качеством.",
        "Лошадка": "Популярно, но мало зарабатывает: поднять цену на 5–10 % или удешевить техкарту.",
        "Загадка": "Выгодно, но редко берут: переставить выше в меню, рекомендовать официантам.",
        "Собака": "Убрать из меню или полностью переделать.",
    }
    for r in rows:
        hp, hm = r["share"] >= pop_line, r["margin"] >= avg_margin
        r["group"] = "Звезда" if hp and hm else "Лошадка" if hp else "Загадка" if hm else "Собака"
        r["advice"] = advice[r["group"]]
        r["share"] = round(r["share"] * 100, 1)
    return {"avg_margin": round(avg_margin), "popularity_line_pct": round(pop_line * 100, 1), "items": rows}
