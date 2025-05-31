import customtkinter as ctk
from ui.screens import LoginScreen, RegisterScreen
from ui.main_menu import *
from ui.profile_form import ProfileForm 

def show_main_menu(user_data):
    for widget in app.winfo_children():
        widget.destroy()
    MainMenu(app, user_data)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Community Volunteer Matchmaker")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.after(100, lambda: self.state("zoomed"))

        self.current_frame = None
        self.show_login()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    def show_login(self):
        self.clear_frame()
        self.current_frame = LoginScreen(self, self.show_register, self.switch_to_main)
        self.current_frame.pack(expand=True, fill="both")

    def show_register(self):
        self.clear_frame()
        self.current_frame = RegisterScreen(self, self.show_login, self.switch_to_main)
        self.current_frame.pack(expand=True, fill="both")

    def switch_to_main(self, result, just_registered=False):
        self.clear_frame()
        self.show_main_screen(result, just_registered)
        
    def show_main_screen(self, result, just_registered):
        self.clear_frame()

        if just_registered:
            self.current_frame = ProfileForm(
                self,
                result,
                on_close_callback=lambda: self.show_main_menu(result)
            )
        else:
            self.show_main_menu(result)

    def show_main_menu(self, result):
        self.clear_frame()
        self.current_frame = MainMenu(self, result)
        self.current_frame.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = App()
    app.mainloop()
    
