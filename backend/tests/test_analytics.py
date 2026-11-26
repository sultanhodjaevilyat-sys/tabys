"""Тесты модуля «Интеллект». Запуск из папки backend:  python -m unittest -v
(работают и через pytest). Не нужны ни БД, ни сеть — только генератор данных.
"""
import unittest
from datetime import date, datetime

from app import analytics as a
from app.agent import ask_demo
from app.datagen import generate

DATA = generate(today=date(2026, 11, 26))


class TestDishCost(unittest.TestCase):
    def test_cost_is_sum_of_recipe(self):
        # Бешбармак: 0.25 кг говядины × 4000 + 0.10 кг муки × 350 + 0.05 кг лука × 200
        self.assertAlmostEqual(a.dish_cost(1, DATA["recipes"], DATA["ingredients"]), 1000 + 35 + 10, places=1)


class TestStockLosses(unittest.TestCase):
    def test_finds_beef_overuse_on_tue_thu(self):
        res = a.stock_losses(DATA["sales"], DATA["usage"], DATA["recipes"], DATA["ingredients"])
        beef = next(x for x in res if x["ingredient"] == "Говядина")
        self.assertTrue(beef["suspicious"])
        self.assertGreater(beef["overuse_pct"], 5)
        self.assertEqual(set(beef["worst_days"]), {"Вт", "Чт"})

    def test_normal_products_are_not_flagged(self):
        res = a.stock_losses(DATA["sales"], DATA["usage"], DATA["recipes"], DATA["ingredients"])
        flagged = [x["ingredient"] for x in res if x["suspicious"]]
        self.assertEqual(flagged, ["Говядина"])

    def test_handmade_example(self):
        # 10 продаж блюда с нормой 0.2 кг → ожидаем 2 кг, факт 2.5 кг → +25 %
        sales = [{"dish_id": 1, "qty": 1, "sold_at": datetime(2026, 1, 5, 12), "order_id": i} for i in range(10)]
        usage = [{"ingredient_id": 1, "qty": 2.5, "date": date(2026, 1, 5)}]
        res = a.stock_losses(sales, usage, [{"dish_id": 1, "ingredient_id": 1, "qty": 0.2}],
                             [{"id": 1, "name": "X", "unit": "кг", "cost": 1000, "stock": 0, "supplier": ""}])
        self.assertAlmostEqual(res[0]["overuse_pct"], 25.0)
        self.assertEqual(res[0]["loss_tenge"], 500)


class TestCashier(unittest.TestCase):
    def test_flags_only_suspicious_cashier(self):
        res = a.cashier_anomalies(DATA["cash_ops"], DATA["employees"], DATA["sales"])
        flagged = [x["employee"] for x in res if x["suspicious"]]
        self.assertEqual(flagged, ["Ерлан"])


class TestForecast(unittest.TestCase):
    def test_seven_days_non_negative(self):
        fc = a.forecast(DATA["sales"], DATA["dishes"])
        self.assertEqual(len(fc), len(DATA["dishes"]))
        for f in fc:
            self.assertEqual(len(f["days"]), 7)
            self.assertTrue(all(d["qty"] >= 0 for d in f["days"]))
            self.assertTrue(0.8 <= f["trend"] <= 1.2)

    def test_weekend_is_busier(self):
        fc = {f["dish"]: f for f in a.forecast(DATA["sales"], DATA["dishes"])}
        days = {d["day"]: d["qty"] for d in fc["Капучино"]["days"]}
        self.assertGreater(days["Сб"], days["Пн"])

    def test_purchase_order_never_negative(self):
        po = a.purchase_order(a.forecast(DATA["sales"], DATA["dishes"]), DATA["recipes"], DATA["ingredients"])
        self.assertTrue(all(x["to_buy"] >= 0 for x in po))


class TestMenuMatrix(unittest.TestCase):
    def test_every_dish_gets_a_group(self):
        mx = a.menu_matrix(DATA["sales"], DATA["dishes"], DATA["recipes"], DATA["ingredients"])
        groups = {x["group"] for x in mx["items"]}
        self.assertTrue(groups <= {"Звезда", "Лошадка", "Загадка", "Собака"})
        self.assertEqual(len(mx["items"]), len(DATA["dishes"]))
        self.assertAlmostEqual(sum(x["share"] for x in mx["items"]), 100, delta=0.5)


class TestAgentDemo(unittest.TestCase):
    def test_losses_question_uses_both_auditors(self):
        r = ask_demo("Где я теряю деньги?", DATA)
        self.assertEqual(r["tools_used"], ["get_stock_losses", "get_cashier_anomalies"])
        self.assertIn("Говядина", r["answer"])
        self.assertIn("Ерлан", r["answer"])

    def test_russian_number_format(self):
        r = ask_demo("Где я теряю деньги?", DATA)
        self.assertIn("26,55 кг", r["answer"])        # запятая, а не точка
        self.assertIn("93 удаления", r["answer"])     # правильное окончание

    def test_plural(self):
        from app.agent import _plural
        forms = ("удаление", "удаления", "удалений")
        self.assertEqual([_plural(n, *forms) for n in (1, 2, 5, 11, 21, 93, 112)],
                         ["удаление", "удаления", "удалений", "удалений", "удаление", "удаления", "удалений"])

    def test_purchase_question(self):
        r = ask_demo("Что заказать поставщику?", DATA)
        self.assertIn("get_purchase_order", r["tools_used"])


if __name__ == "__main__":
    unittest.main()
