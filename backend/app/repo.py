"""Заполнение базы тестовыми данными и выгрузка таблиц в списки для аналитики."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models as m
from .datagen import generate


def seed_if_empty(db: Session) -> bool:
    if db.scalar(select(func.count()).select_from(m.Dish)):
        return False
    g = generate()
    db.add_all(m.Ingredient(**i) for i in g["ingredients"])
    db.add_all(m.Dish(**{k: v for k, v in d.items() if k != "base"}) for d in g["dishes"])
    db.add_all(m.Employee(**e) for e in g["employees"])
    db.flush()
    db.add_all(m.RecipeItem(**r) for r in g["recipes"])
    db.bulk_insert_mappings(m.Sale, g["sales"])
    db.bulk_insert_mappings(m.StockUsage, g["usage"])
    db.bulk_insert_mappings(m.CashOperation, g["cash_ops"])
    db.commit()
    return True


def _rows(db, model, fields):
    return [{f: getattr(o, f) for f in fields} for o in db.scalars(select(model))]


def load(db: Session) -> dict:
    return {
        "ingredients": _rows(db, m.Ingredient, ["id", "name", "unit", "cost", "stock", "supplier"]),
        "dishes": _rows(db, m.Dish, ["id", "name", "category", "price", "emoji"]),
        "recipes": _rows(db, m.RecipeItem, ["dish_id", "ingredient_id", "qty"]),
        "employees": _rows(db, m.Employee, ["id", "name", "role"]),
        "sales": [
            {"order_id": o, "dish_id": d, "employee_id": e, "qty": q, "price": p, "shift": s, "sold_at": t}
            for o, d, e, q, p, s, t in db.execute(select(
                m.Sale.order_id, m.Sale.dish_id, m.Sale.employee_id, m.Sale.qty,
                m.Sale.price, m.Sale.shift, m.Sale.sold_at))
        ],
        "usage": [{"ingredient_id": i, "qty": q, "date": d}
                  for i, q, d in db.execute(select(m.StockUsage.ingredient_id, m.StockUsage.qty, m.StockUsage.date))],
        "cash_ops": [{"kind": k, "amount": a, "employee_id": e, "created_at": c}
                     for k, a, e, c in db.execute(select(
                         m.CashOperation.kind, m.CashOperation.amount, m.CashOperation.employee_id,
                         m.CashOperation.created_at))],
    }
