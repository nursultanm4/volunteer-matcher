import customtkinter as ctk
from logic.auth import update_user_profile, get_user_profile
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

class ProfileForm(ctk.CTkToplevel):
    def __init__(self, master, user_data, on_close_callback=None, readonly=False):
        super().__init__(master)
        self.title("Дополнительная информация")
        self.geometry("500x550")
        self.scrollable = ctk.CTkScrollableFrame(self, width=480, height=680)
        self.scrollable.pack(fill="both", expand=True)
        self.container = self.scrollable
        self.transient(master)
        self.lift()
        self.grab_set()
        self.user_data = user_data
        self.on_close_callback = on_close_callback
        self.profile_image_path = None
        self.entries = {}
        self.placeholders = {}
        self.readonly = readonly
        self.create_widgets()
        self.load_profile_data()

    def create_widgets(self):
        role = self.user_data["role"]
        parent = self.container

        ctk.CTkLabel(parent, text="Дополнительная информация", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.image_label = ctk.CTkLabel(parent, text="Фото профиля", width=120, height=120, corner_radius=10, fg_color="#dddddd")
        self.image_label.pack(pady=10)

        upload_button = ctk.CTkButton(parent, text="Загрузить фото", command=self.upload_image)
        upload_button.pack(pady=5)
        if self.readonly:
            upload_button.configure(state="disabled")

        self.skill_vars = {}  

        if role == "volunteer":
            fields = {
                "name": "Имя",
                "age": "Возраст",
                "city": "Город",
                "phone": "Телефон",
                "skills": "Навыки и интересы",
                "availability": "Доступность (дни, часы)"
            }
        else:
            fields = {
                "city": "Город",
                "description": "Описание организации"
            }

        for field, label_text in fields.items():
            label = ctk.CTkLabel(parent, text=label_text)
            label.pack(anchor="w", padx=20, pady=(5, 0))

            frame = ctk.CTkFrame(parent)
            frame.pack(fill="x", padx=20, pady=(0, 10))

            if role == "volunteer" and field == "skills":
                for skill in SKILLS_LIST:
                    var = ctk.BooleanVar()
                    cb = ctk.CTkCheckBox(frame, text=skill, variable=var)
                    cb.pack(anchor="w")
                    if self.readonly:
                        cb.configure(state="disabled") 
                    self.skill_vars[skill] = var
                self.entries[field] = self.skill_vars 
            elif field in ["description", "availability"]:
                if self.readonly:
                    value = self.user_data.get(field, "")
                    widget = ctk.CTkLabel(frame, text=value if value else "—", text_color="gray", anchor="w", font=ctk.CTkFont(size=14))
                    widget.pack(fill="x", expand=True)
                    self.entries[field] = widget
                else:
                    widget = ctk.CTkTextbox(frame, height=60, wrap="word")
                    widget.bind("<FocusIn>", lambda e, w=widget, f=field: self.clear_placeholder(w, f))
                    widget.bind("<FocusOut>", lambda e, w=widget, f=field: self.set_placeholder(w, f))
                    widget.bind("<KeyRelease>", lambda e, w=widget: self.auto_resize_textbox(w))
                    widget.pack(fill="x", expand=True)
                    self.entries[field] = widget
                    self.placeholders[field] = label_text
            else:
                if self.readonly:
                    value = self.user_data.get(field, "")
                    widget = ctk.CTkLabel(frame, text=value if value else "—", text_color="gray", anchor="w", font=ctk.CTkFont(size=14))
                    widget.pack(fill="x", expand=True)
                    self.entries[field] = widget
                else:
                    widget = ctk.CTkEntry(frame)
                    widget.bind("<FocusIn>", lambda e, w=widget, f=field: self.clear_placeholder(w, f))
                    widget.bind("<FocusOut>", lambda e, w=widget, f=field: self.set_placeholder(w, f))
                    widget.pack(fill="x", expand=True)
                    self.entries[field] = widget
                    self.placeholders[field] = label_text

            if self.readonly:
                if isinstance(widget, ctk.CTkEntry):
                    widget.configure(state="disabled", text_color="gray")
                elif isinstance(widget, ctk.CTkTextbox):
                    widget.configure(state="disabled", text_color="gray")
                elif isinstance(widget, dict):  
                    for var in widget.values():
                        var.set(var.get())  
                elif isinstance(widget, ctk.CTkCheckBox):
                    widget.configure(state="disabled")

        self.save_button = ctk.CTkButton(parent, text="Сохранить", command=self.save_profile)
        self.save_button.pack(pady=20)

        if self.readonly:
            self.save_button.pack_forget()  

        self.message_label = ctk.CTkLabel(parent, text="")
        self.message_label.pack()

    def load_profile_data(self):
        profile_data = get_user_profile(self.user_data["role"], self.user_data["id"])
        profile_picture = profile_data.get("profile_picture")
        if profile_picture:
            try:
                image = Image.open(profile_picture)
                image = image.resize((200, 200))
                photo = CTkImage(image, size=(200,200))  
                self.image_label.configure(image=photo, text="")
                self.image_label.image = photo
            except Exception as e:
                print(f"Error loading profile picture: {e}")

        for field, widget in self.entries.items():
            value = profile_data.get(field)
            if field == "skills" and self.user_data["role"] == "volunteer":
                if value:
                    selected = [s.strip() for s in value.split(",")]
                    for skill, var in self.skill_vars.items():
                        var.set(skill in selected)
            elif value:
                if isinstance(widget, ctk.CTkTextbox):
                    widget.insert("1.0", value)
                    widget.configure(text_color="black")
                    self.auto_resize_textbox(widget)
                elif isinstance(widget, ctk.CTkEntry):
                    widget.insert(0, value)
                    widget.configure(text_color="black")
                elif isinstance(widget, ctk.CTkLabel):
                    widget.configure(text=value if value else "—")
            else:
                if isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
                    self.set_placeholder(widget, field)

    def set_placeholder(self, widget, field):
        current = widget.get("1.0", "end").strip() if isinstance(widget, ctk.CTkTextbox) else widget.get()
        if not current:
            placeholder = self.placeholders[field]
            if isinstance(widget, ctk.CTkTextbox):
                widget.insert("1.0", placeholder)
                widget.configure(text_color="gray")
            else:
                widget.insert(0, placeholder)
                widget.configure(text_color="gray")

    def clear_placeholder(self, widget, field):
        placeholder = self.placeholders[field]
        current = widget.get("1.0", "end").strip() if isinstance(widget, ctk.CTkTextbox) else widget.get()
        if current == placeholder:
            if isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")
            else:
                widget.delete(0, "end")
            widget.configure(text_color="black")

    def auto_resize_textbox(self, widget):
        content = widget.get("1.0", "end")
        lines = content.count("\n") + 1
        lines = max(3, min(lines, 12))
        widget.configure(height=lines * 20)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.profile_image_path = file_path
            image = Image.open(file_path)
            image = image.resize((200, 200))
            photo = CTkImage(image, size=(200,200))
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo

    def save_profile(self):
        updated_data = {}
        for field, widget in self.entries.items():
            if field == "skills" and self.user_data["role"] == "volunteer":
                selected_skills = [skill for skill, var in self.skill_vars.items() if var.get()]
                value = ", ".join(selected_skills)
            elif isinstance(widget, ctk.CTkTextbox):
                value = widget.get("1.0", "end").strip()
            else:
                value = widget.get().strip()
            if value and value != self.placeholders.get(field, ""):
                updated_data[field] = value

        if self.profile_image_path:
            updated_data["profile_picture"] = self.profile_image_path

        update_user_profile(self.user_data["role"], self.user_data["id"], updated_data)

        if self.on_close_callback:
            self.on_close_callback()

        self.destroy()
