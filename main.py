import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# Настройки
API_KEY = "bf895a7ec2105212131cf543"
HISTORY_FILE = "history.json"
CURRENCIES = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "KZT"]

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер валют")
        self.root.geometry("500x450")
        
        self.history = self.load_history()

        # Интерфейс
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Фрейм ввода
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack()

        tk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Из:").grid(row=0, column=2, padx=5, pady=5)
        self.from_currency = ttk.Combobox(input_frame, values=CURRENCIES, width=5, state="readonly")
        self.from_currency.current(0)
        self.from_currency.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="В:").grid(row=0, column=4, padx=5, pady=5)
        self.to_currency = ttk.Combobox(input_frame, values=CURRENCIES, width=5, state="readonly")
        self.to_currency.current(2)
        self.to_currency.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка конвертации
        self.convert_btn = tk.Button(self.root, text="Конвертировать", command=self.convert_currency, bg="#4CAF50", fg="white")
        self.convert_btn.pack(pady=10)

        # Результат
        self.result_label = tk.Label(self.root, text="", font=("Arial", 14, "bold"))
        self.result_label.pack(pady=5)

        # Таблица истории
        tk.Label(self.root, text="История операций:").pack(pady=5)
        
        columns = ("date", "from", "to", "amount", "result")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)
        self.tree.heading("date", text="Дата")
        self.tree.heading("from", text="Из")
        self.tree.heading("to", text="В")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("result", text="Результат")
        
        self.tree.column("date", width=120)
        self.tree.column("from", width=50)
        self.tree.column("to", width=50)
        self.tree.column("amount", width=80)
        self.tree.column("result", width=100)
        
        self.tree.pack(padx=10, fill=tk.BOTH, expand=True)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    def update_history_table(self):
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Заполнение в обратном порядке 
        for item in reversed(self.history):
            self.tree.insert("", tk.END, values=(item["date"], item["from"], item["to"], item["amount"], item["result"]))

    def convert_currency(self):
        amount_str = self.amount_entry.get().replace(',', '.')
        
        # 1. Валидация ввода 
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректное положительное число.")
            return

        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()

        if from_curr == to_curr:
            messagebox.showinfo("Информация", "Выбраны одинаковые валюты.")
            return

        # 2. Запрос к внешнему API
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_curr}/{to_curr}/{amount}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200 and data["result"] == "success":
                result_amount = round(data["conversion_result"], 2)
                self.result_label.config(text=f"{amount} {from_curr} = {result_amount} {to_curr}")
                
                # 3. Добавление в историю
                record = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "from": from_curr,
                    "to": to_curr,
                    "amount": amount,
                    "result": result_amount
                }
                self.history.append(record)
                self.save_history()
                self.update_history_table()
            else:
                error_type = data.get("error-type", "Неизвестная ошибка API")
                messagebox.showerror("Ошибка API", f"Не удалось получить курс: {error_type}")
                
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка сети", "Проверьте подключение к интернету.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()