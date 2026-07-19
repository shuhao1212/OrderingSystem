# 订餐系统 —— 答辩 PPT 内容大纲

> 以下按幻灯片页组织，每页含标题、要点、备注。可直接交给 AI 生成 PPT。

---

## 第 1 页：封面

**标题**：订餐系统 —— 基于 Flask + SQLite3 的网页版订餐平台

**副标题**：《高级程序设计与实践》课程项目

**信息**：姓名 / 学号 / 日期

---

## 第 2 页：项目背景

**标题**：项目背景与目标

- 模拟真实外卖平台的**商家管理**和**顾客点餐**流程
- 两种角色登录：商家（管理菜品）、顾客（浏览下单评价）
- 数据持久化到 SQLite3 数据库，程序关闭不丢失
- 图形化界面 + 面向对象设计

> 💬 口述：这是一个仿外卖平台的订餐系统，商家可以添加删除菜品，顾客可以浏览菜单、下单、评价。

---

## 第 3 页：技术栈

**标题**：技术选型

| 层级 | 技术 | 选型理由 |
|------|------|---------|
| 后端 | Python Flask | 轻量、适合中小项目 |
| 数据库 | SQLite3 | Python 内置，零安装 |
| 前端 | Bootstrap 5 + Jinja2 | CDN 引入，专业美观 |
| 数据模型 | Python dataclass | 类型清晰，代码简洁 |
| 图片 | 136 张实拍菜品图 | 真实感强 |

> 💬 口述：后端用 Flask 是因为轻量易上手，数据库选 SQLite3 是因为 Python 自带不用装，前端用 Bootstrap 是因为一行 CDN 就能出专业效果。

---

## 第 4 页：系统架构

**标题**：三层架构设计

```
浏览器 (Bootstrap + Jinja2)
        ↓ HTTP
Flask 应用层 (main.py)  ← 路由、权限、业务逻辑
        ↓ 调用
数据访问层 (db_utils.py) ← DatabaseManager 类封装所有 SQL
        ↓ 读写
SQLite3 (data/ordering.db) ← dishes / orders / customers 三表
        ↑
   models.py ← Dish、CartItem、Order 三个 dataclass
```

**关键设计**：数据层与展示层完全分离，`models.py` 和 `db_utils.py` 可跨 UI 框架复用。

> 💬 口述：系统分三层，浏览器发请求到 Flask，Flask 调用数据库工具类，工具类操作 SQLite。数据实体用 dataclass 定义，整个数据层和前端完全解耦。

---

## 第 5 页：数据库设计

**标题**：三张核心数据表

| 表名 | 关键字段 | 说明 |
|------|---------|------|
| `dishes` | id, name(唯一), price, rating, image | 136 道菜品 |
| `orders` | id, customer_name, items(JSON), total_price, rated | 订单快照 |
| `customers` | username(主键), password | 顾客账号 |

**设计亮点**：
- `orders.items` 存 JSON 快照——菜品被删后历史订单依然完整
- `orders.rated` 字段（0/1）控制评分防重复
- `customers` 表支持顾客自助注册

> 💬 口述：三张表。dishes 存菜品，orders 存订单且用 JSON 存明细，这样即使商家删了菜历史订单也不丢。customers 存注册用户。rated 字段保证每单只能评一次。

---

## 第 6 页：功能展示——商家端

**标题**：商家端功能

| 功能 | 实现 |
|------|------|
| 📋 查看菜单 | 表格展示全部 136 道菜（缩略图 + 价格 + 评分） |
| ➕ 添加菜品 | 填写名称/价格/介绍 + 上传图片 |
| ❌ 删除菜品 | 选中即删，序号自动重排 |
| 🔍 搜索菜品 | 输入关键词实时过滤（匹配名称和介绍） |

> 💬 口述：商家登录后看到菜品管理页，左侧加菜右边列表。删菜后序号自动连续，搜索框实时过滤。

---

## 第 7 页：功能展示——顾客端

**标题**：顾客端功能

| 功能 | 实现 |
|------|------|
| 📝 注册/登录 | 顾客自助注册，商家唯一账号 |
| 🛒 点餐 | 菜单按评分降序，选数量→加入购物车→自动算总价 |
| 📋 订单历史 | 查看所有历史订单，按当前用户过滤 |
| ⭐ 评价 | 弹窗选 1-5 星，每单只能评一次 |

> 💬 口述：顾客注册后看到点餐页，菜单按评分从高到低排。加入购物车后自动算总价，结账。订单历史可以看到之前下的单，没评价的可以打分。

---

## 第 8 页：关键代码——面向对象设计

**标题**：面向对象实现

```python
@dataclass
class Dish:
    name: str; price: float; description: str
    rating: float = 0.0; image: str = ""; id: int | None = None

@dataclass
class CartItem:
    dish: Dish; quantity: int = 1

class DatabaseManager:
    def add_dish(self, dish: Dish) -> Dish       # INSERT
    def delete_dish(self, dish_id: int) -> bool    # DELETE
    def search_dishes(self, keyword: str) -> List[Dish]  # LIKE
    def save_order(self, name, items, total) -> int      # INSERT JSON
    def mark_order_rated(self, order_id: int) -> bool     # UPDATE
```

