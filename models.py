from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Dish:
    name: str
    price: float
    description: str
    rating: float = 0.0
    image: str = ""
    id: int | None = None


@dataclass
class User:
    username: str
    password: str
    role: str


@dataclass
class CartItem:
    dish: Dish
    quantity: int = 1


@dataclass
class Order:
    customer_name: str
    items: List[CartItem] = field(default_factory=list)
    total_price: float = 0.0
    created_at: str = ""
    id: int | None = None
