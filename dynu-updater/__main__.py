import requests, json
import json
import tkinter as tk
from tkinter import messagebox

client_id = None
api_key = None
url = "https://api.dynu.com/v2/oauth2/token"

with open("secret.json") as f:
    secret_data = json.load(f)
    client_id = secret_data["client_id"]
    api_key = secret_data["client_secret"]


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

    response = requests.get(url, auth=(client_id, api_key))

    output_text.insert(tk.END, str(response.json())+"\n")
    output_text.see(tk.END)


# Create the GUI window
window = tk.Tk()
window.title("Dynu API Updater")

# Create labels and entry fields for client_id and api_key
client_id_label = tk.Label(window, text="Client ID:")
client_id_label.pack()
client_id_entry = tk.Entry(window)
client_id_entry.insert(tk.END, client_id)
client_id_entry.pack()

api_key_label = tk.Label(window, text="API Key:")
api_key_label.pack()
api_key_entry = tk.Entry(window)
api_key_entry.insert(tk.END, api_key)
api_key_entry.pack()

# Create a button to make the request
request_button = tk.Button(window, text="Make Request", command=make_request)
request_button.pack()

# Create a text window to display the output
output_text = tk.Text(window)
output_text.configure(yscrollcommand=tk.Scrollbar().set)
output_text.config(yscrollcommand=output_text.yview)
scrollbar = tk.Scrollbar(window)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=output_text.yview)
output_text.pack()

# Start the GUI event loop
window.mainloop()
