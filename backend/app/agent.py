"""AI-агент «Ассистент владельца».

Как работает (tool calling):
1. Вопрос владельца + список инструментов (функций) отправляем в Gemini.
2. Модель сама решает, какую функцию вызвать (например, get_stock_losses).
3. Бэкенд выполняет функцию на данных из БД и возвращает результат модели.
4. Модель пишет понятный ответ на русском с цифрами.

Если ключа GEMINI_API_KEY нет — работает демо-режим: инструмент выбирается
по ключевым словам, а ответ собирается по шаблону. Режим честно помечается.
"""
import json

import requests

from . import analytics as a
from .config import GEMINI_API_KEY, GEMINI_MODEL

SYSTEM = (
    "Ты — AI-ассистент владельца кафе в системе Tabys (Казахстан, валюта тенге ₸). "
    "Отвечай кратко и по делу, на русском, с конкретными цифрами из инструментов. "
    "Никогда не выдумывай данные: если нужны цифры — вызови инструмент. "
    "В конце дай 1–3 практических совета. Не обвиняй сотрудников напрямую — говори «стоит проверить»."
)

TOOLS = [
    {"name": "get_dashboard", "description": "Выручка, количество чеков, средний чек, food cost % и выручка по дням за последние N дней.",
     "parameters": {"type": "OBJECT", "properties": {"days": {"type": "INTEGER", "description": "Период в днях, по умолчанию 7"}}}},
    {"name": "get_stock_losses", "description": "Аудитор склада: перерасход продуктов относительно техкарт и потери в тенге за последние 28 дней.",
     "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "get_cashier_anomalies", "description": "Аудитор кассы: удаления позиций после пречека по кассирам, подозрительные отклонения.",
     "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "get_forecast", "description": "Прогноз продаж блюд на 7 дней вперёд по дням недели.",
     "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "get_purchase_order", "description": "Готовый заказ поставщикам на неделю: что и сколько купить, на сколько дней хватит остатков.",
     "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "get_menu_matrix", "description": "Инженерия меню: блюда по группам Звезда/Лошадка/Загадка/Собака, маржа и советы.",
     "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "get_dish_info", "description": "Всё об одном блюде: цена, техкарта и себестоимость, маржа, продажи за 4 недели, прогноз на неделю, группа в матрице меню и совет.",
     "parameters": {"type": "OBJECT", "properties": {
         "dish_name": {"type": "STRING", "description": "Название блюда из меню, например «Лагман» или «Капучино»"}},
         "required": ["dish_name"]}},
]


def find_dish(name: str, dishes: list):
    """Ищем блюдо по названию без учёта регистра: «лагман» → «Лагман»."""
    q = (name or "").strip().lower()
    for d in dishes:
        if d["name"].lower() == q:
            return d
    return next((d for d in dishes if q and (q in d["name"].lower() or d["name"].lower().split()[0][:5] in q)), None)


def dish_info(name: str, data: dict) -> dict:
    s, d, r, i = data["sales"], data["dishes"], data["recipes"], data["ingredients"]
    dish = find_dish(name, d)
    if not dish:
        return {"error": f"Блюдо «{name}» не найдено", "menu": [x["name"] for x in d]}
    mx = next(x for x in a.menu_matrix(s, d, r, i)["items"] if x["dish_id"] == dish["id"])
    fc = next(x for x in a.forecast(s, d) if x["dish_id"] == dish["id"])
    ing = {x["id"]: x for x in i}
    recipe = [{"ingredient": ing[x["ingredient_id"]]["name"], "qty": x["qty"], "unit": ing[x["ingredient_id"]]["unit"],
               "cost": round(x["qty"] * ing[x["ingredient_id"]]["cost"], 1)} for x in r if x["dish_id"] == dish["id"]]
    return {"dish": dish["name"], "price": dish["price"], "cost": mx["cost"], "margin": mx["margin"],
            "food_cost_pct": mx["food_cost_pct"], "sold_28d": mx["sold"], "share_pct": mx["share"],
            "group": mx["group"], "advice": mx["advice"], "forecast_7d": fc["total"], "trend": fc["trend"],
            "recipe": recipe}


