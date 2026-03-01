import customtkinter as ctk

class GuesserScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller

        # --- JOIN FRAME ---
        self.join_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.join_frame.pack(pady=20, padx=20, fill="both")

        ctk.CTkLabel(self.join_frame, text="User 2 - Join Room", font=("Arial", 18, "bold")).pack(pady=10)
        self.room_entry = ctk.CTkEntry(self.join_frame, placeholder_text="Room Number", width=200)
        self.room_entry.pack(pady=5)
        ctk.CTkButton(self.join_frame, text="Join Room", command=self.join_room_action).pack(pady=10)

        # --- GUESS FRAME ---
        self.guess_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.room_title = ctk.CTkLabel(self.guess_frame, text="ROOM: --", font=("Arial", 18, "bold"), text_color="green")
        self.room_title.pack(pady=10)
        self.round_label = ctk.CTkLabel(self.guess_frame, text="", font=("Arial", 12), text_color="gray")
        self.round_label.pack()
        self.guess_entry = ctk.CTkEntry(self.guess_frame, placeholder_text="Your Guess", width=200)
        self.guess_entry.pack(pady=10)
        ctk.CTkButton(self.guess_frame, text="Send Guess", command=self.send_guess).pack(pady=10)
        self.feedback_label = ctk.CTkLabel(self.guess_frame, text="Waiting for Host...", text_color="blue")
        self.feedback_label.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Status: Not Connected", text_color="gray")
        self.status_label.pack(side="bottom", pady=5)
        ctk.CTkButton(self, text="Back to Menu", command=lambda: controller.show_screen("MenuScreen")).pack(side="bottom", pady=20)

    def join_room_action(self):
        room_id = self.room_entry.get()
        if not room_id.isdigit(): return

        self.controller.loading_out.start()
        self.update()

        success, msg = self.controller.web3_service.connect_to_room(int(room_id))
        
        if success:
            receipt = self.controller.web3_service.web3.eth.wait_for_transaction_receipt(msg)
            if receipt.status == 0:
                self.status_label.configure(text="Rejected by contract (wrong fee or same address)", text_color="red")
            else:
                self.join_frame.pack_forget()
                self.guess_frame.pack(pady=20, fill="both")
                self.room_title.configure(text=f"ROOM: {room_id}")
                self.status_label.configure(text=f"Connected to Room #{room_id}", text_color="green")
                self.poll_for_feedback()
        else:
            self.status_label.configure(text=f"Error: {msg}", text_color="red")
        self.controller.loading_out.stop()

    def send_guess(self):
        guess = self.guess_entry.get()
        if not guess.isdigit(): return
            
        self.controller.loading_out.start()
        self.update()

        success, tx_hash = self.controller.web3_service.set_guess(int(guess))
        
        if success:
            self.controller.web3_service.web3.eth.wait_for_transaction_receipt(tx_hash)
            self.feedback_label.configure(text="Guess sent! Waiting for Host...", text_color="orange")
        self.controller.loading_out.stop()

    def poll_for_feedback(self):
        if self.controller.current_screen != self: return
        
        is_finished, result = self.controller.web3_service.get_game_result()
        if is_finished:
            self.check_and_show_withdraw()
            return

        max_r = self.controller.web3_service.max_rounds
        if max_r:
            fc = self.controller.web3_service.get_feedback_count()
            self.round_label.configure(text=f"Round {fc + 1} / {max_r}")

        success, data = self.controller.web3_service.get_last_feedback_event()
        if success:
            mapping = {0: "Equal!", 1: "Greater", 2: "Smaller"}
            self.feedback_label.configure(text=f"Host says: {mapping.get(data['feedback'], '???')}", text_color="green")
        
        self.after(5000, self.poll_for_feedback)

    def check_and_show_withdraw(self):
        if self.controller.web3_service.get_pending_balance():
            ctk.CTkButton(self.guess_frame, text="Claim Winnings", fg_color="gold", text_color="black", 
                           command=self.withdraw_action).pack(pady=10)
            self.feedback_label.configure(text="GAME OVER: YOU WON!", text_color="gold")
        else:
            self.feedback_label.configure(text="GAME OVER: YOU LOST", text_color="gray")

    def withdraw_action(self):
        self.controller.loading_out.start()
        self.update()
        success, tx = self.controller.web3_service.withdraw_winnings()
        if success:
            self.controller.web3_service.web3.eth.wait_for_transaction_receipt(tx)
            self.status_label.configure(text="Winnings Claimed!")
        else:
            self.status_label.configure(text=f"Withdraw failed: {tx}", text_color="red")
        self.controller.loading_out.stop()