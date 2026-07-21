import customtkinter as ctk

# -----------------------------
# Theme
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class JarvisUI:

    def __init__(self):

        # Window
        self.root = ctk.CTk()
        self.root.geometry("360x320")
        self.root.title("Jarvis")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        

        # -----------------------------
        # Robot
        # -----------------------------
        self.logo_label = ctk.CTkLabel(
            self.root,
            text="🤖",
            font=("Segoe UI Emoji", 64)
        )
        self.logo_label.pack(pady=(20, 10))

        # -----------------------------
        # Title
        # -----------------------------
        self.title_label = ctk.CTkLabel(
            self.root,
            text="JARVIS",
            font=("Segoe UI", 26, "bold")
        )
        self.title_label.pack()

        # -----------------------------
        # Subtitle
        # -----------------------------
        self.subtitle = ctk.CTkLabel(
            self.root,
            text="Your Personal AI Assistant",
            font=("Segoe UI", 12),
            text_color="gray"
        )
        self.subtitle.pack(pady=(0, 15))

        # -----------------------------
        # Status
        # -----------------------------
        self.status_label = ctk.CTkLabel(
            self.root,
            text="🟢 Waiting...",
            font=("Segoe UI", 20, "bold"),
            text_color="#4CAF50"
        )
        self.status_label.pack(pady=(10, 0))

        
        # Divider
        self.divider = ctk.CTkLabel(
            self.root,
            text="────────────────────",
            text_color="gray"
        )
        self.divider.pack(pady=(15, 5))

        # Command Label
        self.command_label = ctk.CTkLabel(
            self.root,
            text="Say 'Jarvis'...",
            font=("Segoe UI", 13),
            wraplength=320,
            justify="center",
            text_color="white"
        )
        self.command_label.pack(pady=(5, 0))



    
    # ==========================================================
    # STATUS FUNCTIONS
    # ==========================================================

    def waiting(self):
        self.status_label.configure(
            text="🟢 Waiting...",
            text_color="#4CAF50"
        )

    def listening(self):
        self.status_label.configure(
            text="🎤 Listening...",
            text_color="#00BCD4"
        )

    def processing(self):
        self.status_label.configure(
            text="🧠 Processing...",
            text_color="#FFC107"
        )

    def speaking(self):
        self.status_label.configure(
            text="🔊 Speaking...",
            text_color="#9C27B0"
        )

    def executing(self):
        self.status_label.configure(
            text="⚡ Executing...",
            text_color="#FF9800"
        )

    def update_command(self, text):
        self.command_label.configure(text=text)    

    # ==========================================================
    # RUN
    # ==========================================================

    def run(self):
        self.root.mainloop()


# ==========================================================
# TEST UI
# ==========================================================

if __name__ == "__main__":
    app = JarvisUI()
    app.run()