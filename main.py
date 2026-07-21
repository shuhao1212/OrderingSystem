"""
main.py —— Flask 应用入口（路由 & API 层）
============================================
本文件是整个系统的核心调度层，负责：
1. 定义所有 URL 路由（/login, /business, /customer, /api/*）
2. 处理 HTTP 请求（GET 渲染页面，POST 处理表单/API）
3. 管理登录状态（Flask session）
4. 权限控制（检查 session["role"] 防止越权访问）
5. 调用 db_utils.py 的 DatabaseManager 执行数据库操作

架构分层：
    浏览器 → main.py（路由）→ db_utils.py（数据库）→ SQLite3
                      ↕
                 models.py（数据定义）

启动方式：
    python main.py
    默认运行在 http://127.0.0.1:5000
"""

from __future__ import annotations

import os      # 文件路径操作
import uuid    # 生成唯一文件名（图片上传防重名）

from flask import (
    Flask, jsonify, redirect, render_template, request, session, url_for,
)

from db_utils import DatabaseManager  # 数据库操作类
from models import CartItem, Dish      # 数据实体类


# ==================== Flask 应用初始化 ====================

app = Flask(__name__)  # 创建 Flask 应用实例

# secret_key 用于加密 session（登录状态存储在浏览器 Cookie 中）
# 持久化到文件：服务器重启后 session 不失效，用户无需重新登录
_secret_path = os.path.join("data", ".secret_key")
if os.path.exists(_secret_path):
    with open(_secret_path, "rb") as f:
        app.secret_key = f.read()     # 读取已有密钥
else:
    app.secret_key = os.urandom(24)   # 首次运行生成随机密钥
    os.makedirs("data", exist_ok=True)
    with open(_secret_path, "wb") as f:
        f.write(app.secret_key)       # 保存到文件

# 商家唯一账号（硬编码，不可注册新的）
BUSINESS_ACCOUNT = {"password": "123456", "role": "商家端"}


# ==================== 数据库连接（懒加载单例） ====================

def get_db() -> DatabaseManager:
    """
    获取数据库管理器实例（单例模式）。
    首次调用时创建 DatabaseManager，后续直接返回缓存的实例。
    这样整个应用共用一个数据库连接，避免重复打开。
    """
    if not hasattr(app, "_db"):
        app._db = DatabaseManager("data/ordering.db")
    return app._db


# ==================== 页面路由（返回 HTML） ====================

