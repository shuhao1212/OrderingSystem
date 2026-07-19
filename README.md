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
│   ├── business.html       # 商家端（菜品管理 + 上传图片）
│   └── customer.html       # 顾客端（点餐 + 订单历史）
├── static/
│   └── images/             # 136 张菜品图片
├── 图集/                    # 原始图片素材（按菜名命名）
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

- [x] 添加菜品（名称、价格、介绍、上传图片）
- [x] 删除菜品（序号自动重排）
- [x] 搜索菜品（按名称/介绍模糊匹配）
- [x] 查看所有菜品列表（含缩略图）
- [x] 批量导入 136 道菜品模板数据

### 顾客端

- [x] 自助注册账号
- [x] 浏览菜单（按评分降序，含菜品图片）
- [x] 搜索菜品
- [x] 加入购物车（支持多道菜、调整数量）
- [x] 自动计算总价并结账
- [x] 查看历史订单
- [x] 评价订单中的菜品（⭐1-5 星下拉选择）
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

### v2.3 —— 菜品图片 + 序号重排 + 图片上传

| 新增 / 修复 | 实现方式 |
|------------|---------|
| 菜品图片展示 | `dishes` 表新增 `image` 列，`static/images/` 存放 136 张菜品图 |
| 批量种子数据 | `seed_all_dishes()` 一次性导入全部菜品及合理价格 |
| 序号自动重排 | 表格序号列从数据库 ID 改为 `loop.index` 行号，删除后自动连续 |
| 商家上传图片 | 表单 `multipart/form-data` + 后端 `request.files` 保存，UUID 防重名 |
| 默认菜移除 | 删除无对应图片的 3 个初始示例菜 |

### v2.4 —— 持久化修复 + 安全加固

| 修复 | 实现方式 |
|------|---------|
| 注册账号丢失 | 停止调试期间手动删库操作；`register_customer` 移入首次建库逻辑 |
| session 随机失效 | `secret_key` 从 `os.urandom` 改为文件持久化（`data/.secret_key`） |
| 重复种子调用 | 移除 `main.py` 中冗余的 `seed_all_dishes()` |
| 登录页安全 | 移除用户名/密码预填值，改为 placeholder 提示 |
| 清理废弃代码 | 删除 v1.0 遗留的 `ui.py`（Tkinter 桌面版），项目统一为 Flask |
| 文档完善 | 新增 `答辩指南.md`，含代码导读、修改速查、10 道答辩模拟题 |

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

## 报错记录与解决方案

### 1. `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread`

**现象**：Flask 顾客端页面返回 500 错误，Werkzeug 调试器显示此异常。

**原因**：Flask debug 模式默认多线程，但 SQLite3 默认禁止跨线程使用同一连接。

**解决**：
```python
# db_utils.py，__init__ 方法中
self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
```

---

### 2. Jinja2 模板 `o.items` 解析冲突

**现象**：
```
TypeError: 'builtin_function_or_method' object is not iterable
```
发生在 `customer.html` 第 101 行 `{% for it in o.items %}`。

**原因**：Jinja2 变量解析时，`o.items` 优先查找对象属性，dict 自带的 `.items()` 方法先于 key `'items'` 被匹配，导致尝试迭代一个方法对象。

**解决**：全部改为下标语法 `o['items']`，明确告诉 Jinja2 这是字典键而非对象属性。
```jinja2
{% for it in o['items'] %}
```

---

### 3. 文件编码问题：`UnicodeDecodeError: 'gbk' codec can't decode byte`

**现象**：用 PowerShell 执行 `open('main.py').read()` 时报 GBK 编码错误。

**原因**：PowerShell 默认使用 GBK 编码读取文件，而 Python 源文件包含 UTF-8 中文字符。

**解决**：避免在 PowerShell 中直接读取 Python 文件内容，改用 `python -c` 或直接 `python main.py`。

---

### 4. 数据库文件被锁定

**现象**：
```
Remove-Item: 无法删除项 ... 文件正由另一进程使用
```

**原因**：Flask 服务器正在运行，SQLite 连接持有 `data/ordering.db` 的文件锁。

**解决**：先 `kill_terminal` 停止 Flask 进程，再删除数据库文件，最后重启。

---

### 5. `register_customer` 方法头丢失

**现象**：
```
AttributeError: 'DatabaseManager' object has no attribute 'register_customer'
```

**原因**：在插入 `seed_all_dishes` 方法时，替换操作覆盖了 `register_customer` 的 `def` 行，只留下方法体孤悬在 `seed_all_dishes` 的 `return count` 之后。

**解决**：手动补回 `def register_customer(self, username, password) -> tuple[bool, str]:` 方法头。教训：替换代码时确保 `oldString` 和 `newString` 边界精确，不要依赖行号。

---

### 6. 删除菜品后序号出现缺口

**现象**：删除中间某道菜后，序号列显示 1, 2, 4, 5... 中间有断层。

**原因**：序号列直接使用了数据库自增 ID（`d.id`），而 SQLite 的 AUTOINCREMENT 不会回收已删除的 ID。

**解决**：将模板中的 `{{ d.id }}` 替换为 `{{ loop.index }}`（Jinja2 内置行计数器），搜索结果的 JS 中也用 `map((d, i) => ... i + 1 ...)` 生成连续序号。删除按钮仍使用 `d.id` 来精确定位数据库记录。

---

### 7. 菜品数据与图片文件不匹配

**现象**：代码中有"1饭"、"宫保鸡丁"等默认菜，但用户已将图片文件重命名为"米饭.jpg"或删除了图片。

**解决**：
- `seed_all_dishes()` 中使用 `INSERT OR IGNORE` 防止重复
- 删除数据库后重新生成，确保数据与 `static/images/` 中的文件一致
- 移除 `initialize()` 中的 3 个硬编码默认菜，统一由 `seed_all_dishes()` 管理
- 清理 `static/images/` 中不再被引用的孤立图片文件

### 8. 注册账号重启后丢失

**现象**：注册的顾客账号下次打开网页无**解决**：
- 调试期间多次手动 `Remove-Item data/ordering.db` 导致数据丢失——这是操作问题而非 bug
- 将 `register_customer("顾客", "123456")` 移入 `if self.count_dishes() == 0:` 块，确保只在首次建库时执行
- Flask `secret_key` 从 `os.urandom(24)` 改为文件持久化，避免 session 随重启失效

### 9. 登录页默认预填用户名密码

**现象**：打开登录页自动填好"顾客 / 123456"，不够安全。

**解决**：移除 `value` 属性，改用 `placeholder` 提示文字，首次访问为空输入框。

---

## 环境要求

- Python 3.9+
- Flask（`pip install flask`）
- 无需额外数据库安装（SQLite3 内置于 Python）

## License

MIT
