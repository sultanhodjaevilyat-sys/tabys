"""PaySystem: подписка на Tabys через Stripe Checkout (тестовый режим).

Поток оплаты:
1. Фронтенд → POST /api/billing/checkout {plan, email}
2. Бэкенд создаёт Checkout Session в Stripe (mode=subscription) и сохраняет запись
   Subscription со статусом pending.
3. Пользователь платит на странице Stripe тестовой картой 4242 4242 4242 4242.
4. Stripe присылает webhook checkout.session.completed → статус active.
   Локально без Stripe CLI webhook не дойдёт, поэтому страница успеха дополнительно
   вызывает /api/billing/verify, и бэкенд сам спрашивает Stripe о статусе сессии.

Без STRIPE_SECRET_KEY работает демо-режим (без перехода в Stripe), он помечается mode=demo.
"""
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import FRONTEND_URL, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from .models import Subscription

PLANS = {
    "start": {"name": "Tabys Старт", "price": 9900, "features": ["Касса и меню", "Склад и техкарты", "1 точка"]},
    "business": {"name": "Tabys Бизнес", "price": 19900, "features": ["Всё из Старт", "Аудитор потерь", "Прогноз и автозаказ", "AI-ассистент"]},
    "network": {"name": "Tabys Сеть", "price": 49900, "features": ["Всё из Бизнес", "До 10 точек", "Импорт из iiko / Paloma / Rosta"]},
}


def _stripe():
    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe


def create_checkout(db: Session, plan: str, email: str) -> dict:
    if plan not in PLANS:
        raise HTTPException(400, "Неизвестный тариф")
    p = PLANS[plan]
    if not STRIPE_SECRET_KEY:
        sid = "demo_" + uuid.uuid4().hex[:16]
        db.add(Subscription(plan=plan, email=email, status="pending", mode="demo", stripe_session_id=sid))
        db.commit()
        return {"url": f"{FRONTEND_URL}/billing/success?session_id={sid}", "mode": "demo"}
    stripe = _stripe()
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_email=email or None,
        line_items=[{
            "quantity": 1,
            "price_data": {
                "currency": "kzt",
                "unit_amount": p["price"] * 100,  # Stripe считает в тиынах
                "recurring": {"interval": "month"},
                "product_data": {"name": p["name"]},
            },
        }],
        metadata={"plan": plan},
        success_url=f"{FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{FRONTEND_URL}/pricing?canceled=1",
    )
    db.add(Subscription(plan=plan, email=email, status="pending", mode="stripe", stripe_session_id=session.id))
    db.commit()
    return {"url": session.url, "mode": "stripe"}


def _get(db, session_id) -> Subscription:
    sub = db.scalar(select(Subscription).where(Subscription.stripe_session_id == session_id))
    if not sub:
        raise HTTPException(404, "Сессия оплаты не найдена")
    return sub


def verify(db: Session, session_id: str) -> dict:
    sub = _get(db, session_id)
    if sub.mode == "demo":
        sub.status = "active"
    elif sub.status != "active":
        s = _stripe().checkout.Session.retrieve(session_id)
        if s.status == "complete" and s.payment_status in ("paid", "no_payment_required"):
            sub.status = "active"
            sub.stripe_subscription_id = s.subscription or ""
    db.commit()
    return serialize(sub)


def handle_webhook(db: Session, payload: bytes, signature: str) -> dict:
    stripe = _stripe()
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(400, "STRIPE_WEBHOOK_SECRET не задан")
    try:
        event = stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(400, "Неверная подпись webhook")
    obj = event["data"]["object"]
    if event["type"] == "checkout.session.completed":
        sub = db.scalar(select(Subscription).where(Subscription.stripe_session_id == obj["id"]))
        if sub:  # повторный webhook ничего не ломает: статус просто остаётся active
            sub.status = "active"
            sub.stripe_subscription_id = obj.get("subscription") or ""
    elif event["type"] == "customer.subscription.deleted":
        sub = db.scalar(select(Subscription).where(Subscription.stripe_subscription_id == obj["id"]))
        if sub:
            sub.status = "canceled"
    db.commit()
    return {"received": True}


def serialize(sub: Subscription) -> dict:
    return {"id": sub.id, "plan": sub.plan, "plan_name": PLANS[sub.plan]["name"], "email": sub.email,
            "status": sub.status, "mode": sub.mode, "created_at": sub.created_at.isoformat()}
