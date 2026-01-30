import customtkinter as ctk
from screens.menu import MenuScreen
from screens.game import GameScreen
from screens.wallet import WalletScreen
from screens.user1 import SetNumberScreen
from screens user2 import GuessScreen
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
        for Screen in (MenuScreen, GameScreen, WalletScreen, SetNumberScreen, GuessScreen):
            screen = Screen(self.container, self)
            self.screens[Screen.__name__] = screen
            screen.place(relwidth=1, relheight=1)

        self.show_screen("MenuScreen")

    def show_screen(self, name):
        self.screens[name].tkraise()

