import json
import time
import requests
import threading
import customtkinter as ctk
from tkinter import messagebox

from .countdownthread import CountdownThread

client_id = None
api_key = None
timer_thread: CountdownThread = None
url = "https://api.dynu.com/v2/oauth2/token"

with open("secret.json") as f:
    secret_data = json.load(f)
    client_id = secret_data["client_id"]
    api_key = secret_data["client_secret"]


def on_window_close():
    if timer_thread is not None:
        timer_thread.kill()
    window.destroy()
    exit(0)


def fetch_data():
    global timer_thread
    response = requests.get(url, auth=(client_id, api_key))
    response_json = response.json()

    # Check authentication
    match response.status_code:
        case 401:
            messagebox.showerror("Error", "Invalid client_id or api_key")
            return
        case 200:
            # Update the timer label with the value of the timer
            if timer_thread is not None:
                timer_thread.kill()

            timer_thread = CountdownThread(
                response_json["expires_in"], timer_time_label
            )
            timer_thread.start()

            output_text.insert(ctk.END, str(response_json) + "\n")
            output_text.see(ctk.END)
        case _:
            pass

    request_button.configure(state="normal")


def make_request():
    client_id = client_id_entry.get()
    api_key = api_key_entry.get()

    if client_id == "" or api_key == "":
        messagebox.showerror("Error", "Please provide client_id and api_key")
        return

    # Since the value of client_id and api_key are now known,
    # we can write them back to the secret.json file
    with open("secret.json", "w") as f:
        json.dump({"client_id": client_id, "client_secret": api_key}, f)

    request_button.configure(state="disabled")
    thread = threading.Thread(target=fetch_data)
    thread.start()


# Create the GUI window
window = ctk.CTk()
window.title("Dynu API Updater")
window.iconbitmap("favicon.ico")
window.protocol("WM_DELETE_WINDOW", on_window_close)

window.minsize(400, 700)

window.grid_columnconfigure((0, 1), weight=1)
window.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)
window.grid_rowconfigure(7, weight=30)

# Create labels and entry fields for client_id and api_key
client_id_label = ctk.CTkLabel(window, text="Client ID:")
client_id_label.grid(row=0, column=0)
client_id_entry = ctk.CTkEntry(window)
client_id_entry.insert(ctk.END, client_id)
client_id_entry.grid(row=1, column=0)


api_key_label = ctk.CTkLabel(window, text="API Key:")
api_key_label.grid(row=2, column=0)
api_key_entry = ctk.CTkEntry(window)
api_key_entry.insert(ctk.END, api_key)
api_key_entry.grid(row=3, column=0)

# A timer to show how long you can make API requests for
timer_label = ctk.CTkLabel(window, text="Timer (seconds):")
timer_label.grid(row=1, column=1)

timer_time_label = ctk.CTkLabel(window, text="0")
timer_time_label.grid(row=2, column=1)

# Create a button to make the request
request_button = ctk.CTkButton(window, text="Make Request", command=make_request)
request_button.grid(columnspan=2, row=6, column=0, padx=10, pady=10)

# Create a text window to display the output
output_text = ctk.CTkTextbox(window)
output_text.grid(columnspan=2, row=7, column=0, padx=10, pady=10, sticky="nsew")

# Start the GUI event loop
window.mainloop()