- 实体用 `dataclass` 定义，类型清晰
- 数据库操作封装在 `DatabaseManager` 类中
- `main.py` 只调用方法，不直接写 SQL

> 💬 口述：所有实体用 dataclass 定义，数据库操作全封装在 DatabaseManager 类里，main.py 只负责路由调度。这体现了面向对象的封装思想。

---

## 第 9 页：关键代码——评分防重复 & 订单快照

**标题**：两个核心机制

**评分防重复**：
```python
if get_db().is_order_rated(order_id):   # rated=1 则拒绝
    return jsonify({"ok": False, "msg": "该订单已评价"})
# ... 逐道打分 ...
get_db().mark_order_rated(order_id)     # 标记已评
```

**订单快照**（即使菜品被删，历史订单不丢）：
```python
payload = [{
    "dish_name": item.dish.name,    # 把菜名写进订单
    "unit_price": item.dish.price,  # 把价格写进订单
    "quantity": item.quantity,
} for item in items]
# 存入 orders.items (JSON TEXT)
```

> 💬 口述：评分防重复靠 rated 字段，评价后置 1，再评就拒绝。订单快照就是在下单时把菜名和价格写死进 JSON，后面商家改价删菜都不影响。

---

## 第 10 页：关键代码——登录与权限

**标题**：混合登录模式

```python
if role == "商家端":
    # 唯一账号，硬编码验证
    if username == "商家" and password == "123456":
        session["role"] = "商家端"
elif role == "顾客端":
    # 查询 customers 表验证
    customer = get_db().validate_customer(username, password)
    if customer:
        session["role"] = "顾客端"

# 每个路由开头均有权限检查
if session.get("role") != "商家端":
    return redirect(url_for("login"))
```

> 💬 口述：商家只有一个账号，密码写死在代码里；顾客注册后存数据库。每个页面加载时检查 session 里的角色，防止越权访问。

---

## 第 11 页：创新点

**标题**：项目亮点

| 创新 | 说明 |
|------|------|
| 🔄 分层可复用 | models + db_utils 从 Tkinter 版无缝迁移到 Flask 版 |
| 📸 订单快照 | JSON 存储订单明细，菜品被删历史订单不丢 |
| 🔒 评分防重复 | rated 字段控制，一单一评 |
| 🔢 序号自动重排 | Jinja2 `loop.index` 替代数据库 ID |
| 🖼️ 136 张实拍图 | 真实菜品图片，按菜名自动匹配 |
| 📝 顾客自助注册 | customers 表支持注册，数据隔离 |

> 💬 口述：几个亮点——数据层可以跨框架复用；订单快照保护历史数据；评分防刷；序号自动重排；真实菜品图片。

---

## 第 12 页：踩坑与解决

**标题**：遇到的问题与解决

| 问题 | 原因 | 解决 |
|------|------|------|
| SQLite 跨线程报错 | Flask 多线程 | `check_same_thread=False` |
| Jinja2 `o.items` 报错 | dict 方法名冲突 | 改为 `o['items']` |
| 删菜后序号断裂 | 显示数据库 ID | 改用 `loop.index` |
| 注册账号丢失 | 调试时删库 | `register_customer` 仅首次执行 |
| 数据库文件锁定 | Flask 进程持有 | 先停服务再删库 |

> 💬 口述：开发中碰到的典型问题——SQLite 多线程、模板语法冲突、序号显示、数据持久化。每个都有明确的解决方案。

---

## 第 13 页：项目总结

**标题**：总结与收获

- ✅ 完成了一个功能完整的网页版订餐系统（136 道菜、8 个页面/API）
- ✅ 实践了 **三层架构 + 面向对象 + 数据库设计**
- ✅ 掌握了 Flask 路由、Jinja2 模板、Bootstrap 前端、AJAX 交互
- ✅ 积累了调试经验：线程安全、模板解析、文件锁、数据一致性
- 📝 代码量：Python ~600 行 + HTML ~500 行 + 136 张图片

> 💬 口述：整个项目下来，从桌面版到网页版，从前端到后端到数据库，完整走了一遍 Web 开发的流程。最大的收获是理解了分层设计的好处——数据层写好了，换界面框架几乎不用改。

---

## 第 14 页：致谢

**标题**：谢谢！请老师提问

- GitHub 仓库：github.com/shuhao1212/OrderingSystem
- 演示地址：http://127.0.0.1:5000

---

## 附：演示流程建议（3 分钟）

| 时间 | 内容 |
|------|------|
| 0:00-0:30 | 封面 + 项目背景 + 技术栈 |
| 0:30-1:00 | 架构图 + 数据库设计 |
| 1:00-2:00 | 现场演示：商家登录→加菜→顾客注册→加购物车→结账→评价 |
| 2:00-2:30 | 两段核心代码（评分防重复 + 订单快照） |
| 2:30-3:00 | 创新点 + 踩坑 + 总结 |
