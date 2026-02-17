import customtkinter as ctk
from screens.menu import MenuScreen
from screens.game import GameScreen
from screens.wallet import WalletScreen
from screens.host_screen import HostScreen
from screens.guesser_screen import GuesserScreen
from blockchain.logic import Web3Service

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Guess Game")
        self.geometry("420x420")
        self.resizable(False, False)
        self.web3_service = Web3Service()

        self.container = ctk.CTkFrame(self, corner_radius=20)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.screens = {}
        for Screen in (MenuScreen, GameScreen, WalletScreen, HostScreen, GuesserScreen):
            screen = Screen(self.container, self)
            self.screens[Screen.__name__] = screen
            screen.place(relwidth=1, relheight=1)

        self.show_screen("MenuScreen")

    def show_screen(self, name):
        if name == "WalletScreen":
            if "WalletScreen" in self.screens:
                self.screens["WalletScreen"].destroy()
            wallet_screen = WalletScreen(self.container, self)
            self.screens["WalletScreen"] = wallet_screen
            wallet_screen.place(relwidth=1, relheight=1)
        
        self.screens[name].tkraise()