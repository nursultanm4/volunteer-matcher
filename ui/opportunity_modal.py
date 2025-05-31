import customtkinter as ctk
from PIL import Image
from ui.profile_form import ProfileForm
from customtkinter import CTkImage 
from CTkMessagebox import CTkMessagebox
from logic.applications import record_opportunity_view
from logic.applications import get_applications_for_opportunity
from logic.auth import get_user_profile

def open_opportunity_modal(master, opportunity, user_data=None):
    overlay = ctk.CTkToplevel(master)
    overlay.attributes("-fullscreen", True)
    overlay.configure(fg_color="black")
    overlay.attributes("-alpha", 0.3)
    overlay.lift()

    modal = ctk.CTkToplevel(master)
    modal.title("Информация о возможности")
    modal.geometry("800x590")
    modal.transient(master)
    modal.grab_set()
    modal.lift()

    def close_modal():
        modal.destroy()
        overlay.destroy()

    modal.protocol("WM_DELETE_WINDOW", close_modal)

    container = ctk.CTkScrollableFrame(modal, width=760, height=520)
    container.pack(fill="both", expand=True, padx=20, pady=20)
    container.grid_columnconfigure(1, weight=1)

    img_path = opportunity.get("profile_picture") 
    if img_path:
        try:
            image = Image.open(img_path)
            image = image.resize((200, 200))
            photo = CTkImage(image, size=(200,200))
            image_label = ctk.CTkLabel(container, image=photo, text="")
            image_label.image = photo
        except Exception as e:
            print("Ошибка загрузки фото:", e)
            image_label = ctk.CTkLabel(container, text="Фото\nнет", width=120, height=120,
                                    corner_radius=10, fg_color="#dddddd", justify="center")
    else:
        image_label = ctk.CTkLabel(container, text="Фото\nнет", width=120, height=120,
                                corner_radius=10, fg_color="#dddddd", justify="center")

    image_label.grid(row=0, column=0, rowspan=3, padx=(0, 20), sticky="n")

    title_label = ctk.CTkLabel(container, text=opportunity["title"],
                               font=ctk.CTkFont(size=18, weight="bold"), anchor="w")
    title_label.grid(row=0, column=1, sticky="w", pady=(0, 5))

    meta_label = ctk.CTkLabel(container,
                              text=f"{opportunity['org']} • {opportunity['date']} • {opportunity['city']}",
                              font=ctk.CTkFont(size=13), text_color="gray")
    meta_label.grid(row=1, column=1, sticky="w", pady=(0, 10))

    desc_text = opportunity.get("description", "Описание отсутствует.")
    description = ctk.CTkLabel(container, text=desc_text,
                               font=ctk.CTkFont(size=13), wraplength=400, justify="left")
    description.grid(row=2, column=1, sticky="nw")

    skills = opportunity.get("skills")
    if skills:
        skills_label = ctk.CTkLabel(container, text=f"Навыки: {skills}", font=ctk.CTkFont(size=13), text_color="gray")
        skills_label.grid(row=3, column=1, sticky="nw", pady=(10, 0))
        next_row = 4
    else:
        next_row = 3

    if user_data:
        record_opportunity_view(user_data["id"], user_data["role"], opportunity["id"])

    def apply_action():
        from logic.applications import apply_to_opportunity
        apply_to_opportunity(user_data["id"], opportunity["id"])
        CTkMessagebox(title="Успех", message="Заявка отправлена!", icon="check")

    if user_data and user_data.get("role") == "volunteer":
        apply_btn = ctk.CTkButton(container, text="Податься", command=apply_action)
        apply_btn.grid(row=next_row, column=1, sticky="w", pady=(20, 0))

    if user_data and user_data.get("role") == "organization" and user_data["id"] == opportunity.get("organization_id"):
        stats_btn = ctk.CTkButton(container, text="Статистика", command=lambda: open_stats_window(opportunity))
        stats_btn.grid(row=next_row+1, column=1, sticky="w", pady=(10, 0))

    close_button = ctk.CTkButton(container, text="Закрыть", command=close_modal)
    close_button.grid(row=next_row, column=1, sticky="e", pady=(20, 0))

def open_stats_window(opportunity):
    stats_win = ctk.CTkToplevel()
    stats_win.title("Статистика подающихся волонтеров")
    stats_win.geometry("910x500")
    stats_win.grab_set()

    required_skills = [s.strip() for s in (opportunity.get("skills") or "").split(",") if s.strip()]
    ctk.CTkLabel(stats_win, text="Требуемые навыки:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 0))
    ctk.CTkLabel(stats_win, text=", ".join(required_skills) if required_skills else "—", text_color="gray").pack(pady=(0, 10))

    applications = get_applications_for_opportunity(opportunity["id"])

    perfect_matches = 0
    volunteer_list_frame = ctk.CTkScrollableFrame(stats_win, width=460, height=350)
    volunteer_list_frame.pack(pady=10, padx=10, fill="both", expand=True)

    for app in applications:
        volunteer = get_user_profile("volunteer", app["volunteer_id"])
        volunteer_skills = [s.strip() for s in (volunteer.get("skills") or "").split(",") if s.strip()]
        # check for perfect match
        if set(required_skills) and set(required_skills).issubset(set(volunteer_skills)):
            perfect_matches += 1
            match_text = "✅"
        else:
            match_text = ""
        ctk.CTkLabel(volunteer_list_frame, text=f"{volunteer.get('name', '—')} ({', '.join(volunteer_skills) if volunteer_skills else '—'}) {match_text}",
                     anchor="w", font=ctk.CTkFont(size=13)).pack(fill="x", padx=5, pady=2)

    ctk.CTkLabel(stats_win, text=f"Идеальные матчи: {perfect_matches}", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(10, 0))
