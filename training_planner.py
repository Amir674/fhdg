import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "trainings.json"

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")
        
        self.trainings = []
        self.load_data()
        
        # Поля ввода
        frame_input = tk.Frame(root)
        frame_input.pack(pady=10)
        
        tk.Label(frame_input, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5)
        self.entry_date = tk.Entry(frame_input, width=15)
        self.entry_date.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_input, text="Тип тренировки:").grid(row=0, column=2, padx=5)
        self.type_var = tk.StringVar()
        self.entry_type = tk.Entry(frame_input, textvariable=self.type_var, width=15)
        self.entry_type.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_input, text="Длительность (мин):").grid(row=0, column=4, padx=5)
        self.entry_duration = tk.Entry(frame_input, width=10)
        self.entry_duration.grid(row=0, column=5, padx=5)
        
        self.btn_add = tk.Button(frame_input, text="Добавить тренировку", command=self.add_training)
        self.btn_add.grid(row=0, column=6, padx=10)
        
        # Фильтры
        frame_filter = tk.Frame(root)
        frame_filter.pack(pady=5)
        
        tk.Label(frame_filter, text="Фильтр по типу:").grid(row=0, column=0, padx=5)
        self.filter_type_var = tk.StringVar()
        self.filter_type_entry = tk.Entry(frame_filter, textvariable=self.filter_type_var, width=15)
        self.filter_type_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_filter, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5)
        self.filter_date_var = tk.StringVar()
        self.filter_date_entry = tk.Entry(frame_filter, textvariable=self.filter_date_var, width=15)
        self.filter_date_entry.grid(row=0, column=3, padx=5)
        
        self.btn_filter = tk.Button(frame_filter, text="Применить фильтр", command=self.filter_table)
        self.btn_filter.grid(row=0, column=4, padx=5)
        
        self.btn_reset = tk.Button(frame_filter, text="Сбросить фильтр", command=self.reset_filter)
        self.btn_reset.grid(row=0, column=5, padx=5)
        
        # Таблица
        self.tree = ttk.Treeview(root, columns=("date", "type", "duration"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        self.tree.column("date", width=120)
        self.tree.column("type", width=150)
        self.tree.column("duration", width=120)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Кнопки управления
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(pady=5)
        
        self.btn_delete = tk.Button(frame_buttons, text="Удалить выбранное", command=self.delete_selected)
        self.btn_delete.pack(side=tk.LEFT, padx=5)
        
        self.btn_save = tk.Button(frame_buttons, text="Сохранить в JSON", command=self.save_data)
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        # Обновить таблицу
        self.refresh_table()
    
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_str):
        try:
            duration = float(duration_str)
            return duration > 0
        except ValueError:
            return False
    
    def add_training(self):
        date = self.entry_date.get().strip()
        training_type = self.type_var.get().strip()
        duration = self.entry_duration.get().strip()
        
        if not date or not training_type or not duration:
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения!")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        
        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return
        
        self.trainings.append({
            "date": date,
            "type": training_type,
            "duration": float(duration)
        })
        
        # Очистка полей
        self.entry_date.delete(0, tk.END)
        self.type_var.set("")
        self.entry_duration.delete(0, tk.END)
        
        self.refresh_table()
        self.save_data()  # Автосохранение
    
    def refresh_table(self, filtered_list=None):
        # Очистить таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        data = filtered_list if filtered_list is not None else self.trainings
        for training in data:
            self.tree.insert("", tk.END, values=(
                training["date"],
                training["type"],
                training["duration"]
            ))
    
    def filter_table(self):
        filter_type = self.filter_type_var.get().strip()
        filter_date = self.filter_date_var.get().strip()
        
        filtered = self.trainings.copy()
        
        if filter_type:
            filtered = [t for t in filtered if filter_type.lower() in t["type"].lower()]
        
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты в фильтре!")
                return
            filtered = [t for t in filtered if t["date"] == filter_date]
        
        self.refresh_table(filtered)
    
    def reset_filter(self):
        self.filter_type_var.set("")
        self.filter_date_var.set("")
        self.refresh_table()
    
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        for item in selected:
            values = self.tree.item(item, "values")
            # Удаление по совпадению (дата + тип + длительность)
            self.trainings = [t for t in self.trainings 
                            if not (t["date"] == values[0] and 
                                   t["type"] == values[1] and 
                                   str(t["duration"]) == values[2])]
        
        self.refresh_table()
        self.save_data()
    
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.trainings = json.load(f)
            except:
                self.trainings = []
    
    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.trainings, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
