import customtkinter as ctk
from logic.auth import login_user, register_user


class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, switch_to_register, switch_to_main):
        super().__init__(master)
        self.master = master
        self.switch_to_register = switch_to_register
        self.switch_to_main = switch_to_main

        self.label = ctk.CTkLabel(self, text="Вход", font=ctk.CTkFont(size=32, weight="bold"))
        self.label.pack(pady=(40, 24))

        self.phone_entry = ctk.CTkEntry(self, placeholder_text="Телефон", font=ctk.CTkFont(size=18), width=320, height=48)
        self.phone_entry.pack(pady=12)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Пароль", show="*", font=ctk.CTkFont(size=18), width=320, height=48)
        self.password_entry.pack(pady=12)

        self.role_var = ctk.StringVar(value="volunteer")
        radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        radio_frame.pack(pady=10)
        ctk.CTkRadioButton(radio_frame, text="Волонтёр", variable=self.role_var, value="volunteer", font=ctk.CTkFont(size=16)).pack(side="left", padx=16)
        ctk.CTkRadioButton(radio_frame, text="Организация", variable=self.role_var, value="organization", font=ctk.CTkFont(size=16)).pack(side="left", padx=16)

        self.login_button = ctk.CTkButton(self, text="Войти", font=ctk.CTkFont(size=18, weight="bold"), width=320, height=48, command=self.attempt_login)
        self.login_button.pack(pady=24)

        self.register_link = ctk.CTkButton(
            self,
            text="Нет аккаунта? Зарегистрироваться",
            command=self.switch_to_register,
            fg_color="transparent",
            text_color="blue",
            hover=False,
            font=ctk.CTkFont(size=15, underline=True),
            width=320,
            height=36
        )
        self.register_link.pack(pady=(0, 20))

        self.message = ctk.CTkLabel(self, text="", text_color="red", font=ctk.CTkFont(size=15))
        self.message.pack(pady=5)

    def attempt_login(self):
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if not phone or not password:
            self.message.configure(text="⚠️ Заполните все поля", text_color="orange")
            return

        success, result = login_user(role, phone, password)
        if success:
            self.switch_to_main(result, just_registered=False)  
        else:
            self.message.configure(text=result, text_color="red")


class RegisterScreen(ctk.CTkFrame):
    def __init__(self, master, switch_to_login, switch_to_main):
        super().__init__(master)
        self.master = master
        self.switch_to_login = switch_to_login
        self.switch_to_main = switch_to_main

        self.label = ctk.CTkLabel(self, text="Регистрация", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=10)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Имя")
        self.name_entry.pack(pady=5)

        self.phone_entry = ctk.CTkEntry(self, placeholder_text="Телефон")
        self.phone_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Пароль", show="*")
        self.password_entry.pack(pady=5)

        self.role_var = ctk.StringVar(value="volunteer")
        ctk.CTkRadioButton(self, text="Волонтёр", variable=self.role_var, value="volunteer").pack()
        ctk.CTkRadioButton(self, text="Организация", variable=self.role_var, value="organization").pack()

        self.register_button = ctk.CTkButton(self, text="Зарегистрироваться", command=self.attempt_register)
        self.register_button.pack(pady=10)

        self.login_link = ctk.CTkButton(
            self,
            text="Уже есть аккаунт? Войти",
            command=self.switch_to_login,
            fg_color="transparent",
            text_color="blue",
            hover=False
        )
        self.login_link.pack()

        self.message = ctk.CTkLabel(self, text="", text_color="red")
        self.message.pack(pady=5)

    def attempt_register(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if not all([name, phone, password]):
            self.message.configure(text="⚠️ Заполните все поля")
            return
        if len(password) < 8:
            self.message.configure(text="⚠️ Пароль должен быть не менее 8 символов")
            return

        success, result = register_user(role, name, phone, password)
        if success:
            self.message.configure(text="✅ Успешная регистрация", text_color="green")
            self.switch_to_main(result, just_registered=True)
        else:
            self.message.configure(text=f"❌ {result}", text_color="red")
