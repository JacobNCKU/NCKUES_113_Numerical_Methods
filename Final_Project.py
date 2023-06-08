#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tkinter as tk
import tkinter.messagebox as messagebox
import pickle
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import font
from datetime import datetime, date

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt, font):
        super().__init__(parent) 
        # 設定對話框標題
        self.title(title) 
        # 儲存字型資訊
        self.font = font 

        # 建立標籤元件，顯示提示訊息
        self.label_prompt = tk.Label(self, text=prompt, font=self.font) 
        # 將標籤元件放置於對話框上，設定上方的留白大小
        self.label_prompt.pack(pady=10) 

        # 建立輸入框元件，供使用者輸入資料
        self.entry_value = tk.Entry(self, font=self.font) 
        # 將輸入框元件放置於對話框上，設定上方的留白大小
        self.entry_value.pack(pady=10)  

        # 建立確定按鈕元件，點擊後呼叫 self.ok 方法
        self.button_ok = tk.Button(self, text="確定", command=self.ok, font=self.font) 
        # 將確定按鈕元件放置於對話框上，設定上方的留白大小
        self.button_ok.pack(pady=10)  

    def ok(self):
        self.value = self.entry_value.get()
        self.destroy()

class Ingredient:
    def __init__(self, name, quantity, expiration_date):
        self.name = name
        self.quantity = quantity
        self.expiration_date = expiration_date

class Storage:
    def __init__(self):
        self.ingredients = []

    def add_ingredient(self, ingredient):
        self.ingredients.append(ingredient)

    def remove_ingredient(self, ingredient):
        self.ingredients.remove(ingredient)

    def get_ingredients(self):
        return self.ingredients

class InventoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("食材庫存管理系統")

        # 新增儲存室食材的儲存
        self.pantry = Storage()
        # 新增過期區食材的儲存
        self.expired_items = Storage() 
        self.added_ingredients = []
        self.create_widgets()

    def create_widgets(self):
        self.label_title = tk.Label(self.root, text="🍎🌟食材庫存管理系統🌟🍎", font=("Helvetica", 18))
        self.label_title.pack(pady=10)

        self.label_datetime = tk.Label(self.root, text=self.get_current_datetime(), font=("Helvetica", 12))
        self.label_datetime.pack(pady=5)

        self.frame_ingredients = tk.Frame(self.root)
        self.frame_ingredients.pack()
        self.label_ingredients = tk.Label(self.frame_ingredients, text="▸▹▸ 放入保鮮食材 ◂◃◂", font=("Helvetica", 14))
        self.label_ingredients.pack()

        self.listbox_ingredients = tk.Listbox(self.frame_ingredients, width=40, height=6, font=("Helvetica", 12)) # 創建了一個寬度為40、高度為8的Listbox元件，使用"Helvetica"字型，字型大小為12。
        self.listbox_ingredients.pack(side=tk.LEFT, padx=10) # 並設定水平方向的留白為10。

        self.scrollbar_ingredients = tk.Scrollbar(self.frame_ingredients)
        self.scrollbar_ingredients.pack(side=tk.RIGHT, fill=tk.Y) # 設定垂直方向的填充為tk.Y，以便自動調整高度

        self.listbox_ingredients.config(yscrollcommand=self.scrollbar_ingredients.set)
        self.scrollbar_ingredients.config(command=self.listbox_ingredients.yview) # 在捲動條被操作時更新Listbox的顯示
        self.frame_buttons = tk.Frame(self.root)
        self.frame_buttons.pack(pady=10)

        self.button_add = tk.Button(self.frame_buttons, text="⪧ 放入保鮮", command=self.add_ingredient, font=("Helvetica", 12))
        self.button_add.grid(row=0, column=0, padx=5, pady=5)

        self.button_remove = tk.Button(self.frame_buttons, text="⪧ 取消保鮮", command=self.remove_ingredient, font=("Helvetica", 12))
        self.button_remove.grid(row=0, column=1, padx=5, pady=5)

        self.button_expire = tk.Button(self.frame_buttons, text="⪧ 即期品回報", command=self.show_expiring_ingredients, font=("Helvetica", 12))
        self.button_expire.grid(row=0, column=2, padx=5, pady=5)

        self.button_statistics = tk.Button(self.frame_buttons, text="⪧ 善食先為", command=self.show_statistics, font=("Helvetica", 12))
        self.button_statistics.grid(row=1, column=0, padx=5, pady=5)

        self.button_pie_chart = tk.Button(self.frame_buttons, text="⪧ 新鮮度整理", command=self.show_pie_chart, font=("Helvetica", 12))
        self.button_pie_chart.grid(row=1, column=1, padx=5, pady=5)

        self.button_remove_expired = tk.Button(self.frame_buttons, text="⪧ 過期廚餘桶", command=self.remove_expired_ingredients, font=("Helvetica", 12))
        self.button_remove_expired.grid(row=1, column=2, padx=5, pady=5)

        self.calculate_ratio_fun = tk.Button(self.frame_buttons, text="⪧ 食材消耗率", command=self.calculate_ratio, font=("Helvetica", 12))
        self.calculate_ratio_fun.grid(row=2, column=1, padx=5, pady=5)

        self.label_pantry = tk.Label(self.root, text="—⪧⊹⊰ 儲藏室 ⊱⊹⪦—", font=("Helvetica", 14))
        self.label_pantry.pack(pady=10)

        self.listbox_pantry = tk.Listbox(self.root, width=40, height=8, font=("Helvetica", 12))
        self.listbox_pantry.pack()

        self.label_expired = tk.Label(self.root, text="—⪧⊹⊰ 過期區 ⊱⊹⪦—", font=("Helvetica", 14))
        self.label_expired.pack(pady=10)

        self.listbox_expired = tk.Listbox(self.root, width=40, height=5, font=("Helvetica", 12))
        self.listbox_expired.pack()

        self.populate_ingredients_listbox()

        # Update current datetime label every second
        self.update_datetime_label()

        # Load saved inventory
        self.load_inventory()


    def get_current_datetime(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def update_datetime_label(self):
        # 更新日期時間標籤的文字
        self.label_datetime.configure(text=self.get_current_datetime(), font=("Helvetica", 14))
        # 每隔一秒重新呼叫 update_datetime_label 方法更新日期時間
        self.root.after(1000, self.update_datetime_label)

    def populate_ingredients_listbox(self):
        # 清空食材清單
        self.listbox_ingredients.delete(0, tk.END)
        # 將食材庫存中的食材加入食材清單中
        for ingredient in self.pantry.get_ingredients():
            self.listbox_ingredients.insert(tk.END, f"{ingredient.name} ({ingredient.quantity})")
            
    def calculate_ratio(self):
        today = date.today()
        ratios = []
        ingredient_names = []  # 存儲食材名稱的列表
        for selected_ingredient_obj in self.pantry.ingredients:
            name = selected_ingredient_obj.name
            quantity = selected_ingredient_obj.quantity

            remaining_days = (selected_ingredient_obj.expiration_date - today).days
            if remaining_days >= 0:
                ratio = int(quantity) / remaining_days
                ratios.append(ratio)
                ingredient_names.append(name)

        x = list(range(len(self.pantry.ingredients)))

        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['font.size'] = 12  # 設置字體大小為12
        # 計算線性回歸
        coefficients = np.polyfit(x, ratios, 1)
        line = np.polyval(coefficients, x)

        # 計算最大和最小比例數據
        max_ratio_index = np.argmax(ratios)
        min_ratio_index = np.argmin(ratios)
        max_ratio = ratios[max_ratio_index]
        min_ratio = ratios[min_ratio_index]
        max_ingredient_name = ingredient_names[max_ratio_index]
        min_ingredient_name = ingredient_names[min_ratio_index]

        # 创建新的Tkinter窗口
        window = tk.Toplevel(self.root)
        window.title("Ingredient Ratios")

        # 創建標籤顯示最大和最小比例數據及對應的食材名稱
        label_font = font.Font(size=14, weight="bold")
        label_max = tk.Label(window, text=f"最大係數: {max_ratio:.2f}，建議盡速食用: {max_ingredient_name}", font=label_font)
        label_max.pack()
        label_min = tk.Label(window, text=f"最小係數: {min_ratio:.2f}，可以慢慢享用: {min_ingredient_name}", font=label_font)
        label_min.pack()

        # 創建繪圖區域
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        ax.plot(x, ratios, 'o-', label='Coefficient')
        ax.plot(x, line, '--', label='Linear Regression')
        ax.set_xlabel('Ingredient')
        ax.set_ylabel('Coefficient')
        ax.set_title(' 【 回歸直線分析法 】 ')
        ax.set_xticks(x)
        ax.set_xticklabels([ingredient.name for ingredient in self.pantry.ingredients], rotation=45)
        ax.legend()

        # 將繪圖區域添加到Tkinter窗口中
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # 進入Tkinter事件循環
        window.mainloop()

    def create_menu(self):
        self.menubar = Menu(self.master)
        self.master.config(menu=self.menubar)

        self.file_menu = Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Exit", command=self.master.quit)

        self.edit_menu = Menu(self.menubar, tearoff=0)
        self.edit_menu.add_command(label="Calculate Ratios", command=self.calculate_ratio)

        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)

    def add_ingredient(self):
        dialog = CustomDialog(self.root, "新增食材", "請輸入食材名稱和數量（用逗號,分隔）：", ("Helvetica", 12))          # 創建自訂對話框以獲取食材資訊
        self.root.wait_window(dialog)

        if dialog.value:
             # 解析使用者輸入的食材名稱和數量
            values = dialog.value.split(",")            
            if len(values) == 2:
                name = values[0].strip()
                quantity = values[1].strip()
                dialog = CustomDialog(self.root, "新增食材", "請輸入食材的過期日期（YYYY-MM-DD）：", ("Helvetica", 12))  # 創建自訂對話框以獲取食材的過期日期
                self.root.wait_window(dialog)

                if dialog.value:
                    try:
                        # 解析使用者輸入的日期並創建食材對象
                        expiration_date = date.fromisoformat(dialog.value)
                        ingredient = Ingredient(name, quantity, expiration_date)
                        self.added_ingredients.append(ingredient)  # 將食材添加到已添加食材的列表中
                        # 如果食材已過期，將其添加到過期區並在過期區的Listbox中顯示
                        if expiration_date <= date.today():
                            self.expired_items.add_ingredient(ingredient)
                            self.listbox_expired.insert(tk.END, f"{ingredient.name} ({ingredient.quantity})")
                        else:
                            # 如果食材未過期，將其添加到儲藏室並在儲藏室的Listbox中顯示
                            self.pantry.add_ingredient(ingredient)
                            self.listbox_pantry.insert(tk.END, f"{ingredient.name} ({ingredient.quantity})")
                        # 在食材清單的Listbox中顯示食材
                        self.listbox_ingredients.insert(tk.END, f"{ingredient.name} ({ingredient.quantity})")

                    except ValueError:
                        messagebox.showerror("錯誤", "輸入的日期格式無效。請使用YYYY-MM-DD格式。")
                else:
                    messagebox.showerror("錯誤", "請輸入有效的過期日期。")
            else:
                messagebox.showerror("錯誤", "請以逗號分隔食材名稱和數量。")
        else:
            messagebox.showerror("錯誤", "請輸入有效的食材名稱和數量。")


    def remove_ingredient(self):
        # 獲取所選食材的索引
        selected_index = self.listbox_ingredients.curselection()
        if selected_index:
            selected_ingredient = self.listbox_ingredients.get(selected_index)
            name, quantity = selected_ingredient.split(" (")
            quantity = quantity[:-1]
            # 在儲藏室中尋找並移除所選食材
            for i, ingredient in enumerate(self.pantry.get_ingredients()):
                if ingredient.name == name and ingredient.quantity == quantity:
                    self.pantry.remove_ingredient(ingredient)
                    self.listbox_pantry.delete(i)
                    messagebox.showinfo("刪除食材", f"已成功刪除食材: {selected_ingredient}")
                    break
            else:
                messagebox.showerror("錯誤", "找不到該食材。")
        else:
            messagebox.showerror("錯誤", "請選擇要刪除的食材。")


    def remove_expired_ingredients(self):
        expired_ingredients = self.expired_items.get_ingredients()
        for ingredient in expired_ingredients:
            self.expired_items.remove_ingredient(ingredient)
            self.listbox_expired.delete(0, tk.END)
        messagebox.showinfo("刪除過期食材", "已成功刪除所有過期食材。")

    
    def show_expiring_ingredients(self):
        # 清空儲藏室清單
        self.listbox_pantry.delete(0, tk.END)
        # 根據保鮮期限排序食材清單
        sorted_ingredients = sorted(self.pantry.get_ingredients(), key=lambda x: x.expiration_date)
        for ingredient in sorted_ingredients:
            expiration_date = ingredient.expiration_date.strftime("%Y-%m-%d")
            self.listbox_pantry.insert(tk.END, f"{ingredient.name} ({ingredient.quantity}) - 保存期限：{expiration_date}")
        # 清空過期區清單
        self.listbox_expired.delete(0, tk.END)
        for ingredient in self.expired_items.get_ingredients():
            expiration_date = ingredient.expiration_date.strftime("%Y-%m-%d")
            self.listbox_expired.insert(tk.END, f"{ingredient.name} ({ingredient.quantity}) - 保存期限：{expiration_date}")
    
        today = date.today()
        expiring_ingredients = []
        # 找出即將過期的食材
        for ingredient in sorted_ingredients:
            days_left = (ingredient.expiration_date - today).days
            if days_left <= 7:
                expiring_ingredients.append((ingredient, days_left))
    
        if expiring_ingredients:
            # 如果有即將過期的食材，按照剩餘天數排序並建立訊息
            expiring_ingredients.sort(key=lambda x: x[1])
            message = "即將過期的食材：\n\n"
            for ingredient, days_left in expiring_ingredients:
                message += f"{ingredient.name} ({ingredient.quantity}) - 還有 {days_left} 天\n"
            messagebox.showinfo("即將過期的食材", message)
        else:
            messagebox.showinfo("即將過期的食材", "目前沒有即將過期的食材，真棒!ᕦ( ᐛ )ᕤ")
    
    
    def show_statistics(self):
        ingredient_names = []
        quantities = []

        for ingredient in self.pantry.get_ingredients():
            ingredient_names.append(ingredient.name)
            quantities.append(int(ingredient.quantity))

        # 設置字型為微軟正黑體
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        # 創建一個圖形和軸
        fig, ax = plt.subplots()
        # 繪製條形圖
        ax.bar(ingredient_names, quantities, width=0.2)
        # 設置圖形標題和軸標籤
        ax.set_title("食材庫存統計")
        ax.set_xlabel("食材名稱")
        ax.set_ylabel("數量", rotation=0)
        # 設置x軸刻度和標籤
        ax.set_xticks(range(len(ingredient_names)))  # Set the tick positions
        ax.set_xticklabels(ingredient_names, rotation=0)

        # 建立新的Tkinter視窗
        stats_window = tk.Toplevel(self.root)
        stats_window.title("庫存統計")

        # 將圖形嵌入到Tkinter視窗中
        canvas = FigureCanvasTkAgg(fig, master=stats_window)
        canvas.draw()
        canvas.get_tk_widget().pack()


    def show_pie_chart(self):
        expiration_status = {
            '未過期': len(self.pantry.get_ingredients()),
            '即將過期': len(self.expired_items.get_ingredients()),
            '已過期': len(self.expired_items.get_ingredients())
        }

        today = date.today()
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        # 檢查儲藏室中是否有已過期的食材，並更新已過期數量
        for ingredient in self.pantry.get_ingredients():
            if ingredient.expiration_date < today:
                expiration_status['已過期'] += 1

        labels = list(expiration_status.keys())
        values = list(expiration_status.values())

        # 產生含有百分比的標籤
        labels_with_percentages = [f"{label} ({value}種，{int(value/sum(values)*100)}%)" for label, value in zip(labels, values)]
        # 創建一個圖形和軸
        fig, ax = plt.subplots()
        ax.pie(values, labels=labels_with_percentages, autopct='%1.1f%%', startangle=90)

        # 設置圖形標題
        ax.set_title("食材期限狀態")
        # 設置圓餅圖的橢圓形
        ax.axis('equal')

        # 建立新的Tkinter視窗
        pie_window = tk.Toplevel(self.root)
        pie_window.title("食材期限狀態")

        # 將圖形嵌入到Tkinter視窗中
        canvas = FigureCanvasTkAgg(fig, master=pie_window)
        canvas.draw()
        canvas.get_tk_widget().pack()


    def load_inventory(self):
        try:
             # 打開 "inventory.pkl" 檔案進行讀取
            with open("inventory.pkl", "rb") as file:
                # 載入檔案中的資料
                inventory_data = pickle.load(file)
                # 檢查載入的資料是否為字典型態
                if isinstance(inventory_data, dict):
                    # 從字典中取得食材庫存和過期食材的資料
                    pantry_data = inventory_data.get("pantry", [])
                    expired_data = inventory_data.get("expired_items", [])
                else:
                    # 如果載入的資料不是字典型態，則初始化食材庫存和過期食材的空列表
                    pantry_data = []
                    expired_data = []

                # 遍歷食材庫存的資料，並建立 Ingredient 物件
                for data in pantry_data:
                    name = data.get("name", "")
                    quantity = data.get("quantity", "")
                    expiration_date = data.get("expiration_date")
                    if name and quantity and expiration_date:
                        ingredient = Ingredient(name, quantity, date.fromisoformat(expiration_date))
                        # 將食材加入食材庫存
                        self.pantry.add_ingredient(ingredient)
                        # 在食材庫存的清單框中插入食材
                        self.listbox_pantry.insert(tk.END, f"{ingredient.name} ({ingredient.quantity})")

                # 遍歷過期食材的資料，並建立 Ingredient 物件
                for data in expired_data:
                    name = data.get("name", "")
                    quantity = data.get("quantity", "")
                    expiration_date = data.get("expiration_date")
                    if name and quantity and expiration_date:
                        ingredient = Ingredient(name, quantity, date.fromisoformat(expiration_date))
                        # 將食材加入過期食材清單
                        self.expired_items.add_ingredient(ingredient)
                        # 在過期食材的清單框中插入食材並顯示過期日期
                        self.listbox_expired.insert(tk.END, f"{ingredient.name} ({ingredient.quantity}) - 保存期限：{expiration_date}")
        except FileNotFoundError:
            # 如果找不到 "inventory.pkl" 檔案，忽略錯誤
            pass


    def save_inventory(self):
        pantry_data = []
        expired_data = []

        # 將食材庫存中的食材轉換為字典格式並加入 pantry_data 列表
        for ingredient in self.pantry.get_ingredients():
            data = {
                "name": ingredient.name,
                "quantity": ingredient.quantity,
                "expiration_date": ingredient.expiration_date.isoformat()
            }
            pantry_data.append(data)
        # 將過期食材清單中的食材轉換為字典格式並加入 expired_data 列表
        for ingredient in self.expired_items.get_ingredients():
            data = {
                "name": ingredient.name,
                "quantity": ingredient.quantity,
                "expiration_date": ingredient.expiration_date.isoformat()
            }
            expired_data.append(data)

        # 建立包含庫存資料的字典
        inventory_data = {
            "pantry": pantry_data,
            "expired_items": expired_data
        }
        # 將庫存資料寫入 "inventory.pkl" 檔案
        with open("inventory.pkl", "wb") as file:
            pickle.dump(inventory_data, file)


    def on_closing(self):
        # 當關閉視窗時觸發的函式
        if messagebox.askokcancel("離開", "確定要離開嗎？"):
            # 儲存庫存資料
            self.save_inventory()
            # 關閉視窗
            self.root.destroy()

root = tk.Tk()
app = InventoryGUI(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()


# In[1]:



# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