def run_tool(name: str, args: dict, data: dict):
    s, d, r, i = data["sales"], data["dishes"], data["recipes"], data["ingredients"]
    if name == "get_dashboard":
        return a.dashboard(s, d, r, i, days=int(args.get("days") or 7))
    if name == "get_stock_losses":
        return a.stock_losses(s, data["usage"], r, i)[:6]
    if name == "get_cashier_anomalies":
        return a.cashier_anomalies(data["cash_ops"], data["employees"], s)
    if name == "get_forecast":
        return [{k: v for k, v in f.items() if k != "days"} | {"by_day": {x["day"]: x["qty"] for x in f["days"]}}
                for f in a.forecast(s, d)]
    if name == "get_purchase_order":
        return [x for x in a.purchase_order(a.forecast(s, d), r, i) if x["to_buy"] > 0]
    if name == "get_menu_matrix":
        return a.menu_matrix(s, d, r, i)
    if name == "get_dish_info":
        return dish_info(args.get("dish_name", ""), data)
    return {"error": f"unknown tool {name}"}


def _gemini(contents):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": contents,
        "tools": [{"functionDeclarations": TOOLS}],
        "generationConfig": {"temperature": 0.3},
    }
    resp = requests.post(url, json=body, headers={"x-goog-api-key": GEMINI_API_KEY}, timeout=60)
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]


def ask_gemini(question: str, history: list, data: dict) -> dict:
    contents = [{"role": h["role"], "parts": [{"text": h["text"]}]} for h in history[-8:]]
    contents.append({"role": "user", "parts": [{"text": question}]})
    used = []
    for _ in range(5):  # не больше 5 шагов «подумал → вызвал инструмент»
        content = _gemini(contents)
        parts = content.get("parts", [])
        calls = [p["functionCall"] for p in parts if "functionCall" in p]
        if not calls:
            text = "".join(p.get("text", "") for p in parts).strip()
            return {"answer": text or "Не удалось получить ответ.", "tools_used": used, "mode": "gemini"}
        contents.append(content)
        responses = []
        for c in calls:
            result = run_tool(c["name"], c.get("args") or {}, data)
            used.append(c["name"])
            responses.append({"functionResponse": {"name": c["name"], "response": {"result": json.loads(json.dumps(result, default=str))}}})
        contents.append({"role": "user", "parts": responses})
    return {"answer": "Слишком много шагов, уточните вопрос.", "tools_used": used, "mode": "gemini"}


# ---------- демо-режим без ключа ----------
KEYWORDS = [
    ("get_cashier_anomalies", ["касс", "удален", "удалён", "отмен", "пречек", "сотрудник", "ворует", "кража"]),
    ("get_stock_losses", ["потер", "теря", "склад", "перерасход", "списан", "продукт"]),
    ("get_purchase_order", ["закуп", "заказ", "поставщ", "купить"]),
    ("get_forecast", ["прогноз", "спрос", "сколько прода", "будущ"]),
    ("get_menu_matrix", ["меню", "блюд", "цен", "марж", "убрать"]),
    ("get_dashboard", ["выручк", "продаж", "чек", "итог", "как дела", "food"]),
]


def _fmt(n):
    """Деньги: 106200 → «106 200»."""
    return f"{round(n):,}".replace(",", " ")


def _num(x):
    """Дробные числа по-русски: 26.55 → «26,55»."""
    return f"{x:g}".replace(".", ",")


