import customtkinter as ctk
from customtkinter import CTkScrollableFrame  
from ui.profile_form import ProfileForm
from ui.add_opportunity import AddOpportunityModal
from ui.opportunity_modal import *
from ui.opportunity_card import create_opportunity_card
from config.db_config import get_connection
from ui.add_opportunity import AddOpportunityModal
from ui.utils import center_window
from customtkinter import CTkImage
from logic.applications import get_applications_for_organization
from logic.applications import has_unseen_applications
from logic.applications import get_opportunity_views

class MainMenu(ctk.CTkFrame):
    def __init__(self, master, user_data):
        super().__init__(master)
        self.master = master
        self.user_data = user_data
        self.role = user_data["role"]
        self.filter_city = None
        self.filter_org = None
        self.pack(fill="both", expand=True)
        self.create_widgets()
        

    def create_widgets(self):
        ctk.CTkLabel(self, text=f"Добро пожаловать, {self.user_data['name']}!",
                     font=ctk.CTkFont(size=20)).pack(pady=20)

        ctk.CTkLabel(self, text="Заполни дополнительные поля для лучшего использования платформы!",
                     font=ctk.CTkFont(size=14), text_color="gray").pack(pady=5)

        top_buttons = ctk.CTkFrame(self)
        top_buttons.pack(pady=10)

        ctk.CTkButton(top_buttons, text="Профиль", command=self.open_profile_form).pack(side="left", padx=10)

        if (self.role == "organization"):
            ctk.CTkButton(top_buttons, text="Добавить объявление", command=self.open_add_opportunity).pack(side="left", padx=10)

        if self.role == "volunteer":
            filter_btn = ctk.CTkButton(top_buttons, text="Фильтр возможностей", command=self.open_filter_window)
            filter_btn.pack(side="left", padx=10)
            reset_btn = ctk.CTkButton(top_buttons, text="Сбросить фильтры", command=self.reset_filters)
            reset_btn.pack(side="left", padx=10)
            
        notif_color = "red" if (self.role == "organization" and has_unseen_applications(self.user_data["id"])) else None
        self.notif_btn = ctk.CTkButton(
            top_buttons,
            text="🔔 Уведомления",
            command=self.open_notifications,
            state="normal" if self.role == "organization" else "disabled",
            text_color=notif_color
        )
        self.notif_btn.pack(side="left", padx=10)

        self.opps_frame = CTkScrollableFrame(self, width=600, height=400)
        self.opps_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.load_opportunities()

        logout_btn = ctk.CTkButton(
            self,
            text="Выйти",
            command=self.logout,
            fg_color="#e57373",
            text_color="white",
            width=120
        )
        logout_btn.place(relx=1.0, rely=1.0, anchor="se", x=-30, y=-30)  

    def load_opportunities(self):
        print("Загружаем все возможности...") 

        for widget in self.opps_frame.winfo_children():
            widget.destroy()

        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT o.id, o.title, o.description, o.city, o.date, org.name, org.profile_picture, o.profile_picture, o.organization_id, o.skills
            FROM opportunities o
            JOIN organizations org ON o.organization_id = org.id
        """
        params = []
        where_clauses = []
        if self.filter_city:
            where_clauses.append("LOWER(o.city) LIKE %s")
            params.append(f"%{self.filter_city.lower()}%")
        if self.filter_org:
            where_clauses.append("LOWER(org.name) LIKE %s")
            params.append(f"%{self.filter_org.lower()}%")
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        query += " ORDER BY o.id DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        print("Найдено:", len(results))  
        cursor.close()
        conn.close()

        for row in results:
            opp = {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "city": row[3],
                "date": row[4],
                "org": row[5],
                "org_profile_picture": row[6],
                "profile_picture": row[7],
                "organization_id": row[8],  
                "skills": row[9],
            }
            views_count = get_opportunity_views(opp["id"])
            opp["views"] = views_count
            # only allow edit/delete for orgs and only for their own cards
            can_edit = (
                self.role == "organization"
                and self.user_data["id"] == opp["organization_id"]
            )
            card = create_opportunity_card(
                self.opps_frame,
                opp,
                self.open_opportunity_modal,
                self.edit_opportunity if can_edit else None,
                self.delete_opportunity if can_edit else None,
            )
            card.pack(fill="x", padx=10, pady=5)

    def open_profile_form(self):
        ProfileForm(self, self.user_data)

    def open_opportunity_modal(self, opportunity):
        print("Открываем подробности возможности:", opportunity["title"])  
        open_opportunity_modal(self.master, opportunity, self.user_data)

    def open_add_opportunity(self):
        print("Открываем окно создания объявления")  
        AddOpportunityModal(self, self.user_data["id"], on_created_callback=self.load_opportunities)

    def edit_opportunity(self, opportunity):
        class EditOpportunityModal(ctk.CTkToplevel):
            def __init__(self, master, opp, on_save_callback):
                super().__init__(master)
                self.opp = opp
                self.transient(master)
                self.lift()
                self.on_save_callback = on_save_callback
                self.title("Редактировать возможность")
                center_window(self, 700, 590)  
                self.grab_set()
 
                self.scrollable = ctk.CTkScrollableFrame(self, width=650, height=540)
                self.scrollable.pack(fill="both", expand=True, padx=0, pady=0)
                self.create_widgets()

            def create_widgets(self):
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

                self.title_entry = ctk.CTkEntry(self.scrollable, placeholder_text="Название", width=300)
                self.title_entry.insert(0, self.opp["title"])
                self.title_entry.pack(pady=10)

                self.description_entry = ctk.CTkTextbox(self.scrollable, height=100, width=300)
                self.description_entry.insert("1.0", self.opp["description"])
                self.description_entry.pack(pady=10)

                self.city_entry = ctk.CTkEntry(self.scrollable, placeholder_text="Город", width=300)
                self.city_entry.insert(0, self.opp["city"])
                self.city_entry.pack(pady=10)

                self.date_entry = ctk.CTkEntry(self.scrollable, placeholder_text="Дата (гггг-мм-дд)", width=300)
                self.date_entry.insert(0, self.opp["date"])
                self.date_entry.pack(pady=10)

                ctk.CTkLabel(self.scrollable, text="Требуемые навыки").pack(anchor="w", padx=20, pady=(10, 0))
                self.skill_vars = {}
                skills_frame = ctk.CTkFrame(self.scrollable)
                skills_frame.pack(fill="x", padx=20, pady=(0, 10))
                existing_skills = [s.strip() for s in (self.opp.get("skills") or "").split(",") if s.strip()]
                for skill in SKILLS_LIST:
                    var = ctk.BooleanVar(value=skill in existing_skills)
                    cb = ctk.CTkCheckBox(skills_frame, text=skill, variable=var)
                    cb.pack(anchor="w")
                    self.skill_vars[skill] = var

                self.image_path = self.opp.get("profile_picture")
                self.image_label = ctk.CTkLabel(self.scrollable, text="Фото", width=120, height=120, corner_radius=10, fg_color="#dddddd")
                self.image_label.pack(pady=10)
                if self.image_path:
                    try:
                        image = Image.open(self.image_path)
                        image = image.resize((120, 120))
                        photo = CTkImage(image)
                        self.image_label.configure(image=photo, text="")
                        self.image_label.image = photo
                    except Exception:
                        pass

                upload_button = ctk.CTkButton(self.scrollable, text="Загрузить новое фото", command=self.upload_image)
                upload_button.pack(pady=5)

                save_button = ctk.CTkButton(self.scrollable, text="Сохранить", command=self.save_changes)
                save_button.pack(pady=20)

            def upload_image(self):
                from tkinter import filedialog
                file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
                if file_path:
                    self.image_path = file_path
                    image = Image.open(file_path)
                    image = image.resize((120, 120))
                    photo = CTkImage(image)
                    self.image_label.configure(image=photo, text="")
                    self.image_label.image = photo

            def save_changes(self):
                updated_data = {
                    "title": self.title_entry.get(),
                    "description": self.description_entry.get("1.0", "end").strip(),
                    "city": self.city_entry.get(),
                    "date": self.date_entry.get(),
                    "profile_picture": self.image_path,
                    "skills": ", ".join([skill for skill, var in self.skill_vars.items() if var.get()])
                }
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE opportunities
                    SET title = %s, description = %s, city = %s, date = %s, profile_picture = %s, skills = %s
                    WHERE id = %s
                """, (
                    updated_data["title"],
                    updated_data["description"],
                    updated_data["city"],
                    updated_data["date"],
                    updated_data["profile_picture"],
                    updated_data["skills"],
                    self.opp["id"]
                ))
                conn.commit()
                cursor.close()
                conn.close()

                self.on_save_callback()
                self.destroy()

        EditOpportunityModal(self, opportunity, self.load_opportunities)


    def delete_opportunity(self, opportunity):
        def confirm_delete():
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM opportunities WHERE id = %s", (opportunity["id"],))
            conn.commit()
            cursor.close()
            conn.close()

            self.load_opportunities()
            confirm_window.destroy()

        confirm_window = ctk.CTkToplevel(self)
        confirm_window.title("Подтверждение удаления")
        center_window(confirm_window, 300, 150)  
        confirm_window.transient(self)
        confirm_window.lift()
        confirm_window.grab_set()

        ctk.CTkLabel(confirm_window, text="Вы уверены, что хотите удалить?", font=ctk.CTkFont(size=14)).pack(pady=20)
        ctk.CTkButton(confirm_window, text="Удалить", command=confirm_delete).pack(side="left", padx=20, pady=20)
        ctk.CTkButton(confirm_window, text="Отмена", command=confirm_window.destroy).pack(side="right", padx=20, pady=20)

    def open_notifications(self):
        if self.role != "organization":
            return

        notif_win = ctk.CTkToplevel(self)
        notif_win.title("Заявки волонтёров")
        notif_win.geometry("780x400")
        notif_win.transient(self)
        notif_win.lift()
        notif_win.grab_set()

        notif_frame = ctk.CTkScrollableFrame(notif_win, width=580, height=460)
        notif_frame.pack(fill="both", expand=True, padx=10, pady=10)

        applications = get_applications_for_organization(self.user_data["id"])
        self.notif_btn.configure(text_color="white")

        if not applications:
            ctk.CTkLabel(notif_frame, text="Нет новых заявок.").pack(pady=20)
            return

        for app in applications:
            row_frame = ctk.CTkFrame(notif_frame)
            row_frame.pack(fill="x", padx=10, pady=8)

            if app["profile_picture"]:
                try:
                    image = Image.open(app["profile_picture"])
                    image = image.resize((60, 60))
                    photo = CTkImage(image, size=(60, 60))
                    img_label = ctk.CTkLabel(row_frame, image=photo, text="")
                    img_label.image = photo
                except Exception:
                    img_label = ctk.CTkLabel(row_frame, text="Нет фото", width=60, height=60, fg_color="#eee", corner_radius=8)
            else:
                img_label = ctk.CTkLabel(row_frame, text="Нет фото", width=60, height=60, fg_color="#eee", corner_radius=8)
            img_label.pack(side="left", padx=10)
            img_label.bind("<Button-1>", lambda e, v_id=app["volunteer_id"]: self.open_volunteer_profile(v_id))

            info = f"{app['volunteer_name']} подался на: {app['opportunity_title']}"
            ctk.CTkLabel(row_frame, text=info, font=ctk.CTkFont(size=14)).pack(side="left", padx=10)

    def open_volunteer_profile(self, volunteer_id):
        from logic.auth import get_user_profile
        profile_data = get_user_profile("volunteer", volunteer_id)
        profile_data["role"] = "volunteer"
        ProfileForm(self, profile_data, readonly=True)

    def update_notification_color(self):
        if self.role == "organization":
            notif_color = "red" if has_unseen_applications(self.user_data["id"]) else "white"
            self.notif_btn.configure(text_color=notif_color)

    def open_filter_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Фильтр возможностей")
        win.geometry("350x220")
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(win, text="Город:").pack(pady=(20, 0))
        city_entry = ctk.CTkEntry(win)
        city_entry.pack(pady=5)

        ctk.CTkLabel(win, text="Название организации:").pack(pady=(10, 0))
        org_entry = ctk.CTkEntry(win)
        org_entry.pack(pady=5)

        def apply_filter():
            self.filter_city = city_entry.get().strip() or None
            self.filter_org = org_entry.get().strip() or None
            win.destroy()
            self.load_opportunities()

        ctk.CTkButton(win, text="Поиск", command=apply_filter).pack(pady=20)

    def reset_filters(self):
        self.filter_city = None
        self.filter_org = None
        self.load_opportunities()

    def logout(self):
        self.master.clear_frame()
        self.master.show_login()