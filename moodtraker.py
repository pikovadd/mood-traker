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

        self.root.geometry("1100x700")
        self.root.resizable(False, False)

        # загружаем картинки для настроений
        self.mood_images = {}
        try:
            self.mood_images["отлично"] = tk.PhotoImage(file="happy.png")
            self.mood_images["хорошо"] = tk.PhotoImage(file="good.png")
            self.mood_images["так себе"] = tk.PhotoImage(file="okay.png")
        except Exception as e:
            print(f"не удалось загрузить картинки: {e}")

        # хранилище данных
        self.data_path = get_data_path()
        self.profile_file = self.data_path / PROFILE_FILE
        self.data_file = self.data_path / DATA_FILE

        # текущие данные
        self.user_name = ""
        self.mood_records = []
        self.current_record = None

        # загрузка профиля
        self.load_profile()

        # отображение начального экрана или главного
        if self.user_name:
            self.show_main_screen()
        else:
            self.show_welcome_screen()

    # работа с данными
    def load_profile(self):
        try:
            if self.profile_file.exists():
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_name = data.get('name', '')
        except Exception:
            self.user_name = ""

    def save_profile(self):
        try:
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump({'name': self.user_name}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"ошибка сохранения профиля: {e}")

    def load_records(self):
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.mood_records = json.load(f)
            else:
                self.mood_records = []
        except Exception:
            self.mood_records = []

    def save_records(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.mood_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("ошибка", f"не удалось сохранить данные: {e}")

    def get_records_for_period(self, days):
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
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_nav_bar(self):
        nav_frame = tk.Frame(self.root, bg="#f0f0f0", height=50)
        nav_frame.pack(fill='x', pady=0)
        nav_frame.pack_propagate(False)

        for text, method_name in nav_buttons_list:
            command = getattr(self, method_name)
            btn = tk.Button(
                nav_frame,
                text=text,
                font=("Arial", 12),
                bg="#f0f0f0",
                bd=0,
                padx=15,
                pady=8,
                command=command
            )
            btn.pack(side='left', expand=True, fill='both')

        return nav_frame

    def create_style_button(self, parent, text, color, command):
        btn = tk.Button(
            parent,
            text=text,
            font=("Arial", 14, "bold"),
            bg=color,
            fg="white",
            padx=30,
            pady=12,
            relief='flat',
            cursor='hand2',
            command=command
        )
        return btn

    def show_welcome_screen(self):
        self.clear_screen()

        main_frame = tk.Frame(self.root, bg="#ffffff")
        main_frame.pack(expand=True, fill='both')

        title_label = tk.Label(
            main_frame,
            text="как тебя зовут?",
            font=("Arial", 24, "bold"),
            bg="#ffffff",
            pady=30
        )
        title_label.pack()

        self.name_entry = tk.Entry(
            main_frame,
            font=("Arial", 18),
            width=20,
            justify='center',
            bd=0,
            relief='solid',
            highlightthickness=2,
            highlightcolor="#4CAF50"
        )
        self.name_entry.pack(pady=20, ipady=8)
        self.name_entry.focus()

        start_btn = tk.Button(
            main_frame,
            text="начать",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=40,
            pady=12,
            relief='flat',
            cursor='hand2',
            command=self.on_start_click
        )
        start_btn.pack(pady=30)

        self.root.bind('<Return>', lambda e: self.on_start_click())

    def on_start_click(self):
        name = self.name_entry.get().strip()
        if name:
            self.user_name = name.title()
            self.save_profile()
            self.show_main_screen()
        else:
            messagebox.showwarning("внимание", "пожалуйста, введите ваше имя")

    def show_main_screen(self):
        self.clear_screen()
        self.load_records()

        self.create_nav_bar()

        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=20, pady=20)

        greeting = tk.Label(
            content_frame,
            text=f"привет, {self.user_name}! :)",
            font=("Arial", 28, "bold"),
            bg="#ffffff"
        )
        greeting.pack(pady=15)

        question = tk.Label(
            content_frame,
            text="как твое настроение\nсегодня? :)",
            font=("Arial", 18),
            bg="#ffffff",
            justify='center'
        )
        question.pack(pady=15)

        btn_frame = tk.Frame(content_frame, bg="#ffffff")
        btn_frame.pack(pady=25)

        buttons = [
            ("сегодня", "#2196F3", self.show_today_screen),
            ("календарь", "#FF9800", self.show_history_screen),
            ("аналитика", "#9C27B0", self.show_analytics_screen)
        ]

        for text, color, command in buttons:
            btn = self.create_style_button(btn_frame, text, color, command)
            btn.pack(side='left', padx=10, expand=True, fill='x')

    def show_help_screen(self):
        self.clear_screen()
        self.load_records()

        self.create_nav_bar()

        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=20, pady=15)

        back_btn = tk.Button(
            content_frame,
            text="← назад",
            font=("Arial", 12),
            bg="#9E9E9E",
            fg="white",
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self.show_main_screen
        )
        back_btn.pack(anchor='nw', pady=(0, 10))

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
            font=("Arial", 12),
            bg="#ffffff",
            justify='left',
            pady=10
        )
        help_label.pack(expand=True)

    def show_today_screen(self):
        self.clear_screen()
        self.load_records()

        self.create_nav_bar()

        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=20, pady=15)

        title = tk.Label(
            content_frame,
            text="# как прошел день?",
            font=("Arial", 22, "bold"),
            bg="#ffffff"
        )
        title.pack(pady=15)

        mood_frame = tk.Frame(content_frame, bg="#ffffff")
        mood_frame.pack(pady=20)

        self.selected_mood = tk.StringVar(value="")

        moods = [
            ("отлично", "#4CAF50"),
            ("хорошо", "#8BC34A"),
            ("так себе", "#FFC107")
        ]

        for label, color in moods:
            frame = tk.Frame(mood_frame, bg=color, relief='ridge', bd=3, padx=15, pady=10)
            frame.pack(side='left', padx=10, expand=True, fill='both')

            if label in self.mood_images:
                img_label = tk.Label(frame, image=self.mood_images[label], bg=color)
                img_label.pack(pady=5)
            else:
                text_label = tk.Label(frame, text=label, font=("Arial", 16), bg=color)
                text_label.pack(pady=5)

            rb = tk.Radiobutton(
                frame,
                text=label,
                font=("Arial", 12, "bold"),
                variable=self.selected_mood,
                value=label,
                bg=color,
                fg="white",
                selectcolor=color,
                indicatoron=True,
                cursor='hand2'
            )
            rb.pack(pady=5)

        add_btn = tk.Button(
            content_frame,
            text="добавить заметку",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white",
            padx=30,
            pady=12,
            relief='flat',
            cursor='hand2',
            command=self.show_add_comment_screen
        )
        add_btn.pack(pady=20)

    def show_add_comment_screen(self):
        if not self.selected_mood.get():
            messagebox.showwarning("внимание", "пожалуйста, выберите настроение")
            return

        self.clear_screen()
        self.load_records()

        self.create_nav_bar()

        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=20, pady=15)

        back_btn = tk.Button(
            content_frame,
            text="← назад",
            font=("Arial", 12),
            bg="#9E9E9E",
            fg="white",
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self.show_today_screen
        )
        back_btn.pack(anchor='nw', pady=(0, 10))

        title = tk.Label(
            content_frame,
            text="опиши свой день",
            font=("Arial", 16, "bold"),
            bg="#ffffff"
        )
        title.pack(pady=12)

        text_area = tk.Text(
            content_frame,
            font=("Arial", 12),
            height=5,
            width=40,
            wrap='word',
            relief='solid',
            bd=2
        )
        text_area.pack(pady=10, padx=20)
        text_area.focus()

        char_count = tk.Label(
            content_frame,
            text=f"0/{MAX_COMMENT_LENGTH}",
            font=("Arial", 10),
            fg="gray",
            bg="#ffffff"
        )
        char_count.pack()

        def update_char_count(event=None):
            current = len(text_area.get("1.0", "end-1c"))
            char_count.config(text=f"{current}/{MAX_COMMENT_LENGTH}")
            if current > MAX_COMMENT_LENGTH:
                text_area.delete(f"{MAX_COMMENT_LENGTH + 1}.0", "end")

        text_area.bind('<KeyRelease>', update_char_count)

        btn_frame = tk.Frame(content_frame, bg="#ffffff")
        btn_frame.pack(pady=20)

        save_btn = tk.Button(
            btn_frame,
            text="сохранить",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=lambda: self.save_mood_record(
                text_area.get("1.0", "end-1c").strip()
            )
        )
        save_btn.pack(side='left', padx=10)

        cancel_btn = tk.Button(
            btn_frame,
            text="отмена",
            font=("Arial", 12),
            bg="#9E9E9E",
            fg="white",
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self.show_today_screen
        )
        cancel_btn.pack(side='left', padx=10)

    def save_mood_record(self, comment):
        mood = self.selected_mood.get()

        if not mood:
            messagebox.showwarning("внимание", "выберите настроение")
            return

        if len(comment) > MAX_COMMENT_LENGTH:
            messagebox.showwarning("внимание", f"комментарий не может превышать {MAX_COMMENT_LENGTH} символов")
            return

        record = {
            'id': datetime.now().strftime("%Y%m%d%H%M%S%f"),
            'mood': mood,
            'comment': comment,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.mood_records.append(record)
        self.save_records()

        messagebox.showinfo("успех", "запись сохранена!")
        self.show_main_screen()

    def show_history_screen(self):
        self.clear_screen()
        self.load_records()

        self.create_nav_bar()

        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=20, pady=10)

        title = tk.Label(
            content_frame,
            text="календарь настроения",
            font=("Arial", 22, "bold"),
            bg="#ffffff"
        )
        title.pack(pady=8)

        subtitle = tk.Label(
            content_frame,
            text="(за последний месяц)",
            font=("Arial", 12),
            fg="gray",
            bg="#ffffff"
        )
        subtitle.pack()

        list_frame = tk.Frame(content_frame, bg="#ffffff")
        list_frame.pack(expand=True, fill='both', pady=8)

        canvas = tk.Canvas(list_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        records = self.get_records_for_period(30)

        if not records:
            no_data = tk.Label(
                scrollable_frame,
                text="нет записей за последний месяц",
                font=("Arial", 14),
                fg="gray",
                bg="#ffffff"
            )
            no_data.pack(pady=30)
        else:
            records.sort(key=lambda x: x.get('date', ''), reverse=True)
            for record in records:
                self.create_history_card(scrollable_frame, record)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_history_card(self, parent, record):
        mood_colors = {
            "отлично": "#4CAF50",
            "хорошо": "#8BC34A",
            "так себе": "#FFC107"
        }

        mood = record.get('mood', '')
        color = mood_colors.get(mood, "#FFC107")

        card = tk.Frame(
            parent,
            bg="white",
            relief='ridge',
            bd=1,
            padx=10,
            pady=8
        )
        card.pack(fill='x', pady=3)

        top_frame = tk.Frame(card, bg="white")
        top_frame.pack(fill='x')

        left_frame = tk.Frame(top_frame, bg="white")
        left_frame.pack(side='left')

        if mood in self.mood_images:
            img = tk.Label(left_frame, image=self.mood_images[mood], bg="white")
            img.pack(side='left')

        mood_label = tk.Label(
            left_frame,
            text=mood,
            font=("Arial", 14, "bold"),
            bg="white",
            fg=color
        )
        mood_label.pack(side='left', padx=(5, 0))

        date_label = tk.Label(
            top_frame,
            text=record.get('date', '')[:16],
            font=("Arial", 10),
            bg="white",
            fg="gray"
        )
        date_label.pack(side='right')

        comment = record.get('comment', '')
        if comment:
            comment_label = tk.Label(
                card,
                text=comment,
                font=("Arial", 10),
                bg="white",
                wraplength=600,
                justify='left'
            )
            comment_label.pack(anchor='w', pady=(3, 0))

        edit_btn = tk.Button(
            card,
            text="редактировать",
            font=("Arial", 10),
            bg="white",
            bd=0,
            fg="#2196F3",
            cursor='hand2',
            command=lambda r=record: self.show_edit_record_screen(r)
        )
        edit_btn.pack(anchor='e', pady=(3, 0))

    def show_edit_record_screen(self, record):
        self.current_record = record

        self.clear_screen()
        self.load_records()

        self.create_nav_bar()

        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=20, pady=15)

        back_btn = tk.Button(
            content_frame,
            text="← назад",
            font=("Arial", 12),
            bg="#9E9E9E",
            fg="white",
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self.show_history_screen
        )
        back_btn.pack(anchor='nw', pady=(0, 10))

        title = tk.Label(
            content_frame,
            text="редактирование записи",
            font=("Arial", 16, "bold"),
            bg="#ffffff"
        )
        title.pack(pady=12)

        mood_frame = tk.Frame(content_frame, bg="#ffffff")
        mood_frame.pack(pady=10)

        mood_label = tk.Label(
            mood_frame,
            text="настроение:",
            font=("Arial", 12),
            bg="#ffffff"
        )
        mood_label.pack(side='left', padx=8)

        selected_mood_edit = tk.StringVar(value=record.get('mood', ''))

        moods = ["отлично", "хорошо", "так себе"]

        for label in moods:
            rb = tk.Radiobutton(
                mood_frame,
                text=label,
                font=("Arial", 12),
                variable=selected_mood_edit,
                value=label,
                bg="#ffffff",
                indicatoron=True,
                cursor='hand2'
            )
            rb.pack(side='left', padx=8)

        comment_label = tk.Label(
            content_frame,
            text="комментарий:",
            font=("Arial", 12),
            bg="#ffffff"
        )
        comment_label.pack(anchor='w', padx=20, pady=(10, 5))

        text_area = tk.Text(
            content_frame,
            font=("Arial", 12),
            height=4,
            width=40,
            wrap='word',
            relief='solid',
            bd=2
        )
        text_area.insert("1.0", record.get('comment', ''))
        text_area.pack(pady=5, padx=20)
        text_area.focus()

        btn_frame = tk.Frame(content_frame, bg="#ffffff")
        btn_frame.pack(pady=20)

        save_btn = tk.Button(
            btn_frame,
            text="сохранить",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=lambda: self.update_record(
                record,
                selected_mood_edit.get(),
                text_area.get("1.0", "end-1c").strip()
            )
        )
        save_btn.pack(side='left', padx=10)

        delete_btn = tk.Button(
            btn_frame,
            text="удалить",
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=lambda: self.delete_record(record)
        )
        delete_btn.pack(side='left', padx=10)

        cancel_btn = tk.Button(
            btn_frame,
            text="отмена",
            font=("Arial", 12),
            bg="#9E9E9E",
            fg="white",
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self.show_history_screen
        )
        cancel_btn.pack(side='left', padx=10)

    def update_record(self, record, mood, comment):
        if not mood:
            messagebox.showwarning("внимание", "выберите настроение")
            return

        if len(comment) > MAX_COMMENT_LENGTH:
            messagebox.showwarning("внимание", f"комментарий не может превышать {MAX_COMMENT_LENGTH} символов")
            return

        for r in self.mood_records:
            if r.get('id') == record.get('id'):
                r['mood'] = mood
                r['comment'] = comment
                break

        self.save_records()
        messagebox.showinfo("успех", "запись обновлена!")
        self.show_history_screen()

    def delete_record(self, record):
        if messagebox.askyesno("подтверждение", "вы уверены, что хотите удалить эту запись?"):
            self.mood_records = [r for r in self.mood_records if r.get('id') != record.get('id')]
            self.save_records()
            messagebox.showinfo("успех", "запись удалена!")
            self.show_history_screen()

    def show_analytics_screen(self):
        self.clear_screen()
        self.load_records()

        self.create_nav_bar()

        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(expand=True, fill='both', padx=20, pady=10)

        title = tk.Label(
            content_frame,
            text="аналитика",
            font=("Arial", 22, "bold"),
            bg="#ffffff"
        )
        title.pack(pady=8)

        period_frame = tk.Frame(content_frame, bg="#ffffff")
        period_frame.pack(pady=10)

        period_label = tk.Label(
            period_frame,
            text="выбери период:",
            font=("Arial", 12),
            bg="#ffffff"
        )
        period_label.pack(side='left', padx=10)

        self.selected_period = tk.StringVar(value="неделя")

        week_btn = tk.Radiobutton(
            period_frame,
            text="неделя",
            font=("Arial", 12),
            variable=self.selected_period,
            value="неделя",
            bg="#ffffff",
            cursor='hand2',
            command=self.show_analytics_period
        )
        week_btn.pack(side='left', padx=10)

        month_btn = tk.Radiobutton(
            period_frame,
            text="месяц",
            font=("Arial", 12),
            variable=self.selected_period,
            value="месяц",
            bg="#ffffff",
            cursor='hand2',
            command=self.show_analytics_period
        )
        month_btn.pack(side='left', padx=10)

        self.analytics_container = tk.Frame(content_frame, bg="#ffffff")
        self.analytics_container.pack(expand=True, fill='both', pady=10)

        self.show_analytics_period()

    def show_analytics_period(self):
        for widget in self.analytics_container.winfo_children():
            widget.destroy()

        period = self.selected_period.get()
        days = 7 if period == "неделя" else 30

        records = self.get_records_for_period(days)

        if not records:
            no_data = tk.Label(
                self.analytics_container,
                text="нет данных за выбранный период",
                font=("Arial", 16),
                fg="gray",
                bg="#ffffff"
            )
            no_data.pack(expand=True)
            return

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

        period_label = tk.Label(
            self.analytics_container,
            text=f"статистика за {period}",
            font=("Arial", 14, "bold"),
            bg="#ffffff"
        )
        period_label.pack(pady=5)

        chart_frame = tk.Frame(self.analytics_container, bg="#ffffff")
        chart_frame.pack(expand=True, fill='both', pady=10)

        max_count = max(mood_counts.values()) if max(mood_counts.values()) > 0 else 1

        colors = {
            "отлично": "#4CAF50",
            "хорошо": "#8BC34A",
            "так себе": "#FFC107"
        }

        for mood, count in mood_counts.items():
            frame = tk.Frame(chart_frame, bg="#ffffff")
            frame.pack(side='left', expand=True, fill='both', padx=8)

            height = int((count / max_count) * 150) if max_count > 0 else 0
            height = max(height, 10) if count > 0 else 0

            bar = tk.Frame(
                frame,
                bg=colors.get(mood, "#9E9E9E"),
                height=height,
                width=50
            )
            bar.pack(side='bottom', pady=3)

            count_label = tk.Label(
                frame,
                text=str(count),
                font=("Arial", 12, "bold"),
                bg="#ffffff"
            )
            count_label.pack()

            mood_label = tk.Label(
                frame,
                text=mood,
                font=("Arial", 11),
                bg="#ffffff"
            )
            mood_label.pack()

        total_label = tk.Label(
            self.analytics_container,
            text=f"всего записей: {total}",
            font=("Arial", 12),
            fg="gray",
            bg="#ffffff"
        )
        total_label.pack(pady=8)


def main():
    root = tk.Tk()
    app = MoodTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