@app.route("/")
def index() -> str:
    """
    首页：自动跳转到对应的功能页面。
    - 已登录 → 根据角色跳转到 /business 或 /customer
    - 未登录 → 跳转到 /login
    """
    if "username" in session:
        return redirect(url_for("business" if session["role"] == "商家端" else "customer"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    """
    登录页。
    GET：渲染登录表单。
    POST：验证用户名密码，分两种模式——
      - 商家端：硬编码验证（唯一账号 "商家"，密码见 BUSINESS_ACCOUNT）
      - 顾客端：查询 customers 表验证
    验证通过后，将 username 和 role 存入 session。
    """
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "")

        if not username or not password:
            error = "请输入用户名和密码"
        elif role == "商家端":
            # 商家：只有唯一账号，硬编码密码
            if username == "商家" and password == BUSINESS_ACCOUNT["password"]:
                session["username"] = username  # 存入 session
                session["role"] = role
                session["cart"] = []            # 清空购物车
                return redirect(url_for("business"))
            error = "商家账号或密码不正确"
        elif role == "顾客端":
            # 顾客：查询数据库 customers 表
            customer = get_db().validate_customer(username, password)
            if customer:
                session["username"] = username
                session["role"] = role
                session["cart"] = []
                return redirect(url_for("customer"))
            error = "用户名或密码不正确，请先注册"
    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register() -> str:
    """
    顾客注册页。
    GET：渲染注册表单。
    POST：写入 customers 表，自动登录。
    注意：不能注册 "商家" 这个用户名。
    """
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == "商家":
            error = "该用户名已被占用"
        elif not username or not password:
            error = "请输入用户名和密码"
        else:
            ok, msg = get_db().register_customer(username, password)
            if ok:
                # 注册成功直接登录
                session["username"] = username
                session["role"] = "顾客端"
                session["cart"] = []
                return redirect(url_for("customer"))
            error = msg
    return render_template("register.html", error=error)


@app.route("/logout")
def logout() -> str:
    """退出登录：清空 session，跳回登录页。"""
    session.clear()
    return redirect(url_for("login"))


@app.route("/business")
def business() -> str:
    """
    商家端主页（菜品管理）。
    权限检查：只有 role == "商家端" 的用户可以访问。
    展示全部菜品列表和添加/删除/搜索功能。
    """
    if session.get("role") != "商家端":
        return redirect(url_for("login"))  # 非商家用户重定向到登录页
    dishes = get_db().list_dishes()  # 获取全部菜品
    return render_template("business.html", dishes=dishes)


@app.route("/customer")
def customer() -> str:
    """
    顾客端主页（点餐 + 订单历史）。
    权限检查：只有 role == "顾客端" 的用户可以访问。
    准备三类数据传给模板：
    - dishes: 菜单列表（按评分降序）
    - cart_items: 购物车内容（从 session 读取）
    - orders: 当前顾客的历史订单
    """
    if session.get("role") != "顾客端":
        return redirect(url_for("login"))

    # 获取菜品，按评分从高到低排列
    dishes = get_db().list_dishes(sort_by_rating=True)

    # 从 session 中读取购物车数据，构建带详细信息的购物车列表
    cart = session.get("cart", [])  # session 中存的是 [{dish_id, quantity}, ...]
    cart_items: list[dict] = []
    total = 0.0
    for item in cart:
        dish = get_db().get_dish_by_id(item["dish_id"])
        if dish:
            subtotal = dish.price * item["quantity"]
            cart_items.append({"dish": dish, "quantity": item["quantity"], "subtotal": subtotal})
            total += subtotal

    # 获取订单，只显示当前顾客的订单
    orders_raw = get_db().list_orders()
    orders = []
    for o in orders_raw:
        if o["customer_name"] == session.get("username", ""):
            o["rated"] = get_db().is_order_rated(o["id"])  # 预计算评价状态
            orders.append(o)

    return render_template(
        "customer.html", dishes=dishes, cart_items=cart_items, total=total, orders=orders,
    )


# ==================== API 路由（商家端） ====================

@app.route("/api/dish/add", methods=["POST"])
def api_add_dish() -> str:
    """
    商家添加菜品（含图片上传）。
    返回 JSON：{"ok": True} 或 {"ok": False, "msg": "错误原因"}
    
    图片处理流程：
    1. 从 request.files 获取上传文件
    2. 校验文件扩展名（只允许 jpg/png/gif/webp）
    3. 生成 UUID 前缀防止文件名冲突
    4. 保存到 static/images/ 目录
    """
    # 权限检查：只有商家可以添加菜品
    if session.get("role") != "商家端":
        return jsonify({"ok": False, "msg": "请先登录"})

    name = request.form.get("name", "").strip()
    price_text = request.form.get("price", "").strip()
    description = request.form.get("description", "").strip()

    if not name or not price_text or not description:
        return jsonify({"ok": False, "msg": "请完整填写"})
    try:
        price = float(price_text)
    except ValueError:
        return jsonify({"ok": False, "msg": "价格必须是数字"})

    # ---- 处理图片上传 ----
    image = ""
    file = request.files.get("image")  # 获取上传的文件对象
    if file and file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower()  # 提取扩展名
        if ext in ("jpg", "jpeg", "png", "gif", "webp"):
            # UUID 前缀 + 原文件名 = 保证唯一
            image = f"{uuid.uuid4().hex[:8]}_{file.filename}"
            file.save(os.path.join("static", "images", image))

    get_db().add_dish(Dish(name=name, price=price, description=description, image=image))
    return jsonify({"ok": True})


@app.route("/api/dish/<int:dish_id>/delete", methods=["POST"])
def api_delete_dish(dish_id: int) -> str:
    """
    商家删除菜品。
    URL 中的 <int:dish_id> 会被 Flask 自动解析为整数。
    注意：不影响历史订单（订单存的是菜品快照）。
    """
    if session.get("role") != "商家端":
        return jsonify({"ok": False, "msg": "请先登录"})
    get_db().delete_dish(dish_id)
    return jsonify({"ok": True})


@app.route("/api/dish/search")
def api_search_dish() -> str:
    """
    菜品搜索 API（GET 请求）。
    参数：?q=关键词
    返回匹配菜品的 JSON 数组，供前端搜索框使用。
    不传参数或空字符串时返回全部菜品。
    """
    keyword = request.args.get("q", "").strip()
    if keyword:
        dishes = get_db().search_dishes(keyword)
    else:
        dishes = get_db().list_dishes()
    return jsonify([
        {"id": d.id, "name": d.name, "price": d.price, "rating": d.rating,
         "description": d.description, "image": d.image}
        for d in dishes
    ])


# ==================== API 路由（顾客端） ====================

@app.route("/api/cart/add", methods=["POST"])
def api_cart_add() -> str:
    """
    顾客将菜品加入购物车。
    购物车数据存在 Flask session 中（浏览器 Cookie），不写数据库。
    session["cart"] 是一个列表：[{dish_id, quantity}, ...]
    """
    if session.get("role") != "顾客端":
        return jsonify({"ok": False, "msg": "请先登录"})

    dish_id = int(request.form.get("dish_id", 0))
    quantity = int(request.form.get("quantity", 1))
    dish = get_db().get_dish_by_id(dish_id)
    if not dish or quantity <= 0:
        return jsonify({"ok": False, "msg": "参数错误"})

    cart: list = session.get("cart", [])
    cart.append({"dish_id": dish_id, "quantity": quantity})
    session["cart"] = cart  # 更新 session（Flask 会自动保存到 Cookie）
    return jsonify({"ok": True, "name": dish.name})


@app.route("/api/cart/remove/<int:index>", methods=["POST"])
def api_cart_remove(index: int) -> str:
    """从购物车中移除指定位置的菜品（按索引）。"""
    cart: list = session.get("cart", [])
    if 0 <= index < len(cart):
        cart.pop(index)
        session["cart"] = cart
    return jsonify({"ok": True})


@app.route("/api/cart/clear", methods=["POST"])
def api_cart_clear() -> str:
    """清空购物车。"""
    session["cart"] = []
    return jsonify({"ok": True})


@app.route("/api/checkout", methods=["POST"])
def api_checkout() -> str:
    """
    结账下单。
    1. 从 session 读取购物车数据
    2. 根据菜品 ID 从数据库获取最新菜品信息
    3. 计算总价
    4. 调用 save_order 写入 orders 表（含菜品快照）
    5. 清空购物车
    返回订单 ID 和总价。
    """
    if session.get("role") != "顾客端":
        return jsonify({"ok": False, "msg": "请先登录"})

    cart: list = session.get("cart", [])
    if not cart:
        return jsonify({"ok": False, "msg": "购物车为空"})

    # 构建 CartItem 列表并计算总价
    items = []
    total = 0.0
    for item in cart:
        dish = get_db().get_dish_by_id(item["dish_id"])
        if dish is None:
            continue  # 菜品已被删除，跳过
        items.append(CartItem(dish=dish, quantity=item["quantity"]))
        total += dish.price * item["quantity"]

    if not items:
        return jsonify({"ok": False, "msg": "购物车中没有有效菜品"})

    order_id = get_db().save_order(session["username"], items, total)
    session["cart"] = []  # 清空购物车
    return jsonify({"ok": True, "order_id": order_id, "total": total})


@app.route("/api/order/<int:order_id>/rate", methods=["POST"])
def api_rate_order(order_id: int) -> str:
    """
    评价订单中的菜品。
    
    评分防重复机制：
    1. 检查订单 rated 字段是否为 1 → 已评价则直接拒绝
    2. 从 orders 表中获取订单明细（含 dish_id）
    3. 逐道菜读取评分（前端传 rating_{dish_id} 参数）
    4. 调用 update_dish_rating 更新菜品评分
    5. 调用 mark_order_rated 标记订单已评价（rated=1）
    """
    if session.get("role") != "顾客端":
        return jsonify({"ok": False, "msg": "请先登录"})

    # 防重复：已评价则拒绝
    if get_db().is_order_rated(order_id):
        return jsonify({"ok": False, "msg": "该订单已评价"})

    orders = get_db().list_orders()
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return jsonify({"ok": False, "msg": "订单不存在"})

    # 逐道菜读取评分并更新
    for item_data in order["items"]:
        rating_text = request.form.get(f'rating_{item_data["dish_id"]}', "")
        if rating_text:
            try:
                rating = float(rating_text)
                if 1 <= rating <= 5:
                    get_db().update_dish_rating(item_data["dish_id"], rating)
            except ValueError:
                pass  # 非法输入忽略

    # 标记订单已评价
    get_db().mark_order_rated(order_id)
    return jsonify({"ok": True})


# ==================== 程序入口 ====================

if __name__ == "__main__":
    """
    启动 Flask 开发服务器。
    - debug=True：代码改动后自动重载，方便开发调试
    - port=5000：监听 5000 端口
    - 访问 http://127.0.0.1:5000 即可使用
    """
    app.run(debug=True, port=5000)
