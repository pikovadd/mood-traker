import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# константы
APP_NAME = "Трекер настроения"
DATA_FILE = "mood_data.json"
PROFILE_FILE = "profile.json"
MAX_COMMENT_LENGTH = 200

# кнопки навигации
nav_buttons_list = [
    ("помощь", "show_help_screen"),
    ("сегодня", "show_today_screen"),
    ("календарь", "show_history_screen"),
    ("аналитика", "show_analytics_screen")
]


# путь к файлу данных
def get_data_path():
    app_data = Path(os.path.expanduser("~")) / "AppData" / "Local" / "MoodTracker"
    app_data.mkdir(parents=True, exist_ok=True)
    return app_data


class MoodTrackerApp:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)

        # полноэкранный режим
        self.root.attributes('-fullscreen', True)

        # настройка размера и веса для адаптивности
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # переменная для отслеживания полноэкранного режима
        self.fullscreen = True
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.toggle_fullscreen)

        # хранилище данных
        self.data_path = get_data_path()
        self.profile_file = self.data_path / PROFILE_FILE
        self.data_file = self.data_path / DATA_FILE

        # текущие данные
        self.user_name = ""
        self.mood_records = []
        self.current_record_id = None

        # загрузка профиля
        self.load_profile()

        # отображение начального экрана или главного
        if self.user_name:
            self.show_main_screen()
        else:
            self.show_welcome_screen()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        return "break"

    # работа с данными
    def load_profile(self):
        # загрузка профиля пользователя
        try:
            if self.profile_file.exists():
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_name = data.get('name', '')
        except Exception:
            self.user_name = ""

    def save_profile(self):
        # сохранение профиля пользователя
        try:
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump({'name': self.user_name}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"ошибка сохранения профиля: {e}")

    def load_records(self):
        # загрузка записей из файла
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.mood_records = json.load(f)
            else:
                self.mood_records = []
        except Exception:
            self.mood_records = []

    def save_records(self):
        # сохранение записей в файл
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.mood_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("ошибка", f"не удалось сохранить данные: {e}")

    def get_records_for_period(self, days):
        # получение записей за указанное количество дней
        cutoff_date = datetime.now() - timedelta(days=days)
        result = []
        for record in self.mood_records:
            try:
                record_date = datetime.strptime(record['date'], "%Y-%m-%d %H:%M:%S")
                if record_date >= cutoff_date:
                    result.append(record)
            except ValueError:
                continue
        return result

    # экраны
    def clear_screen(self):
        # очистка главного окна
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_nav_bar(self):
        """создает навигационную панель"""
        nav_frame = tk.Frame(self.root, bg="#f0f0f0", height=50)
        nav_frame.pack(fill='x', pady=0)
        nav_frame.pack_propagate(False)

        # проходим по списку кнопок
        for text, method_name in nav_buttons_list:
            # получаем метод по имени
            command = getattr(self, method_name)

            btn = tk.Button(
                nav_frame,
                text=text,
                font=("Arial", 14),
                bg="#f0f0f0",
                bd=0,
                padx=20,
                pady=10,
                command=command
            )
            btn.pack(side='left', expand=True, fill='both')

        # кнопка выхода из полноэкранного режима
        exit_btn = tk.Button(
            nav_frame,
            text="✕",
            font=("Arial", 14),
            bg="#f0f0f0",
            bd=0,
            padx=20,
            pady=10,
            command=self.toggle_fullscreen
        )
        exit_btn.pack(side='right')

        return nav_frame

    def show_welcome_screen(self):
        # отображение начального экрана
        self.clear_screen()

        # фрейм для центрирования
        main_frame = tk.Frame(self.root, bg="#ffffff")
        main_frame.pack(expand=True, fill='both')

        # заголовок
        title_label = tk.Label(
            main_frame,
            text="как тебя зовут?",
            font=("Arial", 32, "bold"),
            bg="#ffffff",
            pady=30
        )
        title_label.pack()

        # поле ввода имени
        self.name_entry = tk.Entry(
            main_frame,
            font=("Arial", 24),
            width=20,
            justify='center',
            bd=0,
            relief='solid',
            highlightthickness=2,
            highlightcolor="#4CAF50"
        )
        self.name_entry.pack(pady=20, ipady=10)
        self.name_entry.focus()

        # кнопка "начать"
        start_btn = tk.Button(
            main_frame,
            text="начать",
            font=("Arial", 18, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=50,
            pady=15,
            relief='flat',
            cursor='hand2',
            command=self.on_start_click
        )
        start_btn.pack(pady=30)

        # информация о полноэкранном режиме
        info_label = tk.Label(
            main_frame,
            text="F11 - полноэкранный режим / Esc - выход",
            font=("Arial", 10),
            fg="gray",
            bg="#ffffff"
        )
        info_label.pack(side='bottom', pady=10)

        # обработка Enter
        self.root.bind('<Return>', lambda e: self.on_start_click())

    def on_start_click(self):
        # обработчик кнопки начать
        name = self.name_entry.get().strip()
        if name:
            self.user_name = name
            self.save_profile()
            self.show_main_screen()
        else:
            messagebox.showwarning("внимание", "пожалуйста, введите ваше имя")

    def show_main_screen(self):
        # отображение главного экрана
        self.clear_screen()
        self.load_records()

        # навигационная панель
        self.create_nav_bar()

        # основной контент
        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=40, pady=40)

        # приветствие
        greeting = tk.Label(
            content_frame,
            text=f"привет, {self.user_name}! :)",
            font=("Arial", 36, "bold"),
            bg="#ffffff"
        )
        greeting.pack(pady=20)

        question = tk.Label(
            content_frame,
            text="как твое настроение\nсегодня? :)",
            font=("Arial", 24),
            bg="#ffffff",
            justify='center'
        )
        question.pack(pady=20)

        # кнопки быстрого перехода
        btn_frame = tk.Frame(content_frame, bg="#ffffff")
        btn_frame.pack(pady=40)

        # создаем стильные кнопки
        buttons = [
            ("сегодня", "#2196F3", self.show_today_screen),
            ("календарь", "#FF9800", self.show_history_screen),
            ("аналитика", "#9C27B0", self.show_analytics_screen)
        ]

        for text, color, command in buttons:
            btn = tk.Button(
                btn_frame,
                text=text,
                font=("Arial", 18, "bold"),
                bg=color,
                fg="white",
                padx=60,
                pady=20,
                relief='flat',
                cursor='hand2',
                command=command
            )
            btn.pack(side='left', padx=20, expand=True, fill='x')

    def show_help_screen(self):
        # отображение раздела помощь
        self.clear_screen()
        self.load_records()

        # навигационная панель
        self.create_nav_bar()

        # основной контент
        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=40, pady=30)

        help_text = """краткая инструкция

1. как выбрать настроение:
   нажмите на кнопку "сегодня" и выберите один из вариантов

2. как добавить запись:
   выберите настроение -> нажмите "добавить заметку" -> 
   введите комментарий (до 200 символов) -> нажмите "сохранить"

3. где посмотреть историю:
   нажмите "календарь" -> список всех записей за последний месяц

4. как работает статистика:
   нажмите "аналитика" -> выберите период (неделя или месяц) -> 
   отобразится график

5. редактирование/удаление:
   нажмите на запись в календаре -> измените данные -> 
   нажмите "сохранить" или "удалить" """

        help_label = tk.Label(
            content_frame,
            text=help_text,
            font=("Arial", 16),
            bg="#ffffff",
            justify='left',
            pady=20
        )
        help_label.pack(expand=True)

    def show_today_screen(self):
        # отображение раздела сегодня
        self.clear_screen()
        self.load_records()

        # навигационная панель
        self.create_nav_bar()

        # основной контент
        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=40, pady=30)

        # заголовок
        title = tk.Label(
            content_frame,
            text="# как прошел день?",
            font=("Arial", 28, "bold"),
            bg="#ffffff"
        )
        title.pack(pady=20)

        # выбор настроения
        mood_frame = tk.Frame(content_frame, bg="#ffffff")
        mood_frame.pack(pady=30)

        # варианты настроения
        self.selected_mood = tk.StringVar(value="")

        moods = [
            ("отлично", "#4CAF50"),
            ("хорошо", "#8BC34A"),
            ("так себе", "#FFC107")
        ]

        for label, color in moods:
            rb = tk.Radiobutton(
                mood_frame,
                text=label,
                font=("Arial", 20),
                variable=self.selected_mood,
                value=label,
                bg=color,
                padx=30,
                pady=20,
                relief='ridge',
                bd=3,
                selectcolor='white',
                indicatoron=False,
                cursor='hand2'
            )
            rb.pack(side='left', padx=15, expand=True, fill='both')

        # кнопка добавления заметки
        add_btn = tk.Button(
            content_frame,
            text="добавить заметку",
            font=("Arial", 18, "bold"),
            bg="#2196F3",
            fg="white",
            padx=40,
            pady=15,
            relief='flat',
            cursor='hand2',
            command=self.show_add_comment_screen
        )
        add_btn.pack(pady=30)

    def show_add_comment_screen(self):
        # отображение окна добавления комментария
        if not self.selected_mood.get():
            messagebox.showwarning("внимание", "пожалуйста, выберите настроение")
            return

        # создаем новое окно
        comment_window = tk.Toplevel(self.root)
        comment_window.title("добавление заметки")
        comment_window.geometry("500x400")
        comment_window.resizable(False, False)
        comment_window.grab_set()

        # настройка центрирования окна
        comment_window.transient(self.root)

        # заголовок
        title = tk.Label(
            comment_window,
            text="опиши свой день",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=15)

        # текстовое поле
        text_area = tk.Text(
            comment_window,
            font=("Arial", 14),
            height=6,
            width=40,
            wrap='word',
            relief='solid',
            bd=2
        )
        text_area.pack(pady=15, padx=30)
        text_area.focus()

        # счетчик символов
        char_count = tk.Label(
            comment_window,
            text=f"0/{MAX_COMMENT_LENGTH}",
            font=("Arial", 12),
            fg="gray"
        )
        char_count.pack()

        def update_char_count(event=None):
            current = len(text_area.get("1.0", "end-1c"))
            char_count.config(text=f"{current}/{MAX_COMMENT_LENGTH}")
            if current > MAX_COMMENT_LENGTH:
                text_area.delete(f"{MAX_COMMENT_LENGTH + 1}.0", "end")

        text_area.bind('<KeyRelease>', update_char_count)

        # кнопки
        btn_frame = tk.Frame(comment_window)
        btn_frame.pack(pady=20)

        save_btn = tk.Button(
            btn_frame,
            text="сохранить",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=lambda: self.save_mood_record(
                text_area.get("1.0", "end-1c").strip(),
                comment_window
            )
        )
        save_btn.pack(side='left', padx=10)

        cancel_btn = tk.Button(
            btn_frame,
            text="отмена",
            font=("Arial", 14),
            bg="#f44336",
            fg="white",
            padx=30,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=comment_window.destroy
        )
        cancel_btn.pack(side='left', padx=10)

    def save_mood_record(self, comment, window):
        # сохранение записи о настроении
        mood = self.selected_mood.get()

        if not mood:
            messagebox.showwarning("внимание", "выберите настроение")
            return

        # проверка длины комментария
        if len(comment) > MAX_COMMENT_LENGTH:
            messagebox.showwarning("внимание", f"комментарий не может превышать {MAX_COMMENT_LENGTH} символов")
            return

        # создание записи
        record = {
            'id': datetime.now().strftime("%Y%m%d%H%M%S%f"),
            'mood': mood,
            'comment': comment,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.mood_records.append(record)
        self.save_records()

        window.destroy()
        messagebox.showinfo("успех", "запись сохранена!")

        # возврат на главный экран
        self.show_main_screen()

    def show_history_screen(self):
        # отображение раздела календарь/история
        self.clear_screen()
        self.load_records()

        # навигационная панель
        self.create_nav_bar()

        # основной контент
        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=40, pady=20)

        # заголовок
        title = tk.Label(
            content_frame,
            text="календарь настроения",
            font=("Arial", 28, "bold"),
            bg="#ffffff"
        )
        title.pack(pady=10)

        # подзаголовок
        subtitle = tk.Label(
            content_frame,
            text="(за последний месяц)",
            font=("Arial", 14),
            fg="gray",
            bg="#ffffff"
        )
        subtitle.pack()

        # контейнер для списка записей
        list_frame = tk.Frame(content_frame, bg="#ffffff")
        list_frame.pack(expand=True, fill='both', pady=10)

        # создаем Canvas с прокруткой
        canvas = tk.Canvas(list_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # отображение записей за последний месяц
        records = self.get_records_for_period(30)

        if not records:
            no_data = tk.Label(
                scrollable_frame,
                text="нет записей за последний месяц",
                font=("Arial", 16),
                fg="gray",
                bg="#ffffff"
            )
            no_data.pack(pady=40)
        else:
            # сортируем по дате (новые сверху)
            records.sort(key=lambda x: x.get('date', ''), reverse=True)

            for record in records:
                self.create_history_card(scrollable_frame, record)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_history_card(self, parent, record):
        # создание карточки записи в истории
        mood_colors = {
            "отлично": "#4CAF50",
            "хорошо": "#8BC34A",
            "так себе": "#FFC107"
        }

        mood = record.get('mood', '')
        color = mood_colors.get(mood, "#FFC107")

        # карточка
        card = tk.Frame(
            parent,
            bg="white",
            relief='ridge',
            bd=1,
            padx=15,
            pady=10
        )
        card.pack(fill='x', pady=5)

        # настроение и дата
        top_frame = tk.Frame(card, bg="white")
        top_frame.pack(fill='x')

        mood_label = tk.Label(
            top_frame,
            text=mood,
            font=("Arial", 16, "bold"),
            bg="white",
            fg=color
        )
        mood_label.pack(side='left')

        date_label = tk.Label(
            top_frame,
            text=record.get('date', '')[:16],
            font=("Arial", 12),
            bg="white",
            fg="gray"
        )
        date_label.pack(side='right')

        # комментарий
        comment = record.get('comment', '')
        if comment:
            comment_label = tk.Label(
                card,
                text=comment,
                font=("Arial", 12),
                bg="white",
                wraplength=600,
                justify='left'
            )
            comment_label.pack(anchor='w', pady=(5, 0))

        # кнопка для редактирования
        edit_btn = tk.Button(
            card,
            text="редактировать",
            font=("Arial", 12),
            bg="white",
            bd=0,
            fg="#2196F3",
            cursor='hand2',
            command=lambda r=record: self.show_edit_record_screen(r)
        )
        edit_btn.pack(anchor='e', pady=(5, 0))

    def show_edit_record_screen(self, record):
        # отображение окна редактирования записи
        # сохраняем ID текущей записи
        self.current_record_id = record.get('id')

        # создаем окно редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("внесенная запись")
        edit_window.geometry("500x450")
        edit_window.resizable(False, False)
        edit_window.grab_set()
        edit_window.transient(self.root)

        # заголовок
        title = tk.Label(
            edit_window,
            text="редактирование записи",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=15)

        # выбор настроения
        mood_frame = tk.Frame(edit_window)
        mood_frame.pack(pady=15)

        mood_label = tk.Label(
            mood_frame,
            text="настроение:",
            font=("Arial", 14)
        )
        mood_label.pack(side='left', padx=10)

        selected_mood_edit = tk.StringVar(value=record.get('mood', ''))

        moods = [
            "отлично",
            "хорошо",
            "так себе"
        ]

        for label in moods:
            rb = tk.Radiobutton(
                mood_frame,
                text=label,
                font=("Arial", 14),
                variable=selected_mood_edit,
                value=label,
                indicatoron=True,
                cursor='hand2'
            )
            rb.pack(side='left', padx=10)

        # текстовое поле для комментария
        comment_label = tk.Label(
            edit_window,
            text="комментарий:",
            font=("Arial", 14)
        )
        comment_label.pack(anchor='w', padx=30, pady=(15, 5))

        text_area = tk.Text(
            edit_window,
            font=("Arial", 14),
            height=4,
            width=45,
            wrap='word',
            relief='solid',
            bd=2
        )
        text_area.insert("1.0", record.get('comment', ''))
        text_area.pack(pady=5, padx=30)

        # кнопки
        btn_frame = tk.Frame(edit_window)
        btn_frame.pack(pady=20)

        save_btn = tk.Button(
            btn_frame,
            text="сохранить",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=25,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=lambda: self.update_record(
                record,
                selected_mood_edit.get(),
                text_area.get("1.0", "end-1c").strip(),
                edit_window
            )
        )
        save_btn.pack(side='left', padx=10)

        delete_btn = tk.Button(
            btn_frame,
            text="удалить",
            font=("Arial", 14, "bold"),
            bg="#f44336",
            fg="white",
            padx=25,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=lambda: self.delete_record(record, edit_window)
        )
        delete_btn.pack(side='left', padx=10)

        cancel_btn = tk.Button(
            btn_frame,
            text="отмена",
            font=("Arial", 14),
            bg="#9E9E9E",
            fg="white",
            padx=25,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=edit_window.destroy
        )
        cancel_btn.pack(side='left', padx=10)

    def update_record(self, record, mood, comment, window):
        # обновление записи
        if not mood:
            messagebox.showwarning("внимание", "выберите настроение")
            return

        if len(comment) > MAX_COMMENT_LENGTH:
            messagebox.showwarning("внимание", f"комментарий не может превышать {MAX_COMMENT_LENGTH} символов")
            return

        # находим запись и обновляем
        for r in self.mood_records:
            if r.get('id') == record.get('id'):
                r['mood'] = mood
                r['comment'] = comment
                break

        self.save_records()
        window.destroy()
        messagebox.showinfo("успех", "запись обновлена!")
        self.show_history_screen()

    def delete_record(self, record, window):
        # удаление записи
        if messagebox.askyesno("подтверждение", "вы уверены, что хотите удалить эту запись?"):
            self.mood_records = [r for r in self.mood_records if r.get('id') != record.get('id')]
            self.save_records()
            window.destroy()
            messagebox.showinfo("успех", "запись удалена!")
            self.show_history_screen()

    def show_analytics_screen(self):
        # отображение раздела аналитика
        self.clear_screen()
        self.load_records()

        # навигационная панель
        self.create_nav_bar()

        # основной контент
        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=40, pady=20)

        # заголовок
        title = tk.Label(
            content_frame,
            text="аналитика",
            font=("Arial", 28, "bold"),
            bg="#ffffff"
        )
        title.pack(pady=10)

        # выбор периода
        period_frame = tk.Frame(content_frame, bg="#ffffff")
        period_frame.pack(pady=15)

        period_label = tk.Label(
            period_frame,
            text="выбери период:",
            font=("Arial", 16),
            bg="#ffffff"
        )
        period_label.pack(side='left', padx=15)

        self.selected_period = tk.StringVar(value="неделя")

        week_btn = tk.Radiobutton(
            period_frame,
            text="неделя",
            font=("Arial", 16),
            variable=self.selected_period,
            value="неделя",
            bg="#ffffff",
            cursor='hand2',
            command=self.show_analytics_period
        )
        week_btn.pack(side='left', padx=15)

        month_btn = tk.Radiobutton(
            period_frame,
            text="месяц",
            font=("Arial", 16),
            variable=self.selected_period,
            value="месяц",
            bg="#ffffff",
            cursor='hand2',
            command=self.show_analytics_period
        )
        month_btn.pack(side='left', padx=15)

        # контейнер для графика
        self.analytics_container = tk.Frame(content_frame, bg="#ffffff")
        self.analytics_container.pack(expand=True, fill='both', pady=15)

        # отображение данных за неделю по умолчанию
        self.show_analytics_period()

    def show_analytics_period(self):
        # отображение статистики за выбранный период
        # очищаем контейнер
        for widget in self.analytics_container.winfo_children():
            widget.destroy()

        period = self.selected_period.get()
        days = 7 if period == "неделя" else 30

        records = self.get_records_for_period(days)

        if not records:
            no_data = tk.Label(
                self.analytics_container,
                text="нет данных за выбранный период",
                font=("Arial", 20),
                fg="gray",
                bg="#ffffff"
            )
            no_data.pack(expand=True)
            return

        # подсчет статистики
        mood_counts = {
            "отлично": 0,
            "хорошо": 0,
            "так себе": 0
        }

        for record in records:
            mood = record.get('mood', '')
            if mood in mood_counts:
                mood_counts[mood] += 1

        total = sum(mood_counts.values())

        # заголовок периода
        period_label = tk.Label(
            self.analytics_container,
            text=f"статистика за {period}",
            font=("Arial", 18, "bold"),
            bg="#ffffff"
        )
        period_label.pack(pady=5)

        # создание простой гистограммы
        chart_frame = tk.Frame(self.analytics_container, bg="#ffffff")
        chart_frame.pack(expand=True, fill='both', pady=15)

        # максимальное значение для масштабирования
        max_count = max(mood_counts.values()) if max(mood_counts.values()) > 0 else 1

        # цвета для настроений
        colors = {
            "отлично": "#4CAF50",
            "хорошо": "#8BC34A",
            "так себе": "#FFC107"
        }

        # создаем столбцы
        for mood, count in mood_counts.items():
            frame = tk.Frame(chart_frame, bg="#ffffff")
            frame.pack(side='left', expand=True, fill='both', padx=10)

            # высота столбца (макс 250px)
            height = int((count / max_count) * 200) if max_count > 0 else 0
            height = max(height, 10) if count > 0 else 0

            # столбец
            bar = tk.Frame(
                frame,
                bg=colors.get(mood, "#9E9E9E"),
                height=height,
                width=60
            )
            bar.pack(side='bottom', pady=5)

            # количество
            count_label = tk.Label(
                frame,
                text=str(count),
                font=("Arial", 16, "bold"),
                bg="#ffffff"
            )
            count_label.pack()

            # название
            mood_label = tk.Label(
                frame,
                text=mood,
                font=("Arial", 14),
                bg="#ffffff"
            )
            mood_label.pack()

        # общее количество записей
        total_label = tk.Label(
            self.analytics_container,
            text=f"всего записей: {total}",
            font=("Arial", 14),
            fg="gray",
            bg="#ffffff"
        )
        total_label.pack(pady=10)


def main():
    # точка входа в приложение
    root = tk.Tk()
    app = MoodTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
