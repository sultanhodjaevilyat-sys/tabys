"""Tabys API (FastAPI). Запуск: uvicorn app.main:app --reload"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from . import analytics as a
from . import billing
from .agent import ask
from .config import FRONTEND_URL, GEMINI_API_KEY, STRIPE_SECRET_KEY
from .db import Base, SessionLocal, engine, get_db
from .models import Subscription
from .repo import load, seed_if_empty

_cache: dict = {}


def data(db: Session) -> dict:
    """Данные для аналитики кэшируются в памяти: тестовые продажи не меняются."""
    if "d" not in _cache:
        _cache["d"] = load(db)
    return _cache["d"]


@asynccontextmanager
async def lifespan(_app):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_if_empty(db)
    yield


app = FastAPI(title="Tabys API", version="1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_URL, "http://127.0.0.1:5173"],
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"ok": True, "ai": "gemini" if GEMINI_API_KEY else "demo", "payments": "stripe" if STRIPE_SECRET_KEY else "demo"}


@app.get("/api/dashboard")
def dashboard(days: int = 7, db: Session = Depends(get_db)):
    d = data(db)
    res = a.dashboard(d["sales"], d["dishes"], d["recipes"], d["ingredients"], days)
    losses = a.stock_losses(d["sales"], d["usage"], d["recipes"], d["ingredients"])
    cash = a.cashier_anomalies(d["cash_ops"], d["employees"], d["sales"])
    res["losses_28d"] = sum(x["loss_tenge"] for x in losses if x["suspicious"]) + sum(x["void_amount"] for x in cash if x["suspicious"])
    res["alerts"] = len([x for x in losses if x["suspicious"]]) + len([x for x in cash if x["suspicious"]])
    return res


@app.get("/api/menu")
def menu(db: Session = Depends(get_db)):
    d = data(db)
    mx = {x["dish_id"]: x for x in a.menu_matrix(d["sales"], d["dishes"], d["recipes"], d["ingredients"])["items"]}
    ing = {i["id"]: i for i in d["ingredients"]}
    out = []
    for dish in d["dishes"]:
        recipe = [{"ingredient": ing[r["ingredient_id"]]["name"], "unit": ing[r["ingredient_id"]]["unit"], "qty": r["qty"],
                   "cost": round(r["qty"] * ing[r["ingredient_id"]]["cost"], 1)}
                  for r in d["recipes"] if r["dish_id"] == dish["id"]]
        out.append(dish | {"recipe": recipe, **{k: mx[dish["id"]][k] for k in ("cost", "margin", "group", "sold", "food_cost_pct", "advice")}})
    return out


@app.get("/api/audit")
def audit(db: Session = Depends(get_db)):
    d = data(db)
    return {"stock": a.stock_losses(d["sales"], d["usage"], d["recipes"], d["ingredients"]),
            "cashiers": a.cashier_anomalies(d["cash_ops"], d["employees"], d["sales"])}


@app.get("/api/forecast")
def forecast(db: Session = Depends(get_db)):
    d = data(db)
    fc = a.forecast(d["sales"], d["dishes"])
    return {"forecast": fc, "purchase_order": a.purchase_order(fc, d["recipes"], d["ingredients"])}


@app.get("/api/menu-matrix")
def menu_matrix(db: Session = Depends(get_db)):
    d = data(db)
    return a.menu_matrix(d["sales"], d["dishes"], d["recipes"], d["ingredients"])


class ChatIn(BaseModel):
    message: str
    history: list[dict] = []


@app.post("/api/agent/chat")
def agent_chat(body: ChatIn, db: Session = Depends(get_db)):
    return ask(body.message.strip()[:1000], body.history, data(db))


class CheckoutIn(BaseModel):
    plan: str
    email: str = ""


@app.get("/api/billing/plans")
def plans():
    return [{"id": k} | v for k, v in billing.PLANS.items()]


@app.post("/api/billing/checkout")
def checkout(body: CheckoutIn, db: Session = Depends(get_db)):
    return billing.create_checkout(db, body.plan, body.email.strip())


@app.get("/api/billing/verify")
def verify(session_id: str, db: Session = Depends(get_db)):
    return billing.verify(db, session_id)


@app.post("/api/billing/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    return billing.handle_webhook(db, await request.body(), request.headers.get("stripe-signature", ""))


@app.get("/api/billing/subscriptions")
def subscriptions(db: Session = Depends(get_db)):
    return [billing.serialize(s) for s in db.scalars(select(Subscription).order_by(desc(Subscription.id)).limit(20))]
