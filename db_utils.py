# AI assisted (GitHub Copilot / DeepSeek V4 Pro): debugging & seed data formatting
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
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
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
                    rating REAL DEFAULT 0.0,
                    image TEXT DEFAULT ''
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
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS customers (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT '顾客端'
                )
                """
            )
        try:
            self.connection.execute("ALTER TABLE orders ADD COLUMN rated INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            self.connection.execute("ALTER TABLE dishes ADD COLUMN image TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
        if self.count_dishes() == 0:
            self.seed_all_dishes()
            self.register_customer("顾客", "123456")

    def count_dishes(self) -> int:
        row = self.connection.execute("SELECT COUNT(*) AS count FROM dishes").fetchone()
        return int(row["count"])

    def add_dish(self, dish: Dish) -> Dish:
        try:
            with self.connection:
                cursor = self.connection.execute(
                    "INSERT INTO dishes (name, price, description, rating, image) VALUES (?, ?, ?, ?, ?)",
                    (dish.name, dish.price, dish.description, dish.rating, dish.image),
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
            "SELECT id, name, price, description, rating, image FROM dishes WHERE id = ?",
            (dish_id,),
        ).fetchone()
        if row is None:
            return None
        return Dish(id=row["id"], name=row["name"], price=row["price"], description=row["description"], rating=row["rating"], image=row["image"])

    def list_dishes(self, sort_by_rating: bool = False) -> List[Dish]:
        query = "SELECT id, name, price, description, rating, image FROM dishes"
        if sort_by_rating:
            query += " ORDER BY rating DESC, name ASC"
        else:
            query += " ORDER BY name ASC"
        rows = self.connection.execute(query).fetchall()
        return [
            Dish(id=row["id"], name=row["name"], price=row["price"], description=row["description"], rating=row["rating"], image=row["image"])
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
            "SELECT id, name, price, description, rating, image FROM dishes WHERE name LIKE ? OR description LIKE ? ORDER BY rating DESC, name ASC",
            (keyword, keyword),
        ).fetchall()
        return [
            Dish(id=row["id"], name=row["name"], price=row["price"], description=row["description"], rating=row["rating"], image=row["image"])
            for row in rows
        ]

    def is_order_rated(self, order_id: int) -> bool:
        row = self.connection.execute("SELECT rated FROM orders WHERE id = ?", (order_id,)).fetchone()
        return row is not None and bool(row["rated"])

    def mark_order_rated(self, order_id: int) -> bool:
        with self.connection:
            cursor = self.connection.execute("UPDATE orders SET rated = 1 WHERE id = ?", (order_id,))
        return cursor.rowcount > 0

    # AI assisted (GitHub Copilot / DeepSeek V4 Pro): seed data formatting
    def seed_all_dishes(self) -> int:
        dishes_data = [
            ("米饭", 2.0, "白米饭"),
            ("五香豆干", 12.0, "五香卤制，软嫩入味"),
            ("农家小炒肉", 26.0, "农家风味，香辣下饭"),
            ("凉拌海带丝", 10.0, "清爽开胃小菜"),
            ("剁椒排骨", 38.0, "剁椒蒸制，鲜辣香浓"),
            ("剁椒鱼头", 48.0, "经典湘菜，鲜辣入味"),
            ("千叶豆腐", 16.0, "软嫩Q弹，酱香浓郁"),
            ("卤鸡腿", 15.0, "卤香四溢，肉质鲜嫩"),
            ("卤鸭腿", 16.0, "秘制卤汁，香醇入味"),
            ("口水鸡", 32.0, "麻辣鲜香，回味无穷"),
            ("可乐鸡翅", 28.0, "可乐烧制，甜香可口"),
            ("台湾卤肉", 30.0, "台式风味，肥而不腻"),
            ("咖喱鸡", 30.0, "浓郁咖喱，鸡肉嫩滑"),
            ("回锅肉", 28.0, "川味经典，肥而不腻"),
            ("回锅肉2", 28.0, "回锅肉（升级版）"),
            ("土豆炒肉片", 22.0, "家常小炒，土豆绵软"),
            ("土豆烧肉", 28.0, "土豆烧肉，浓油赤酱"),
            ("土豆牛肉", 35.0, "土豆炖牛腩，软烂入味"),
            ("地三鲜", 18.0, "东北名菜，三鲜合一"),
            ("外婆菜", 16.0, "外婆的味道，咸香下饭"),
            ("外婆菜炒蛋", 18.0, "外婆菜配炒蛋"),
            ("小炒肉", 26.0, "辣椒小炒肉，经典湘味"),
            ("小炒黄牛肉", 38.0, "黄牛肉嫩滑，香辣过瘾"),
            ("干煸豆角", 16.0, "干煸入味，豆角脆嫩"),
            ("干锅包菜", 16.0, "干锅烹制，麻辣鲜香"),
            ("扁豆腊肉", 26.0, "腊肉咸香，扁豆清甜"),
            ("日本豆腐", 15.0, "嫩滑细腻，红烧风味"),
            ("有机花菜", 16.0, "有机花菜，清炒健康"),
            ("杏鲍菇", 18.0, "蚝油杏鲍菇，鲜美弹牙"),
            ("松仁玉米", 18.0, "松仁玉米，香甜可口"),
            ("梅菜扣肉", 36.0, "梅菜香浓，扣肉酥烂"),
            ("榨菜炒肉", 22.0, "榨菜爽脆，肉丝嫩滑"),
            ("毛血旺", 38.0, "麻辣鲜香，料足味浓"),
            ("毛豆炒肉", 22.0, "毛豆鲜嫩，肉片入味"),
            ("毛豆烧鸭", 30.0, "毛豆烧鸭，酱香浓郁"),
            ("毛豆虾仁", 35.0, "毛豆虾仁，鲜美清爽"),
            ("水煮肉片", 32.0, "麻辣水煮，肉片嫩滑"),
            ("水煮鱼片", 38.0, "水煮鱼片，麻辣鲜嫩"),
            ("油爆虾", 42.0, "油爆大虾，壳脆肉嫩"),
            ("清炒土豆丝", 12.0, "酸辣土豆丝，爽脆可口"),
            ("炒丝瓜", 14.0, "清炒丝瓜，鲜嫩清甜"),
            ("炒圆白菜", 12.0, "手撕包菜，酸辣爽口"),
            ("炒小油菜", 12.0, "清炒小油菜，碧绿脆嫩"),
            ("炒菜心", 14.0, "白灼菜心，鲜嫩爽口"),
            ("炒西兰花", 14.0, "蒜蓉西兰花，营养健康"),
            ("炒鱿鱼", 30.0, "爆炒鱿鱼，Q弹鲜美"),
            ("炝油麦菜", 12.0, "炝炒油麦菜，蒜香浓郁"),
            ("炝菜心", 14.0, "炝炒菜心，脆嫩爽口"),
            ("爆炒肥肠", 35.0, "爆炒肥肠，麻辣鲜香"),
            ("爆炒鸭胗", 30.0, "爆炒鸭胗，脆嫩爽口"),
            ("狮子头", 35.0, "扬州狮子头，软糯鲜美"),
            ("番茄牛肉", 38.0, "番茄炖牛腩，酸甜浓郁"),
            ("白切鸡", 30.0, "白切鸡，原汁原味"),
            ("粉蒸肉", 32.0, "粉蒸肉，软糯入味"),
            ("糖醋排骨", 36.0, "糖醋排骨，酸甜可口"),
            ("糖醋里脊", 32.0, "糖醋里脊，外酥里嫩"),
            ("糖醋里脊 (2)", 32.0, "糖醋里脊（升级版）"),
            ("红烧带鱼", 32.0, "红烧带鱼，酱香浓郁"),
            ("红烧排骨", 36.0, "红烧排骨，软烂入味"),
            ("红烧牛腩", 40.0, "红烧牛腩，浓香软烂"),
            ("红烧猪脚", 35.0, "红烧猪脚，Q弹入味"),
            ("红烧肉", 35.0, "毛氏红烧肉，肥而不腻"),
            ("红烧茄子", 16.0, "红烧茄子，软糯香甜"),
            ("红烧豆腐", 14.0, "红烧豆腐，嫩滑入味"),
            ("红烧豆腐2", 14.0, "红烧豆腐（升级版）"),
            ("红烧鸡块", 28.0, "红烧鸡块，酱香浓郁"),
            ("肉沫茄子", 22.0, "肉沫茄子，下饭神器"),
            ("肉沫荷兰豆", 24.0, "肉沫荷兰豆，清香脆嫩"),
            ("肉沫酸豆角", 22.0, "肉沫酸豆角，酸辣开胃"),
            ("脆皮烧鸭", 35.0, "脆皮烧鸭，皮脆肉嫩"),
            ("腐竹烧鸡", 28.0, "腐竹烧鸡，浓香入味"),
            ("腐竹牛腩", 40.0, "腐竹牛腩，软烂香浓"),
            ("腐竹红烧肉", 35.0, "腐竹红烧肉，层次丰富"),
            ("花生焖猪脚", 36.0, "花生焖猪脚，胶质满满"),
            ("花菜炒肉", 22.0, "花菜炒肉，家常美味"),
            ("芹菜香干", 15.0, "芹菜香干，清爽下饭"),
            ("苦瓜炒蛋", 16.0, "苦瓜炒蛋，清热降火"),
            ("莴笋肉丝", 22.0, "莴笋肉丝，清脆爽口"),
            ("蒜苔炒腊肉", 28.0, "蒜苔腊肉，咸香下饭"),
            ("蒜蓉娃娃菜", 14.0, "蒜蓉娃娃菜，鲜嫩清甜"),
            ("蒸蛋", 12.0, "蒸水蛋，嫩滑如布丁"),
            ("豆角茄子", 16.0, "豆角烧茄子，家常经典"),
            ("辣子鸡", 32.0, "辣子鸡，麻辣酥香"),
            ("酱烧排骨", 36.0, "酱烧排骨，酱香浓郁"),
            ("酸汤肥牛", 40.0, "酸汤肥牛，酸辣开胃"),
            ("酸笋肉丝", 24.0, "酸笋肉丝，酸辣爽口"),
            ("酸菜鱼", 38.0, "酸菜鱼，鲜嫩酸爽"),
            ("酸辣土豆丝", 12.0, "酸辣土豆丝，经典下饭菜"),
            ("酸辣豆芽", 10.0, "酸辣豆芽，爽脆开胃"),
            ("金针肥牛", 38.0, "金针菇肥牛，鲜嫩多汁"),
            ("雪菜", 10.0, "雪菜，咸香可口"),
            ("雪菜肉丝", 22.0, "雪菜肉丝，经典搭配"),
            ("青椒炒蛋", 16.0, "青椒炒蛋，简单美味"),
            ("青椒炒蛋2", 16.0, "青椒炒蛋（升级版）"),
            ("青椒肉丝", 24.0, "青椒肉丝，经典家常"),
            ("青豆炒肉", 22.0, "青豆炒肉，鲜嫩下饭"),
            ("青豆炒肉2", 22.0, "青豆炒肉（升级版）"),
            ("香菇滑鸡", 30.0, "香菇滑鸡，嫩滑鲜美"),
            ("香菇菜心", 18.0, "香菇菜心，清淡鲜美"),
            ("香辣牛肉", 42.0, "香辣牛肉，麻辣过瘾"),
            ("香辣鱼块", 35.0, "香辣鱼块，外酥里嫩"),
            ("鱼香肉丝", 26.0, "鱼香肉丝，酸甜微辣"),
            ("麻辣豆腐", 14.0, "麻辣豆腐，麻辣鲜香"),
            ("黄焖鸡", 30.0, "黄焖鸡，浓香四溢"),
            ("黄瓜炒蛋", 16.0, "黄瓜炒蛋，清爽可口"),
            ("黄瓜炒蛋2", 16.0, "黄瓜炒蛋（升级版）"),
            ("黑椒牛肉", 42.0, "黑椒牛肉，嫩滑多汁"),
            ("黑椒肉丸", 28.0, "黑椒肉丸，Q弹入味"),
            ("（单人餐）小炒肉+土豆丝", 28.0, "单人套餐：小炒肉+土豆丝+米饭"),
            ("（单人餐）小炒肉+青菜+汤", 30.0, "单人套餐：小炒肉+青菜+汤+米饭"),
            ("（单人餐）排骨+花菜", 30.0, "单人套餐：排骨+花菜+米饭"),
            ("（单人餐）糖醋里脊+青菜", 30.0, "单人套餐：糖醋里脊+青菜+米饭"),
            ("（单人餐）红烧肉+番茄炒蛋+汤", 32.0, "单人套餐：红烧肉+番茄炒蛋+汤+米饭"),
            ("（单人餐）肥牛+土豆丝 ", 32.0, "单人套餐：肥牛+土豆丝+米饭"),
            ("（单人餐）辣子鸡+番茄炒蛋", 30.0, "单人套餐：辣子鸡+番茄炒蛋+米饭"),
            ("（单人餐）鱼香肉丝+茄子", 28.0, "单人套餐：鱼香肉丝+茄子+米饭"),
            ("（单人餐）鸡丁+豆腐", 28.0, "单人套餐：鸡丁+豆腐+米饭"),
            ("（双人餐）口水鸡+排骨+花菜", 55.0, "双人套餐：口水鸡+排骨+花菜+米饭x2"),
            ("（双人餐）梅菜扣肉+蒸蛋+青菜", 55.0, "双人套餐：梅菜扣肉+蒸蛋+青菜+米饭x2"),
            ("（双人餐）水煮鱼片+梅菜扣肉+花菜+汤+饭", 65.0, "双人套餐：水煮鱼片+梅菜扣肉+花菜+汤+米饭x2"),
            ("（双人餐）狮子头+肥肠+豆腐+豆芽+饭", 62.0, "双人套餐：狮子头+肥肠+豆腐+豆芽+米饭x2"),
            ("（双人餐）猪脚+腐竹烧鸡+雪菜+饭", 60.0, "双人套餐：猪脚+腐竹烧鸡+雪菜+米饭x2"),
            ("（双人餐）红烧带鱼+回锅肉+青菜", 58.0, "双人套餐：红烧带鱼+回锅肉+青菜+米饭x2"),
            ("（双人餐）红烧排骨+外婆菜+青菜+汤+饭", 60.0, "双人套餐：红烧排骨+外婆菜+青菜+汤+米饭x2"),
            ("（双人餐）红烧牛肉+番茄炒蛋+土豆丝", 62.0, "双人套餐：红烧牛肉+番茄炒蛋+土豆丝+米饭x2"),
            ("（汤）冬瓜丸子汤", 12.0, "冬瓜丸子汤，清淡鲜美"),
            ("（汤）玉米排骨汤", 15.0, "玉米排骨汤，清甜滋补"),
            ("（汤）紫菜蛋汤", 8.0, "紫菜蛋花汤，简单鲜美"),
            ("（汤）茶树菇排骨汤", 15.0, "茶树菇排骨汤，鲜美滋补"),
            ("（汤）茶树菇老鸭汤", 18.0, "茶树菇老鸭汤，浓郁鲜美"),
            ("（汤）萝卜排骨汤", 14.0, "萝卜排骨汤，清甜可口"),
            ("（汤）虫草花排骨汤", 16.0, "虫草花排骨汤，滋补养生"),
            ("（汤）虫草花炖鸡汤", 16.0, "虫草花炖鸡汤，鲜美滋补"),
            ("（汤）西红柿蛋汤", 8.0, "西红柿蛋花汤，酸甜开胃"),
            ("（汤）酸辣汤", 10.0, "酸辣汤，开胃暖身"),
            ("（汤）银耳汤", 10.0, "银耳汤，清甜润肺"),
        ]
        count = 0
        for name, price, description in dishes_data:
            image = name + ".jpg"
            try:
                with self.connection:
                    self.connection.execute(
                        "INSERT OR IGNORE INTO dishes (name, price, description, image) VALUES (?, ?, ?, ?)",
                        (name, price, description, image),
                    )
                count += 1
            except sqlite3.IntegrityError:
                pass
        return count

    def register_customer(self, username: str, password: str) -> tuple[bool, str]:
        if not username or not password:
            return False, "用户名和密码不能为空"
        existing = self.connection.execute(
            "SELECT username FROM customers WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            return False, "该用户名已被注册"
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT INTO customers (username, password, role) VALUES (?, ?, '顾客端')",
                    (username, password),
                )
            return True, "注册成功"
        except sqlite3.IntegrityError:
            return False, "该用户名已被注册"

    def validate_customer(self, username: str, password: str) -> dict | None:
        row = self.connection.execute(
            "SELECT username, password, role FROM customers WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        if row is None:
            return None
        return {"username": row["username"], "role": row["role"]}

    def close(self) -> None:
        self.connection.close()
