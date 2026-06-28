from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from db_utils import DatabaseManager
from models import CartItem, Dish, User


class OrderingApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("订餐系统")
        self.geometry("1000x650")
        self.resizable(False, False)
        self.db = DatabaseManager("data/ordering.db")
        self.users = [
            User(username="商家", password="123456", role="商家端"),
            User(username="顾客", password="123456", role="顾客端"),
        ]
        self.cart: list[CartItem] = []
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_login_view()

    def on_close(self) -> None:
        self.db.close()
        self.destroy()

    def show_login_view(self) -> None:
        self.clear_content()
        self.configure(padx=40, pady=40)

        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="订餐系统登录", font=("Microsoft YaHei", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        self.role_var = tk.StringVar(value="顾客端")
        ttk.Label(frame, text="角色").grid(row=1, column=0, sticky="w")
        ttk.Combobox(frame, textvariable=self.role_var, values=["商家端", "顾客端"], state="readonly", width=20).grid(row=1, column=1, padx=5, pady=5)

        self.username_var = tk.StringVar(value="商家")
        self.password_var = tk.StringVar(value="123456")

        ttk.Label(frame, text="用户名").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.username_var, width=24).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="密码").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.password_var, show="*", width=24).grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(frame, text="登录", command=self.handle_login).grid(row=4, column=0, columnspan=2, pady=(20, 0))

    def handle_login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showerror("提示", "请输入用户名和密码")
            return

        matched = next((user for user in self.users if user.username == username and user.password == password and user.role == role), None)
        if matched is None:
            messagebox.showerror("提示", "用户名、密码或角色不正确")
            return

        if role == "商家端":
            self.show_business_view()
        else:
            self.show_customer_view()

    def clear_content(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def show_business_view(self) -> None:
        self.clear_content()
        self.title("商家端 - 菜品管理")

        main = ttk.Frame(self, padding=15)
        main.pack(fill="both", expand=True)

        left = ttk.LabelFrame(main, text="添加菜品", padding=10)
        left.pack(side="left", fill="y", padx=(0, 10))

        self.business_name_var = tk.StringVar()
        self.business_price_var = tk.StringVar()
        self.business_desc_var = tk.StringVar()

        ttk.Label(left, text="名称").grid(row=0, column=0, sticky="w")
        ttk.Entry(left, textvariable=self.business_name_var, width=25).grid(row=0, column=1, pady=3)

        ttk.Label(left, text="价格").grid(row=1, column=0, sticky="w")
        ttk.Entry(left, textvariable=self.business_price_var, width=25).grid(row=1, column=1, pady=3)

        ttk.Label(left, text="介绍").grid(row=2, column=0, sticky="w")
        ttk.Entry(left, textvariable=self.business_desc_var, width=25).grid(row=2, column=1, pady=3)

        ttk.Button(left, text="添加菜品", command=self.add_dish).grid(row=3, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(left, text="删除选中", command=self.delete_selected_dish).grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(left, text="返回登录", command=self.show_login_view).grid(row=5, column=0, columnspan=2, pady=5)

        right = ttk.LabelFrame(main, text="当前菜单", padding=10)
        right.pack(side="left", fill="both", expand=True)

        columns = ("id", "name", "price", "rating", "description")
        self.business_tree = ttk.Treeview(right, columns=columns, show="headings", height=16)
        self.business_tree.heading("id", text="编号")
        self.business_tree.heading("name", text="名称")
        self.business_tree.heading("price", text="价格")
        self.business_tree.heading("rating", text="评分")
        self.business_tree.heading("description", text="介绍")
        self.business_tree.column("id", width=50, anchor="center")
        self.business_tree.column("name", width=120, anchor="center")
        self.business_tree.column("price", width=80, anchor="center")
        self.business_tree.column("rating", width=70, anchor="center")
        self.business_tree.column("description", width=220)
        self.business_tree.pack(fill="both", expand=True)
        self.refresh_business_tree()

    def add_dish(self) -> None:
        name = self.business_name_var.get().strip()
        price_text = self.business_price_var.get().strip()
        description = self.business_desc_var.get().strip()
        if not name or not price_text or not description:
            messagebox.showwarning("提示", "请完整填写名称、价格和介绍")
            return
        try:
            price = float(price_text)
        except ValueError:
            messagebox.showerror("提示", "价格必须是数字")
            return

        dish = Dish(name=name, price=price, description=description)
        self.db.add_dish(dish)
        self.refresh_business_tree()
        self.business_name_var.set("")
        self.business_price_var.set("")
        self.business_desc_var.set("")
        messagebox.showinfo("提示", "菜品添加成功")

    def delete_selected_dish(self) -> None:
        selected = self.business_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要删除的菜品")
            return
        dish_id = int(self.business_tree.item(selected[0], "values")[0])
        success = self.db.delete_dish(dish_id)
        if success:
            self.refresh_business_tree()
            messagebox.showinfo("提示", "菜品已删除")
        else:
            messagebox.showerror("提示", "删除失败")

    def refresh_business_tree(self) -> None:
        for item in self.business_tree.get_children():
            self.business_tree.delete(item)
        for dish in self.db.list_dishes(sort_by_rating=False):
            self.business_tree.insert(
                "",
                "end",
                values=(dish.id, dish.name, f"{dish.price:.2f}", f"{dish.rating:.1f}", dish.description),
            )

    def show_customer_view(self) -> None:
        self.clear_content()
        self.title("顾客端 - 订餐")
        self.cart = []

        main = ttk.Frame(self, padding=15)
        main.pack(fill="both", expand=True)

        left = ttk.LabelFrame(main, text="菜单列表", padding=10)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.customer_name_var = tk.StringVar(value="顾客")
        ttk.Label(left, text="顾客名称").pack(anchor="w")
        ttk.Entry(left, textvariable=self.customer_name_var, width=24).pack(anchor="w", pady=(0, 8))

        columns = ("id", "name", "price", "rating", "description")
        self.customer_tree = ttk.Treeview(left, columns=columns, show="headings", height=14)
        self.customer_tree.heading("id", text="编号")
        self.customer_tree.heading("name", text="名称")
        self.customer_tree.heading("price", text="价格")
        self.customer_tree.heading("rating", text="评分")
        self.customer_tree.heading("description", text="介绍")
        self.customer_tree.column("id", width=50, anchor="center")
        self.customer_tree.column("name", width=120, anchor="center")
        self.customer_tree.column("price", width=80, anchor="center")
        self.customer_tree.column("rating", width=70, anchor="center")
        self.customer_tree.column("description", width=240)
        self.customer_tree.pack(fill="both", expand=True)

        toolbar = ttk.Frame(left)
        toolbar.pack(fill="x", pady=(8, 0))
        self.quantity_var = tk.StringVar(value="1")
        ttk.Label(toolbar, text="数量").pack(side="left")
        ttk.Entry(toolbar, textvariable=self.quantity_var, width=6).pack(side="left", padx=(5, 10))
        ttk.Button(toolbar, text="加入购物车", command=self.add_to_cart).pack(side="left")
        ttk.Button(toolbar, text="评分", command=self.rate_selected_dish).pack(side="left", padx=(10, 0))

        right = ttk.LabelFrame(main, text="购物车", padding=10)
        right.pack(side="right", fill="both")

        self.cart_list = tk.Listbox(right, width=40, height=14)
        self.cart_list.pack(fill="both", expand=True)

        self.total_var = tk.StringVar(value="总价：0.00")
        ttk.Label(right, textvariable=self.total_var, font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", pady=(8, 5))
        ttk.Button(right, text="结账下单", command=self.checkout).pack(fill="x", pady=(4, 0))
        ttk.Button(right, text="返回登录", command=self.show_login_view).pack(fill="x", pady=(6, 0))

        self.refresh_customer_tree()

    def refresh_customer_tree(self) -> None:
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        for dish in self.db.list_dishes(sort_by_rating=True):
            self.customer_tree.insert(
                "",
                "end",
                values=(dish.id, dish.name, f"{dish.price:.2f}", f"{dish.rating:.1f}", dish.description),
            )

    def add_to_cart(self) -> None:
        selected = self.customer_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择一道菜")
            return
        dish_id = int(self.customer_tree.item(selected[0], "values")[0])
        dish = self.db.get_dish_by_id(dish_id)
        if dish is None:
            messagebox.showerror("提示", "菜品不存在")
            return
        try:
            quantity = int(self.quantity_var.get().strip())
        except ValueError:
            messagebox.showerror("提示", "数量必须是整数")
            return
        if quantity <= 0:
            messagebox.showwarning("提示", "数量必须大于 0")
            return
        self.cart.append(CartItem(dish=dish, quantity=quantity))
        self.update_cart_display()
        messagebox.showinfo("提示", f"已加入购物车：{dish.name} x{quantity}")

    def update_cart_display(self) -> None:
        self.cart_list.delete(0, tk.END)
        total = 0.0
        for index, item in enumerate(self.cart, start=1):
            line = f"{index}. {item.dish.name} x{item.quantity} = {item.dish.price * item.quantity:.2f}"
            self.cart_list.insert(tk.END, line)
            total += item.dish.price * item.quantity
        self.total_var.set(f"总价：{total:.2f}")

    def checkout(self) -> None:
        if not self.cart:
            messagebox.showwarning("提示", "购物车为空")
            return
        name = self.customer_name_var.get().strip() or "顾客"
        total = sum(item.dish.price * item.quantity for item in self.cart)
        self.db.save_order(name, self.cart, total)
        self.cart.clear()
        self.update_cart_display()
        messagebox.showinfo("提示", f"下单成功！总价为 {total:.2f} 元")

    def rate_selected_dish(self) -> None:
        selected = self.customer_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要评分的菜品")
            return
        dish_id = int(self.customer_tree.item(selected[0], "values")[0])
        rating_text = simpledialog.askstring("评分", "请输入 1-5 的评分", parent=self)
        if rating_text is None:
            return
        try:
            rating = float(rating_text)
        except ValueError:
            messagebox.showerror("提示", "评分必须是数字")
            return
        if not 1 <= rating <= 5:
            messagebox.showwarning("提示", "评分范围必须在 1 到 5 之间")
            return
        self.db.update_dish_rating(dish_id, rating)
        self.refresh_customer_tree()
        messagebox.showinfo("提示", "评分已更新")


if __name__ == "__main__":
    app = OrderingApp()
    app.mainloop()
