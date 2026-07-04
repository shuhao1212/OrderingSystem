from __future__ import annotations

import json
import os
import sqlite3
from typing import List, Optional

from models import CartItem, Dish


class DatabaseManager:
    def __init__(self, db_path: str = "data/ordering.db") -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.initialize()

    def initialize(self) -> None:
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS dishes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    price REAL NOT NULL,
                    description TEXT,
                    rating REAL DEFAULT 0.0
                )
                """
            )
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    items TEXT NOT NULL,
                    total_price REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    rated INTEGER DEFAULT 0
                )
                """
            )
        try:
            self.connection.execute("ALTER TABLE orders ADD COLUMN rated INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        if self.count_dishes() == 0:
            self.add_dish(Dish(name="宫保鸡丁", price=28.0, description="经典川味，酸甜微辣"))
            self.add_dish(Dish(name="番茄鸡蛋面", price=18.0, description="家常汤面，暖胃好吃"))
            self.add_dish(Dish(name="牛肉汉堡", price=35.0, description="酥脆面包搭配嫩牛肉"))

    def count_dishes(self) -> int:
        row = self.connection.execute("SELECT COUNT(*) AS count FROM dishes").fetchone()
        return int(row["count"])

    def add_dish(self, dish: Dish) -> Dish:
        try:
            with self.connection:
                cursor = self.connection.execute(
                    "INSERT INTO dishes (name, price, description, rating) VALUES (?, ?, ?, ?)",
                    (dish.name, dish.price, dish.description, dish.rating),
                )
            dish.id = cursor.lastrowid
            return dish
        except sqlite3.IntegrityError:
            return dish

    def delete_dish(self, dish_id: int) -> bool:
        with self.connection:
            cursor = self.connection.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
        return cursor.rowcount > 0

    def get_dish_by_id(self, dish_id: int) -> Optional[Dish]:
        row = self.connection.execute(
            "SELECT id, name, price, description, rating FROM dishes WHERE id = ?",
            (dish_id,),
        ).fetchone()
        if row is None:
            return None
        return Dish(id=row["id"], name=row["name"], price=row["price"], description=row["description"], rating=row["rating"])

    def list_dishes(self, sort_by_rating: bool = False) -> List[Dish]:
        query = "SELECT id, name, price, description, rating FROM dishes"
        if sort_by_rating:
            query += " ORDER BY rating DESC, name ASC"
        else:
            query += " ORDER BY name ASC"
        rows = self.connection.execute(query).fetchall()
        return [
            Dish(id=row["id"], name=row["name"], price=row["price"], description=row["description"], rating=row["rating"])
            for row in rows
        ]

    def update_dish_rating(self, dish_id: int, rating: float) -> bool:
        with self.connection:
            cursor = self.connection.execute(
                "UPDATE dishes SET rating = ? WHERE id = ?",
                (rating, dish_id),
            )
        return cursor.rowcount > 0

    def save_order(self, customer_name: str, items: List[CartItem], total_price: float) -> int:
        payload = [
            {
                "dish_id": item.dish.id,
                "dish_name": item.dish.name,
                "quantity": item.quantity,
                "unit_price": item.dish.price,
            }
            for item in items
        ]
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO orders (customer_name, items, total_price, created_at) VALUES (?, ?, ?, datetime('now'))",
                (customer_name, json.dumps(payload, ensure_ascii=False), total_price),
            )
        return cursor.lastrowid

    def list_orders(self) -> List[dict]:
        rows = self.connection.execute(
            "SELECT id, customer_name, items, total_price, created_at FROM orders ORDER BY id DESC"
        ).fetchall()
        return [
            {
                "id": row["id"],
                "customer_name": row["customer_name"],
                "items": json.loads(row["items"]),
                "total_price": row["total_price"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def search_dishes(self, keyword: str) -> List[Dish]:
        keyword = f"%{keyword}%"
        rows = self.connection.execute(
            "SELECT id, name, price, description, rating FROM dishes WHERE name LIKE ? OR description LIKE ? ORDER BY rating DESC, name ASC",
            (keyword, keyword),
        ).fetchall()
        return [
            Dish(id=row["id"], name=row["name"], price=row["price"], description=row["description"], rating=row["rating"])
            for row in rows
        ]

    def is_order_rated(self, order_id: int) -> bool:
        row = self.connection.execute("SELECT rated FROM orders WHERE id = ?", (order_id,)).fetchone()
        return row is not None and bool(row["rated"])

    def mark_order_rated(self, order_id: int) -> bool:
        with self.connection:
            cursor = self.connection.execute("UPDATE orders SET rated = 1 WHERE id = ?", (order_id,))
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()
