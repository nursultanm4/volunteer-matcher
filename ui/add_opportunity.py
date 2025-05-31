import customtkinter as ctk
from config.db_config import get_connection
from CTkMessagebox import CTkMessagebox
from ui.utils import center_window
from tkinter import filedialog
from PIL import Image, ImageTk
from customtkinter import CTkImage

SKILLS_LIST = [
    "Программирование",
    "Помощь окружающей среде",
    "Дизайн",
    "Копирайтинг",
    "SMM",
    "Teamwork",
    "Лидерство",
    "Образование и наставничество",
    "Поддержка животных",
    "Работа с детьми",
    "Монтаж видео/аудио"
]

class AddOpportunityModal(ctk.CTkToplevel):
    def __init__(self, master, org_id, on_created_callback=None):
        super().__init__(master)
        self.org_id = org_id 
        self.on_created_callback = on_created_callback
        self.title("Новое объявление")
        center_window(self, 480, 700)  
        self.grab_set()  

        self.image_path = None  

        self.scrollable = ctk.CTkScrollableFrame(self, width=440, height=650)
        self.scrollable.pack(fill="both", expand=True, padx=0, pady=0)
        self.create_widgets()

    def create_widgets(self):
        self.scrollable.grid_columnconfigure(0, weight=1)

        def add_labeled_entry(row, label_text):
            label = ctk.CTkLabel(self.scrollable, text=label_text)
            label.grid(row=row, column=0, sticky="w", padx=20, pady=(10, 0))
            entry = ctk.CTkEntry(self.scrollable)
            entry.grid(row=row + 1, column=0, padx=20, pady=(0, 10), sticky="ew")
            return entry

        self.title_entry = add_labeled_entry(0, "Название возможности")

        desc_label = ctk.CTkLabel(self.scrollable, text="Описание")
        desc_label.grid(row=2, column=0, sticky="w", padx=20, pady=(10, 0))
        self.description_entry = ctk.CTkTextbox(self.scrollable, height=100)
        self.description_entry.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.city_entry = add_labeled_entry(4, "Город")
        self.date_entry = add_labeled_entry(6, "Дата (гггг-мм-дд)")

        skills_label = ctk.CTkLabel(self.scrollable, text="Требуемые навыки")
        skills_label.grid(row=8, column=0, sticky="w", padx=20, pady=(10, 0))
        self.skill_vars = {}
        skills_frame = ctk.CTkFrame(self.scrollable)
        skills_frame.grid(row=9, column=0, padx=20, pady=(0, 10), sticky="ew")
        for skill in SKILLS_LIST:
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(skills_frame, text=skill, variable=var)
            cb.pack(anchor="w")
            self.skill_vars[skill] = var

        self.image_label = ctk.CTkLabel(self.scrollable, text="Фото", width=120, height=120, corner_radius=10, fg_color="#dddddd")
        self.image_label.grid(row=10, column=0, pady=10)

        upload_button = ctk.CTkButton(self.scrollable, text="Загрузить фото", command=self.upload_image)
        upload_button.grid(row=11, column=0, pady=5)

        submit_btn = ctk.CTkButton(self.scrollable, text="Создать", command=self.submit_opportunity)
        submit_btn.grid(row=12, column=0, padx=20, pady=20)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path = file_path
            image = Image.open(file_path)
            image = image.resize((120, 120))
            photo = CTkImage(image)  
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo

    def submit_opportunity(self):
        title = self.title_entry.get()
        description = self.description_entry.get("0.0", "end").strip()
        city = self.city_entry.get()
        date = self.date_entry.get()

        if not all([title, description, city, date]):
            CTkMessagebox(title="Ошибка", message="Заполните все поля.", icon="warning")
            return

        selected_skills = [skill for skill, var in self.skill_vars.items() if var.get()]
        skills_str = ", ".join(selected_skills)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO opportunities (title, description, city, date, organization_id, profile_picture, skills)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (title, description, city, date, self.org_id, self.image_path, skills_str))
            cursor.fetchone()
            conn.commit()

            if self.on_created_callback:
                print("Calling on_created_callback...")  
                self.on_created_callback()

            cursor.close()
            conn.close()
            
            self.destroy()

        except Exception as e:
            CTkMessagebox(title="Ошибка БД", message=str(e), icon="cancel")
