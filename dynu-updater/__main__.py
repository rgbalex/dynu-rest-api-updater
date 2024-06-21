import json
import time
import requests
import threading
import customtkinter as ctk
from tkinter import messagebox
from .countdownthread import CountdownThread

class DynuAPIUpdater:
    def __init__(self):
        self.client_id = None
        self.api_key = None
        self.timer_thread = None
        self.url = "https://api.dynu.com/v2/oauth2/token"
        
        with open("secret.json") as f:
            secret_data = json.load(f)
            self.client_id = secret_data["client_id"]
            self.api_key = secret_data["client_secret"]
        
        self.create_gui()
    
    def create_gui(self):
        self.window = ctk.CTk()
        self.window.title("Dynu API Updater")
        self.window.iconbitmap("favicon.ico")
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        self.window.minsize(400, 700)
        
        self.window.grid_columnconfigure((0, 1), weight=1)
        self.window.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)
        self.window.grid_rowconfigure(7, weight=30)
        
        self.client_id_label = ctk.CTkLabel(self.window, text="Client ID:")
        self.client_id_label.grid(row=0, column=0)
        self.client_id_entry = ctk.CTkEntry(self.window)
        self.client_id_entry.insert(ctk.END, self.client_id)
        self.client_id_entry.grid(row=1, column=0)
        
        self.api_key_label = ctk.CTkLabel(self.window, text="API Key:")
        self.api_key_label.grid(row=2, column=0)
        self.api_key_entry = ctk.CTkEntry(self.window)
        self.api_key_entry.insert(ctk.END, self.api_key)
        self.api_key_entry.grid(row=3, column=0)
        
        self.timer_label = ctk.CTkLabel(self.window, text="Timer (seconds):")
        self.timer_label.grid(row=1, column=1)
        
        self.timer_time_label = ctk.CTkLabel(self.window, text="0")
        self.timer_time_label.grid(row=2, column=1)
        
        self.request_button = ctk.CTkButton(self.window, text="Make Request", command=self.make_request)
        self.request_button.grid(columnspan=2, row=6, column=0, padx=10, pady=10)
        
        self.output_text = ctk.CTkTextbox(self.window)
        self.output_text.grid(columnspan=2, row=7, column=0, padx=10, pady=10, sticky="nsew")
        
        self.window.mainloop()
    
    def on_window_close(self):
        if self.timer_thread is not None:
            self.timer_thread.kill()
        self.window.destroy()
        exit(0)
    
    def fetch_data(self):
        response = requests.get(self.url, auth=(self.client_id, self.api_key))
        response_json = response.json()
        
        # Check authentication
        if response.status_code == 401:
            messagebox.showerror("Error", "Invalid client_id or api_key")
            return
        elif response.status_code == 200:
            if self.timer_thread is not None:
                self.timer_thread.kill()
            
            self.timer_thread = CountdownThread(response_json["expires_in"], self.timer_time_label)
            self.timer_thread.start()
            
            self.output_text.insert(ctk.END, str(response_json) + "\n")
            self.output_text.see(ctk.END)
        else:
            pass
        
        self.request_button.configure(state="normal")
    
    def make_request(self):
        client_id = self.client_id_entry.get()
        api_key = self.api_key_entry.get()
        
        if client_id == "" or api_key == "":
            messagebox.showerror("Error", "Please provide client_id and api_key")
            return
        
        with open("secret.json", "w") as f:
            json.dump({"client_id": client_id, "client_secret": api_key}, f)
        
        self.request_button.configure(state="disabled")
        thread = threading.Thread(target=self.fetch_data)
        thread.start()

# Create an instance of the DynuAPIUpdater class
dynu_updater = DynuAPIUpdater()
