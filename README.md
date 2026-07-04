# 🍽️ 订餐系统（Ordering System）

Python 课程设计项目——基于 Flask + SQLite3 的网页版订餐系统。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask（Python） |
| 数据库 | SQLite3 |
| 前端 | Jinja2 模板 + Bootstrap 5（CDN） |
| 面向对象 | Python dataclass：`Dish`、`User`、`CartItem`、`Order` |

## 项目结构

```
OrderingSystem/
├── main.py                 # Flask 入口，路由 & API
├── models.py               # 数据类定义（dataclass）
├── db_utils.py             # 数据库工具类，所有增删改查
├── templates/
│   ├── login.html          # 登录页
│   ├── register.html       # 顾客注册页
│   ├── business.html       # 商家端（菜品管理）
│   └── customer.html       # 顾客端（点餐 + 订单历史）
├── data/
│   └── ordering.db         # SQLite 数据库（自动生成）
└── .skills/                # AI 辅助开发技能包
```

## 快速开始

### 1. 安装依赖

```bash
pip install flask
```

### 2. 启动服务器

```bash
python main.py
```

### 3. 打开浏览器

访问 [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 默认账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 商家 | 商家 | 123456 | 唯一商家账号，不可注册新的 |
| 顾客 | 顾客 | 123456 | 默认顾客（兼容旧数据） |
| 顾客 | 自行注册 | 自定义 | 登录页点击"注册新顾客" |

## 功能清单

### 商家端

- [x] 添加菜品（名称、价格、介绍）
- [x] 删除菜品
- [x] 搜索菜品（按名称/介绍模糊匹配）
- [x] 查看所有菜品列表

### 顾客端

- [x] 自助注册账号
- [x] 浏览菜单（按评分降序）
- [x] 搜索菜品
- [x] 加入购物车（支持多道菜、调整数量）
- [x] 自动计算总价并结账
- [x] 查看历史订单
- [x] 评价订单中的菜品（⭐1-5 星）
- [x] 评分防重复：每笔订单只能评价一次

### 数据持久化

- [x] 菜品、订单、顾客信息存入 SQLite3
- [x] 程序关闭重开数据不丢失

---

## 开发历程与反思

### v1.0 —— Tkinter 桌面版

最初使用 Tkinter 构建桌面 GUI，采用了以下架构：

```
main.py → ui.py（Tkinter 窗口类）→ db_utils.py（SQLite）→ models.py（dataclass）
```

**优点**：
- 一键启动，不依赖浏览器
- 面向对象设计清晰，`models.py` 和 `db_utils.py` 职责分明

**不足**：
- Tkinter 界面风格陈旧，布局调整困难
- 表格和交互组件功能有限
- 难以适配不同屏幕尺寸

### v2.0 —— Flask 网页版（当前版本）

将整个 UI 层从 Tkinter 替换为 Flask + Bootstrap，架构变为：

```
main.py（Flask 路由 + API）→ templates/*.html（Jinja2 + Bootstrap）
                          → db_utils.py（SQLite，完全复用）
                          → models.py（dataclass，完全复用）
```

**关键决策**：
1. **`models.py` 和 `db_utils.py` 一行未改**（除 SQLite 线程安全配置），验证了良好的分层设计——数据层与展示层完全解耦
2. 前端用 Bootstrap CDN，无需安装任何前端依赖，开箱即用
3. 购物车存储在 Flask session 中，无需额外数据库表

### v2.1 —— 搜索 + 订单历史 + 评分防重复

| 新增功能 | 实现方式 |
|----------|---------|
| 菜品搜索 | 数据库 `LIKE` 模糊匹配 + 前端实时 AJAX 刷新 |
| 订单历史 | 新增"我的订单"tab，按当前用户过滤 |
| 评分防重复 | `orders` 表新增 `rated` 字段，结账后可评价，评价后按钮消失 |

**反思**：
- 搜索功能最初计划在前端用 JS 过滤，但改为后端 API 查询更灵活（支持模糊匹配描述字段）
- Jinja2 模板中 `o.items` 会优先解析为 dict 的内置方法而非 key，改为 `o['items']` 下标写法解决——这是一个典型的模板引擎陷阱

### v2.2 —— 用户注册

| 新增 | 实现方式 |
|------|---------|
| 顾客注册 | `customers` 表 + `/register` 路由 |
| 商家锁定 | 商家账号硬编码，不可注册新的 |
| 数据隔离 | 每个顾客只能查看自己的订单历史 |

**反思**：
- 将旧版硬编码的 `USERS` 字典改为混合模式（商家硬编码 + 顾客查库），既保持了简洁，又提供了扩展性
- 数据库默认种子 `顾客/123456` 确保旧订单数据兼容

### 架构评价

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  templates/  │ ←→  │   main.py    │ ←→  │  db_utils.py │ ←→ SQLite3
│ (Bootstrap)  │     │  (Flask)     │     │  (数据访问)   │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                     ┌──────┴───────┐
                     │  models.py   │
                     │  (dataclass) │
                     └──────────────┘
```

**优点**：分层清晰，数据层完全可复用，UI 层替换不影响业务逻辑  
**可改进**：目前路由和 API 混在 `main.py` 中，如果继续扩展可拆分为 Blueprint

---

## 环境要求

- Python 3.9+
- Flask（`pip install flask`）
- 无需额外数据库安装（SQLite3 内置于 Python）

## License

MIT
