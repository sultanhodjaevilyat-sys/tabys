"""Таблицы базы данных Tabys (SQLAlchemy 2.0).

Связи:
  Dish 1—N RecipeItem N—1 Ingredient   (техкарта: многие-ко-многим через RecipeItem)
  Dish 1—N Sale N—1 Employee           (продажи)
  Ingredient 1—N StockUsage            (фактический расход склада)
  Employee 1—N CashOperation           (удаления, скидки на кассе)
  Subscription                         (подписка на Tabys через Stripe)
"""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Ingredient(Base):
    __tablename__ = "ingredients"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    unit: Mapped[str] = mapped_column(String(10))
    cost: Mapped[float] = mapped_column(Float)          # цена за единицу, ₸
    stock: Mapped[float] = mapped_column(Float)         # остаток на складе
    supplier: Mapped[str] = mapped_column(String(80))


class Dish(Base):
    __tablename__ = "dishes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    category: Mapped[str] = mapped_column(String(40))
    price: Mapped[int] = mapped_column(Integer)
    emoji: Mapped[str] = mapped_column(String(8), default="")
    recipe: Mapped[list["RecipeItem"]] = relationship(back_populates="dish", cascade="all, delete-orphan")


class RecipeItem(Base):
    __tablename__ = "recipe_items"
    __table_args__ = (UniqueConstraint("dish_id", "ingredient_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id", ondelete="CASCADE"), index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), index=True)
    qty: Mapped[float] = mapped_column(Float)           # норма на 1 порцию
    dish: Mapped[Dish] = relationship(back_populates="recipe")
    ingredient: Mapped[Ingredient] = relationship()


class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    role: Mapped[str] = mapped_column(String(30))


class Sale(Base):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, index=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"), index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    qty: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)
    shift: Mapped[str] = mapped_column(String(10))
    sold_at: Mapped[datetime] = mapped_column(DateTime, index=True)


class StockUsage(Base):
    __tablename__ = "stock_usage"
    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), index=True)
    qty: Mapped[float] = mapped_column(Float)
    date: Mapped[date] = mapped_column(Date, index=True)


class CashOperation(Base):
    __tablename__ = "cash_operations"
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(40))
    amount: Mapped[int] = mapped_column(Integer)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    plan: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | active | canceled
    mode: Mapped[str] = mapped_column(String(10), default="stripe")     # stripe | demo
    stripe_session_id: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)  # локальное время сервера
