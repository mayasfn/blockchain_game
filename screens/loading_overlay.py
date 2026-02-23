import customtkinter as ctk

class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=("gray20", "gray10"))
        
        self.label = ctk.CTkLabel(
            self, 
            text="Waiting for Blockchain...\n(Sepolia can take 15-30 seconds)", 
            font=("Arial", 16, "bold")
        )
        self.label.place(relx=0.5, rely=0.4, anchor="center")

        self.progressbar = ctk.CTkProgressBar(self, orientation="horizontal", width=300)
        self.progressbar.place(relx=0.5, rely=0.5, anchor="center")
        self.progressbar.configure(mode="indeterminate")

    def start(self):
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.progressbar.start()

    def stop(self):
        self.progressbar.stop()
        self.place_forget()