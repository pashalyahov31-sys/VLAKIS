import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("850x650")
        self.root.resizable(False, False)
        
        self.data_file = "training_data.json"
        self.workouts = []
        self.load_data()
        
        self.create_widgets()
        self.update_display()
    
    # ========== Работа с JSON ==========
    def save_data(self):
        """Сохраняет тренировки в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.workouts, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        """Загружает тренировки из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.workouts = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.workouts = []
        else:
            self.workouts = []
    
    # ========== Валидация ввода ==========
    def validate_date(self, date_str):
        """Проверяет формат даты (ГГГГ-ММ-ДД)"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_str):
        """Проверяет, что длительность - положительное число"""
        try:
            duration = float(duration_str)
            return duration > 0
        except ValueError:
            return False
    
    # ========== Добавление тренировки ==========
    def add_workout(self):
        date = self.date_entry.get().strip()
        workout_type = self.type_var.get()
        duration = self.duration_entry.get().strip()
        
        # Проверка корректности ввода
        if not date:
            messagebox.showwarning("Ошибка", "Введите дату!")
            return
        
        if not self.validate_date(date):
            messagebox.showwarning("Ошибка", "Неверный формат даты!\nИспользуйте ГГГГ-ММ-ДД (например, 2024-03-15)")
            return
        
        if not duration:
            messagebox.showwarning("Ошибка", "Введите длительность!")
            return
        
        if not self.validate_duration(duration):
            messagebox.showwarning("Ошибка", "Длительность должна быть положительным числом!")
            return
        
        if not workout_type:
            messagebox.showwarning("Ошибка", "Выберите тип тренировки!")
            return
        
        # Создаём запись
        new_workout = {
            "date": date,
            "type": workout_type,
            "duration": float(duration)
        }
        
        self.workouts.append(new_workout)
        self.save_data()
        self.update_display()
        
        # Очищаем поля ввода
        self.date_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)
        self.type_var.set("")
        
        messagebox.showinfo("Успех", "Тренировка добавлена!")
    
    # ========== Отображение тренировок ==========
    def update_display(self, filtered_workouts=None):
        """Обновляет таблицу с тренировками"""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        workouts_to_show = filtered_workouts if filtered_workouts is not None else self.workouts
        
        # Сортируем по дате (новые сверху)
        workouts_to_show.sort(key=lambda x: x["date"], reverse=True)
        
        for workout in workouts_to_show:
            self.tree.insert("", tk.END, values=(


workout["date"],
                workout["type"],
                f"{workout['duration']:.1f} мин"
            ))
    
    # ========== Фильтрация ==========
    def filter_by_type(self):
        workout_type = self.filter_type_var.get()
        
        if not workout_type:
            messagebox.showwarning("Ошибка", "Выберите тип тренировки для фильтрации!")
            return
        
        filtered = [w for w in self.workouts if w["type"] == workout_type]
        
        if not filtered:
            messagebox.showinfo("Результат", f"Тренировок типа '{workout_type}' не найдено.")
        
        self.update_display(filtered)
        self.current_filter_label.config(text=f"Фильтр: тип = {workout_type}")
    
    def filter_by_date(self):
        date_filter = self.filter_date_entry.get().strip()
        
        if not date_filter:
            messagebox.showwarning("Ошибка", "Введите дату для фильтрации!")
            return
        
        if not self.validate_date(date_filter):
            messagebox.showwarning("Ошибка", "Неверный формат даты!\nИспользуйте ГГГГ-ММ-ДД")
            return
        
        filtered = [w for w in self.workouts if w["date"] == date_filter]
        
        if not filtered:
            messagebox.showinfo("Результат", f"Тренировок за {date_filter} не найдено.")
        
        self.update_display(filtered)
        self.current_filter_label.config(text=f"Фильтр: дата = {date_filter}")
    
    def reset_filter(self):
        """Сбрасывает фильтрацию и показывает все тренировки"""
        self.filter_type_var.set("")
        self.filter_date_entry.delete(0, tk.END)
        self.update_display()
        self.current_filter_label.config(text="Фильтр: все тренировки")
        messagebox.showinfo("Фильтр", "Фильтрация сброшена. Показаны все тренировки.")
    
    def delete_selected(self):
        """Удаляет выбранную тренировку"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите тренировку для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную тренировку?"):
            # Получаем данные выбранной записи
            for item in selected:
                values = self.tree.item(item, "values")
                # Ищем запись в self.workouts
                for i, workout in enumerate(self.workouts):
                    if (workout["date"] == values[0] and 
                        workout["type"] == values[1] and
                        float(workout["duration"]) == float(values[2].replace(" мин", ""))):
                        del self.workouts[i]
                        break
            
            self.save_data()
            self.update_display()
            messagebox.showinfo("Успех", "Тренировка удалена!")
    
    def show_statistics(self):
        """Показывает статистику тренировок"""
        if not self.workouts:
            messagebox.showinfo("Статистика", "Нет данных для статистики.")
            return
        
        total_workouts = len(self.workouts)
        total_duration = sum(w["duration"] for w in self.workouts)
        avg_duration = total_duration / total_workouts
        
        # Статистика по типам
        types_count = {}
        for w in self.workouts:
            types_count[w["type"]] = types_count.get(w["type"], 0) + 1
        
        stats_text = f"📊 Статистика тренировок:\n\n"
        stats_text += f"Всего тренировок: {total_workouts}\n"
        stats_text += f"Общая длительность: {total_duration:.1f} минут\n"
        stats_text += f"Средняя длительность: {avg_duration:.1f} минут\n\n"
        stats_text += f"📈 По типам:\n"
        
        for wtype, count in types_count.items():
            stats_text += f"  • {wtype}: {count} тренировок\n"
        
        messagebox.showinfo("Статистика", stats_text)
    
    # ========== Интерфейс ==========
    def create_widgets(self):
        # Основной контейнер
        main_frame


= ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== Левая панель - Добавление тренировки =====
        left_frame = ttk.LabelFrame(main_frame, text="➕ Добавить тренировку", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Дата
        ttk.Label(left_frame, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.date_entry = ttk.Entry(left_frame, width=25, font=("Arial", 10))
        self.date_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Тип тренировки
        ttk.Label(left_frame, text="Тип тренировки:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.type_var = tk.StringVar()
        workout_types = ["Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Футбол", "Теннис", "Другое"]
        self.type_combo = ttk.Combobox(left_frame, textvariable=self.type_var, values=workout_types, 
                                        state="readonly", width=22, font=("Arial", 10))
        self.type_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Длительность
        ttk.Label(left_frame, text="Длительность (минуты):", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.duration_entry = ttk.Entry(left_frame, width=25, font=("Arial", 10))
        self.duration_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопка добавления
        ttk.Button(left_frame, text="➕ Добавить тренировку", command=self.add_workout).pack(fill=tk.X, pady=10)
        
        # Кнопка удаления
        ttk.Button(left_frame, text="🗑 Удалить тренировку", command=self.delete_selected).pack(fill=tk.X, pady=5)
        
        # Кнопка статистики
        ttk.Button(left_frame, text="📊 Показать статистику", command=self.show_statistics).pack(fill=tk.X, pady=5)
        
        # ===== Правая панель - Просмотр и фильтрация =====
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Фильтры
        filter_frame = ttk.LabelFrame(right_frame, text="🔍 Фильтрация", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Фильтр по типу
        type_filter_frame = ttk.Frame(filter_frame)
        type_filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(type_filter_frame, text="Тип тренировки:", width=15).pack(side=tk.LEFT, padx=(0, 5))
        self.filter_type_var = tk.StringVar()
        filter_type_combo = ttk.Combobox(type_filter_frame, textvariable=self.filter_type_var, 
                                          values=workout_types, state="readonly", width=15)
        filter_type_combo.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(type_filter_frame, text="Применить", command=self.filter_by_type, width=10).pack(side=tk.LEFT)
        
        # Фильтр по дате
        date_filter_frame = ttk.Frame(filter_frame)
        date_filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_filter_frame, text="Дата (ГГГГ-ММ-ДД):", width=15).pack(side=tk.LEFT, padx=(0, 5))
        self.filter_date_entry = ttk.Entry(date_filter_frame, width=15)
        self.filter_date_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(date_filter_frame, text="Применить", command=self.filter_by_date, width=10).pack(side=tk.LEFT)
        
        # Кнопка сброса фильтра
        ttk.Button(filter_frame, text="🔄 Сбросить фильтр", command=self.reset_filter).pack(fill=tk.X, pady=5)
        
        # Текущий фильтр
        self.current_filter_label = ttk.Label(filter_frame, text="Фильтр: все тренировки", 
                                               font=("Arial", 9), foreground="blue")
        self.current_filter_label.pack(pady=(5, 0))
        
        # Таблица тренировок
        table_frame = ttk.LabelFrame(right_frame, text="📋 Список тренировок", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Дата", "Тип тренировки", "Длительность")
        self.tree =
self.date - self Ресурсы и информация.
www.self.date


ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Тип тренировки", text="Тип тренировки")
        self.tree.heading("Длительность", text="Длительность")
        
        self.tree.column("Дата", width=100)
        self.tree.column("Тип тренировки", width=150)
        self.tree.column("Длительность", width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Подсказка
        hint_label = ttk.Label(right_frame, 
                               text="💡 Подсказка: Формат даты ГГГГ-ММ-ДД (например, 2024-03-15)\n"
                                    "   Длительность: положительное число (например, 30 или 45.5)", 
                               font=("Arial", 9), foreground="gray", justify=tk.CENTER)
        hint_label.pack(pady=(5, 0))

def main():
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()