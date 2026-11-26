"""Интеграционные тесты API: поднимают FastAPI с временной SQLite-базой.
Нужны пакеты из requirements.txt + httpx. Если их нет — тесты пропускаются.
Запуск из папки backend:  python -m unittest -v
"""
import os
import tempfile
import unittest

try:
    _tmp = tempfile.mkdtemp()
    os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
    os.environ["GEMINI_API_KEY"] = ""
    os.environ["STRIPE_SECRET_KEY"] = ""
    from fastapi.testclient import TestClient

    from app.main import app
    HAVE_DEPS = True
except ImportError:  # fastapi/sqlalchemy/httpx не установлены
    HAVE_DEPS = False


@unittest.skipUnless(HAVE_DEPS, "нужны fastapi, sqlalchemy, httpx")
class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = TestClient(app)
        cls.client = cls.ctx.__enter__()  # запускает lifespan: создание таблиц и seed

    @classmethod
    def tearDownClass(cls):
        cls.ctx.__exit__(None, None, None)

    def test_health(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["ai"], "demo")

    def test_dashboard(self):
        d = self.client.get("/api/dashboard").json()
        self.assertGreater(d["revenue"], 0)
        self.assertEqual(len(d["by_day"]), 7)
        self.assertGreaterEqual(d["alerts"], 2)

    def test_menu_has_recipes(self):
        menu = self.client.get("/api/menu").json()
        self.assertEqual(len(menu), 12)
        self.assertTrue(all(m["recipe"] for m in menu))

    def test_audit_and_forecast(self):
        audit = self.client.get("/api/audit").json()
        self.assertTrue(any(x["suspicious"] for x in audit["stock"]))
        fc = self.client.get("/api/forecast").json()
        self.assertIn("purchase_order", fc)

    def test_agent_demo(self):
        r = self.client.post("/api/agent/chat", json={"message": "Где я теряю деньги?", "history": []}).json()
        self.assertEqual(r["mode"], "demo")
        self.assertIn("Говядина", r["answer"])

    def test_billing_demo_flow(self):
        plans = self.client.get("/api/billing/plans").json()
        self.assertEqual([p["id"] for p in plans], ["start", "business", "network"])
        r = self.client.post("/api/billing/checkout", json={"plan": "business", "email": "owner@cafe.kz"}).json()
        self.assertEqual(r["mode"], "demo")
        sid = r["url"].split("session_id=")[1]
        sub = self.client.get("/api/billing/verify", params={"session_id": sid}).json()
        self.assertEqual(sub["status"], "active")

    def test_billing_rejects_unknown_plan(self):
        r = self.client.post("/api/billing/checkout", json={"plan": "free-forever"})
        self.assertEqual(r.status_code, 400)

    def test_webhook_without_secret_is_rejected(self):
        r = self.client.post("/api/billing/webhook", content=b"{}", headers={"stripe-signature": "x"})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
