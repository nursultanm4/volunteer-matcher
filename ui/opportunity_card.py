import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage

def bind_all_children(widget, callback, exclude_widgets=None):
    if exclude_widgets is None:
        exclude_widgets = set()
    if widget not in exclude_widgets:
        widget.bind("<Button-1>", callback)
        for child in widget.winfo_children():
            bind_all_children(child, callback, exclude_widgets)

def create_opportunity_card(parent, opp, on_click_callback, on_edit_callback, on_delete_callback):
    frame = ctk.CTkFrame(parent, width=480, height=140, corner_radius=16, fg_color="#f9f9f9")
    frame.pack_propagate(False)

    if opp.get("profile_picture"):
        try:
            image = Image.open(opp["profile_picture"])
            image = image.resize((110, 110))
            photo = CTkImage(image, size=(110, 110))
            img_label = ctk.CTkLabel(frame, image=photo, text="", width=110, height=110, corner_radius=12)
            img_label.image = photo
        except Exception:
            img_label = ctk.CTkLabel(frame, text="Нет фото", width=110, height=110, fg_color="#eee", corner_radius=12)
    else:
        img_label = ctk.CTkLabel(frame, text="Нет фото", width=110, height=110, fg_color="#eee", corner_radius=12)
    img_label.pack(side="left", padx=18, pady=15)

    content_frame = ctk.CTkFrame(frame, fg_color="transparent")
    content_frame.pack(side="left", fill="both", expand=True, padx=0, pady=0)

    title = ctk.CTkLabel(content_frame, text=opp.get("title", "Без названия"),
        font=ctk.CTkFont(size=15, weight="bold"), anchor="w")
    description_text = opp.get("description", "")
    if len(description_text) > 90:
        description_text = description_text[:87] + "..."
    description = ctk.CTkLabel(content_frame, text=description_text,
        font=ctk.CTkFont(size=12), wraplength=320, anchor="w", justify="left")
    subtitle = ctk.CTkLabel(content_frame,
        text=f"{opp.get('org', '')} — {opp.get('date', '')}",
        font=ctk.CTkFont(size=11), text_color="gray", anchor="w")

    views = opp.get("views", 0)
    views_label = ctk.CTkLabel(content_frame, text=f"{views} Views",
        font=ctk.CTkFont(size=11), text_color="gray")
    views_label.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)

    title.pack(anchor="w", padx=0, pady=(8, 0))
    description.pack(anchor="w", padx=0, pady=(2, 0))
    subtitle.pack(anchor="w", padx=0, pady=(2, 0))

    if opp.get("skills"):
        skills_label = ctk.CTkLabel(content_frame, text=f"Навыки: {opp['skills']}",
            font=ctk.CTkFont(size=11), text_color="gray")
        skills_label.pack(anchor="w", padx=0, pady=(0, 4))

    if on_edit_callback and on_delete_callback:
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        edit_button = ctk.CTkButton(button_frame, text="✏️", width=36, command=lambda: on_edit_callback(opp))
        delete_button = ctk.CTkButton(button_frame, text="🗑️", width=36, command=lambda: on_delete_callback(opp))
        edit_button.pack(side="left", padx=7)
        delete_button.pack(side="left", padx=7)
        button_frame.pack(anchor="ne", padx=14, pady=10)
        bind_all_children(frame, lambda e: on_click_callback(opp), exclude_widgets={button_frame, edit_button, delete_button})
    else:
        bind_all_children(frame, lambda e: on_click_callback(opp))
    return frame