def _plural(n, one, few, many):
    """1 удаление, 2 удаления, 5 удалений."""
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def ask_demo(question: str, data: dict) -> dict:
    q = question.lower()
    dish = next((x for x in data["dishes"] if x["name"].lower().split()[0][:5] in q), None)
    if dish:  # вопрос про конкретное блюдо → инструмент с параметром
        res = run_tool("get_dish_info", {"dish_name": dish["name"]}, data)
        recipe = ", ".join(f"{x['ingredient'].lower()} {_num(x['qty'])} {x['unit']}" for x in res["recipe"])
        answer = (f"{res['dish']}: цена {_fmt(res['price'])} ₸, себестоимость {_fmt(res['cost'])} ₸ "
                  f"(food cost {_num(res['food_cost_pct'])} %), маржа {_fmt(res['margin'])} ₸ с порции.\n"
                  f"Техкарта: {recipe}.\n"
                  f"Продано за 4 недели: {res['sold_28d']} {_plural(res['sold_28d'], 'порция', 'порции', 'порций')}, "
                  f"прогноз на неделю — {res['forecast_7d']}.\n"
                  f"Группа в матрице меню: {res['group']}. Совет: {res['advice']}")
        return {"answer": answer, "tools_used": ["get_dish_info"], "mode": "demo"}
    tools = [t for t, words in KEYWORDS if any(w in q for w in words)] or ["get_dashboard", "get_stock_losses"]
    if any(w in q for w in ["потер", "теря", "кража", "ворует"]):  # общий вопрос о потерях = склад + касса
        tools = ["get_stock_losses", "get_cashier_anomalies"]
    tools = tools[:2]
    lines = []
    for t in tools:
        res = run_tool(t, {}, data)
        if t == "get_dashboard":
            lines.append(f"За {res['period']}: выручка {_fmt(res['revenue'])} ₸ ({'+' if res['revenue_change_pct'] > 0 else ''}{_num(res['revenue_change_pct'])} % к прошлой неделе), "
                         f"{res['orders']} {_plural(res['orders'], 'чек', 'чека', 'чеков')}, средний чек {_fmt(res['avg_check'])} ₸, "
                         f"food cost {_num(res['food_cost_pct'])} %.")
        elif t == "get_stock_losses":
            bad = [x for x in res if x["suspicious"]]
            if bad:
                for x in bad:
                    lines.append(f"⚠️ {x['ingredient']}: перерасход {_num(x['overuse'])} {x['unit']} (+{_num(x['overuse_pct'])} %) ≈ {_fmt(x['loss_tenge'])} ₸ за 4 недели, "
                                 f"чаще всего — {', '.join(x['worst_days'])}. Стоит проверить вечерние смены и выход порций.")
            else:
                lines.append("Перерасхода выше 5 % не найдено.")
        elif t == "get_cashier_anomalies":
            for x in res:
                if x["suspicious"]:
                    lines.append(f"⚠️ Кассир {x['employee']}: {x['voids']} {_plural(x['voids'], 'удаление', 'удаления', 'удалений')} "
                                 f"после пречека на {_fmt(x['void_amount'])} ₸ — в {_num(x['vs_others'])} раза чаще коллег. "
                                 "Стоит проверить чеки и камеры.")
            if not any(x["suspicious"] for x in res):
                lines.append("Подозрительных отклонений на кассе нет.")
        elif t == "get_forecast":
            top = res[:3]
            lines.append("Прогноз на 7 дней: " + "; ".join(f"{f['dish']} — {f['total']} {_plural(f['total'], 'порция', 'порции', 'порций')}" for f in top) + ".")
        elif t == "get_purchase_order":
            total = sum(x["sum_tenge"] for x in res)
            lines.append("Заказ поставщикам: " + "; ".join(f"{x['ingredient']} {_num(x['to_buy'])} {x['unit']}" for x in res[:5]) +
                         f". Итого ≈ {_fmt(total)} ₸.")
        elif t == "get_menu_matrix":
            groups = {}
            for x in res["items"]:
                groups.setdefault(x["group"], []).append(x["dish"])
            lines.append(" ".join(f"{g}: {', '.join(v)}." for g, v in groups.items()))
            lines.append("Совет: «Лошадкам» поднять цену на 5–10 %, «Собак» убрать или переделать.")
    return {"answer": "\n".join(lines), "tools_used": tools, "mode": "demo"}


def ask(question: str, history: list, data: dict) -> dict:
    if GEMINI_API_KEY:
        try:
            return ask_gemini(question, history, data)
        except Exception as e:  # сеть, лимит, неверный ключ — не роняем чат
            res = ask_demo(question, data)
            res["answer"] = f"(Gemini недоступен: {type(e).__name__}. Ответ в демо-режиме.)\n" + res["answer"]
            return res
    return ask_demo(question, data)
