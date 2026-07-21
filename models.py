"""
models.py —— 数据模型定义
============================
本文件定义了订餐系统中所有的核心数据结构（实体类）。
使用 Python 的 dataclass 装饰器，可以自动生成 __init__、__repr__ 等方法，
使代码更简洁、类型更清晰。

四个实体类：
- Dish   : 菜品（对应数据库 dishes 表）
- User   : 用户（用于登录验证）
- CartItem : 购物车条目（顾客选菜时的临时数据）
- Order  : 订单（对应数据库 orders 表）
"""

from __future__ import annotations  # 允许在类型注解中使用类名本身（如 Dish 内部引用 Dish）

from dataclasses import dataclass, field  # dataclass: 自动生成构造方法；field: 定义默认值
from typing import List                   # List 类型注解


@dataclass
class Dish:
    """
    菜品实体类
    ----------
    对应数据库中的 dishes 表，每个字段和表的列一一对应。
    顾客浏览菜单、商家管理菜品时，数据都以 Dish 对象的形式传递。

    字段说明：
    - name        : 菜名（在数据库中是 UNIQUE 约束，不能重名）
    - price       : 单价（单位：元）
    - description : 菜品介绍（一句话描述口味、做法等）
    - rating      : 平均评分（0.0 ~ 5.0，顾客评价后更新，默认 0.0 表示暂无评分）
    - image       : 图片文件名（例如 "宫保鸡丁.jpg"，图片存在 static/images/ 下）
    - id          : 数据库自增主键（None 表示还未存入数据库，保存后由 SQLite 自动赋值）
    """
    name: str
    price: float
    description: str
    rating: float = 0.0        # 默认 0.0，新菜还没有人评分
    image: str = ""            # 默认空字符串，没有图片也可以
    id: int | None = None      # | None 表示可以为空（未保存到数据库时就是 None）


@dataclass
class User:
    """
    用户实体类
    ----------
    用于登录验证。商家只有一个硬编码账号，顾客注册后存入 customers 表。

    字段说明：
    - username : 用户名（商家端固定为 "商家"，顾客端由用户注册时自定）
    - password : 密码（明文存储，实际项目中应使用哈希加密）
    - role     : 角色（"商家端" 或 "顾客端"，用于权限控制）
    """
    username: str
    password: str
    role: str


@dataclass
class CartItem:
    """
    购物车条目类
    ------------
    每个 CartItem 代表购物车中的一道菜及数量。
    购物车存在 Flask session 中（浏览器 Cookie），不会写入数据库。

    字段说明：
    - dish     : 菜品对象（包含名称、价格等信息）
    - quantity : 购买数量（默认 1，顾客可自行调整）
    """
    dish: Dish
    quantity: int = 1


@dataclass
class Order:
    """
    订单实体类
    ----------
    对应数据库中的 orders 表。结账时创建，持久化存储。
    注意：目前代码中订单以字典形式传递，此 dataclass 作为类型定义保留。

    字段说明：
    - customer_name : 下单顾客的用户名
    - items         : 订单中的菜品列表（CartItem 列表）
    - total_price   : 订单总价（自动计算）
    - created_at    : 下单时间（数据库自动生成 datetime('now')）
    - id            : 数据库自增主键
    """
    customer_name: str
    items: List[CartItem] = field(default_factory=list)  # 默认空列表
    total_price: float = 0.0
    created_at: str = ""
    id: int | None = None
    total_price: float = 0.0
    created_at: str = ""
    id: int | None = None
