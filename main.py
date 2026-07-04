from __future__ import annotations

import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from db_utils import DatabaseManager
from models import CartItem, Dish

app = Flask(__name__)
_secret_path = os.path.join("data", ".secret_key")
if os.path.exists(_secret_path):
    with open(_secret_path, "rb") as f:
        app.secret_key = f.read()
else:
    app.secret_key = os.urandom(24)
    os.makedirs("data", exist_ok=True)
    with open(_secret_path, "wb") as f:
        f.write(app.secret_key)

BUSINESS_ACCOUNT = {"password": "123456", "role": "商家端"}


def get_db() -> DatabaseManager:
    if not hasattr(app, "_db"):
        app._db = DatabaseManager("data/ordering.db")
    return app._db


@app.route("/")
def index() -> str:
    if "username" in session:
        return redirect(url_for("business" if session["role"] == "商家端" else "customer"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "")
        if not username or not password:
            error = "请输入用户名和密码"
        elif role == "商家端":
            if username == "商家" and password == BUSINESS_ACCOUNT["password"]:
                session["username"] = username
                session["role"] = role
                session["cart"] = []
                return redirect(url_for("business"))
            error = "商家账号或密码不正确"
        elif role == "顾客端":
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
                session["username"] = username
                session["role"] = "顾客端"
                session["cart"] = []
                return redirect(url_for("customer"))
            error = msg
    return render_template("register.html", error=error)


@app.route("/logout")
def logout() -> str:
    session.clear()
    return redirect(url_for("login"))


@app.route("/business")
def business() -> str:
    if session.get("role") != "商家端":
        return redirect(url_for("login"))
    dishes = get_db().list_dishes()
    return render_template("business.html", dishes=dishes)


@app.route("/customer")
def customer() -> str:
    if session.get("role") != "顾客端":
        return redirect(url_for("login"))
    dishes = get_db().list_dishes(sort_by_rating=True)
    cart = session.get("cart", [])
    cart_items: list[dict] = []
    total = 0.0
    for item in cart:
        dish = get_db().get_dish_by_id(item["dish_id"])
        if dish:
            subtotal = dish.price * item["quantity"]
            cart_items.append({"dish": dish, "quantity": item["quantity"], "subtotal": subtotal})
            total += subtotal
    orders_raw = get_db().list_orders()
    orders = []
    for o in orders_raw:
        if o["customer_name"] == session.get("username", ""):
            o["rated"] = get_db().is_order_rated(o["id"])
            orders.append(o)
    return render_template(
        "customer.html", dishes=dishes, cart_items=cart_items, total=total, orders=orders
    )


# ---- API: 商家操作 ----

@app.route("/api/dish/add", methods=["POST"])
def api_add_dish() -> str:
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

    image = ""
    file = request.files.get("image")
    if file and file.filename:
        import uuid
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext in ("jpg", "jpeg", "png", "gif", "webp"):
            image = f"{uuid.uuid4().hex[:8]}_{file.filename}"
            file.save(os.path.join("static", "images", image))

    get_db().add_dish(Dish(name=name, price=price, description=description, image=image))
    return jsonify({"ok": True})


@app.route("/api/dish/<int:dish_id>/delete", methods=["POST"])
def api_delete_dish(dish_id: int) -> str:
    if session.get("role") != "商家端":
        return jsonify({"ok": False, "msg": "请先登录"})
    get_db().delete_dish(dish_id)
    return jsonify({"ok": True})


@app.route("/api/dish/search")
def api_search_dish() -> str:
    keyword = request.args.get("q", "").strip()
    if keyword:
        dishes = get_db().search_dishes(keyword)
    else:
        dishes = get_db().list_dishes()
    return jsonify([
        {"id": d.id, "name": d.name, "price": d.price, "rating": d.rating, "description": d.description, "image": d.image}
        for d in dishes
    ])


# ---- API: 顾客操作 ----

@app.route("/api/cart/add", methods=["POST"])
def api_cart_add() -> str:
    if session.get("role") != "顾客端":
        return jsonify({"ok": False, "msg": "请先登录"})
    dish_id = int(request.form.get("dish_id", 0))
    quantity = int(request.form.get("quantity", 1))
    dish = get_db().get_dish_by_id(dish_id)
    if not dish or quantity <= 0:
        return jsonify({"ok": False, "msg": "参数错误"})
    cart: list = session.get("cart", [])
    cart.append({"dish_id": dish_id, "quantity": quantity})
    session["cart"] = cart
    return jsonify({"ok": True, "name": dish.name})


@app.route("/api/cart/remove/<int:index>", methods=["POST"])
def api_cart_remove(index: int) -> str:
    cart: list = session.get("cart", [])
    if 0 <= index < len(cart):
        cart.pop(index)
        session["cart"] = cart
    return jsonify({"ok": True})


@app.route("/api/cart/clear", methods=["POST"])
def api_cart_clear() -> str:
    session["cart"] = []
    return jsonify({"ok": True})


@app.route("/api/checkout", methods=["POST"])
def api_checkout() -> str:
    if session.get("role") != "顾客端":
        return jsonify({"ok": False, "msg": "请先登录"})
    cart: list = session.get("cart", [])
    if not cart:
        return jsonify({"ok": False, "msg": "购物车为空"})
    items = []
    total = 0.0
    for item in cart:
        dish = get_db().get_dish_by_id(item["dish_id"])
        if dish is None:
            continue
        items.append(CartItem(dish=dish, quantity=item["quantity"]))
        total += dish.price * item["quantity"]
    if not items:
        return jsonify({"ok": False, "msg": "购物车中没有有效菜品"})
    order_id = get_db().save_order(session["username"], items, total)
    session["cart"] = []
    return jsonify({"ok": True, "order_id": order_id, "total": total})


@app.route("/api/order/<int:order_id>/rate", methods=["POST"])
def api_rate_order(order_id: int) -> str:
    if session.get("role") != "顾客端":
        return jsonify({"ok": False, "msg": "请先登录"})
    if get_db().is_order_rated(order_id):
        return jsonify({"ok": False, "msg": "该订单已评价"})
    orders = get_db().list_orders()
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return jsonify({"ok": False, "msg": "订单不存在"})
    for item_data in order["items"]:
        rating_text = request.form.get(f'rating_{item_data["dish_id"]}', "")
        if rating_text:
            try:
                rating = float(rating_text)
                if 1 <= rating <= 5:
                    get_db().update_dish_rating(item_data["dish_id"], rating)
            except ValueError:
                pass
    get_db().mark_order_rated(order_id)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
