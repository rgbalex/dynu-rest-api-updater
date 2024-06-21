import os
import json
import time
import requests
import threading
import customtkinter as ctk
from tkinter import messagebox
from .countdownthread import CountdownThread


class DynuAPIUpdater:
    def __init__(self):
        self.api_key = None
        self.dns_list = None
        self.client_id = None
        self.access_token = None
        self.timer_thread = None
        self.url = "https://api.dynu.com/v2/oauth2/token"
        self.secret_path = os.path.join(os.environ["USERPROFILE"], "dynu_secret.json")

        if not os.path.exists(self.secret_path):
            with open(self.secret_path, "w") as f:
                json.dump(
                    {
                        "client_id": "",
                        "client_secret": "",
                        "auto_update_oauth_session": True,
                    },
                    f,
                )

        try:
            with open(self.secret_path) as f:
                secret_data = json.load(f)
                self.client_id = secret_data["client_id"]
                self.api_key = secret_data["client_secret"]
                self.auto_update_oauth_session = secret_data[
                    "auto_update_oauth_session"
                ]
        except KeyError as e:
            print(f"Error: {e}")

        self.create_gui()

    def create_gui(self):
        self.window = ctk.CTk()
        self.window.title("Dynu API Updater")
        self.window.iconbitmap("favicon.ico")
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.window.minsize(700, 800)

        self.window.grid_columnconfigure((0), weight=0)
        self.window.grid_columnconfigure((1), weight=1)
        self.window.grid_rowconfigure((0), weight=0)
        self.window.grid_rowconfigure((1), weight=30)

        # region OAuthFrame
        self.OAuthFrame = ctk.CTkFrame(self.window)
        self.OAuthFrame.grid_columnconfigure((0, 1), weight=1)
        self.OAuthFrame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)
        self.OAuthFrame.grid(row=0, column=0, padx=10, pady=(10, 10))

        self.JSONFrame = ctk.CTkFrame(self.OAuthFrame)
        self.JSONFrame.grid_columnconfigure((0), weight=1)
        self.JSONFrame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.JSONFrame.configure(border_width=2)
        self.JSONFrame.grid(row=0, column=0, rowspan=4, padx=10, pady=10)

        self.client_id_label = ctk.CTkLabel(self.JSONFrame, text="Client ID:")
        self.client_id_label.grid(row=0, column=0, padx=0)
        self.client_id_entry = ctk.CTkEntry(self.JSONFrame, show="*")
        self.client_id_entry.insert(ctk.END, self.client_id)
        self.client_id_entry.grid(row=1, column=0, padx=10, pady=0)

        self.api_key_label = ctk.CTkLabel(self.JSONFrame, text="API Key:")
        self.api_key_label.grid(row=2, column=0, padx=10)
        self.api_key_entry = ctk.CTkEntry(self.JSONFrame, show="*")
        self.api_key_entry.insert(ctk.END, self.api_key)
        self.api_key_entry.grid(row=3, column=0, padx=10, pady=(0, 5))

        self.TimerFrame = ctk.CTkFrame(self.OAuthFrame)
        self.TimerFrame.grid_columnconfigure((0, 1), weight=1)
        self.TimerFrame.configure(border_width=2)
        self.TimerFrame.grid(row=0, column=1, rowspan=3, padx=10, pady=10)

        self.timer_label = ctk.CTkLabel(self.TimerFrame, text="Timer (seconds):")
        self.timer_label.grid(row=1, column=1, padx=10, pady=0)

        self.timer_time_label = ctk.CTkLabel(
            self.TimerFrame, text="0", font=("Arial", 16)
        )
        self.timer_time_label.grid(row=2, column=1, padx=10, pady=0)

        self.refresh_oauth_session_checkbox = ctk.CTkCheckBox(
            self.OAuthFrame, text="Enable Auto Refresh API Key"
        )
        self.refresh_oauth_session_checkbox.grid(row=3, column=1, padx=10, pady=(0, 0))
        # endregion

        # region APIActionFrame
        self.APIActionFrame = ctk.CTkFrame(self.window)
        self.APIActionFrame.grid(row=0, column=1, padx=10, pady=10)

        self.request_dns_button = ctk.CTkButton(
            self.APIActionFrame,
            text="Request DNS Records",
            command=self.request_dns_records,
        )
        self.request_dns_button.grid(row=0, column=0, padx=10, pady=5)

        self.dns_listbox = ctk.CTkComboBox(self.APIActionFrame)
        self.dns_listbox.configure(values=[])
        self.dns_listbox.set("Request DNS Records")
        self.dns_listbox.grid(row=1, column=0, padx=10, pady=5)

        self.request_update_ip_button = ctk.CTkButton(
            self.APIActionFrame,
            text="Request Update IP",
            command=self.request_update_ip,
        )
        self.request_update_ip_button.grid(row=2, column=0, padx=10, pady=5)

        self.enable_auto_update_ip_checkbox = ctk.CTkCheckBox(
            self.APIActionFrame, text="Enable Auto Update IP"
        )
        self.enable_auto_update_ip_checkbox.grid(row=3, column=0, padx=10, pady=5)

        self.update_ip_interval_label = ctk.CTkLabel(
            self.APIActionFrame, text="Update IP Interval (minutes):"
        )
        self.update_ip_interval_label.grid(row=4, column=0, padx=10, pady=5)

        self.update_ip_interval_entry = ctk.CTkEntry(self.APIActionFrame)
        self.update_ip_interval_entry.grid(row=5, column=0, padx=10, pady=5)
        # endregion

        self.request_button = ctk.CTkButton(
            self.OAuthFrame,
            text="Make Request",
            command=self.authenticate_oauth_session,
        )
        self.request_button.grid(columnspan=2, row=6, column=0, padx=10, pady=5)

        self.output_text = ctk.CTkTextbox(self.window)
        self.output_text.configure(state="disabled")
        self.output_text.grid(
            columnspan=2, row=1, column=0, padx=10, pady=(0, 10), sticky="news"
        )

        self.window.mainloop()

    def on_window_close(self):
        if self.timer_thread is not None:
            self.timer_thread.kill()
        self.window.destroy()
        exit(0)

    def request_dns_records(self):
        if self.access_token is None:
            messagebox.showerror("Error", "Please request OAuth session first")
            return

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        retries = 0
        while retries < 3:
            response = requests.get("https://api.dynu.com/v2/dns", headers=headers)
            response_json = response.json()
            match response.status_code:
                case 401:
                    self.output_text.configure(state="normal")
                    self.output_text.insert(ctk.END, str(response_json) + "\n")
                    self.output_text.see(ctk.END)
                    self.output_text.configure(state="disabled")
                case 200:
                    self.dns_list = response_json["domains"]
                    domains = [record["name"] for record in self.dns_list]

                    if len(domains) == 0:
                        messagebox.showinfo("Info", "No domains found")
                    else:
                        self.dns_listbox.set("Select Domain")

                    self.dns_listbox.configure(values=domains)
                    self.output_text.configure(state="normal")
                    self.output_text.insert(ctk.END, str(response_json) + "\n")
                    self.output_text.see(ctk.END)
                    self.output_text.configure(state="disabled")
                    return
                case _:
                    print(f"Uncaught response status code {response.status_code}")
                    raise Exception(
                        f"Uncaught response status code {response.status_code}"
                    )
            time.sleep(1)
            retries += 1

        if response.status_code == 401:
            messagebox.showerror(
                "Error", "Your session has expired. Please re-authenticate."
            )

    def request_update_ip(self):
        pass

    def update_oauth_session_refresh_preference(self):
        with open(self.secret_path, "r") as f:
            secret_data = json.load(f)
            secret_data["auto_update_oauth_session"] = (
                self.refresh_oauth_session_checkbox.get()
            )

        with open(self.secret_path, "w") as f:
            json.dump(secret_data, f)

        print(
            f"Updated auto update OAuth session preference to {self.refresh_oauth_session_checkbox.get()}"
        )

    def authenticate_oauth_session(self):
        if self.timer_thread is not None:
            self.timer_thread.kill()

        def fetch_data(self):
            response = requests.get(self.url, auth=(self.client_id, self.api_key))
            response_json = response.json()

            # Check authentication
            match response.status_code:
                case 401:
                    messagebox.showerror("Error", "Invalid client_id or api_key")
                    return
                case 200:
                    if self.timer_thread is not None:
                        self.timer_thread.kill()

                    self.access_token = response_json["access_token"]
                    self.timer_thread = CountdownThread(
                        response_json["expires_in"],
                        self.timer_time_label,
                        self.refresh_oauth_session_checkbox,
                        self.authenticate_oauth_session,
                    )
                    self.timer_thread.start()

                    self.output_text.configure(state="normal")
                    self.output_text.insert(
                        ctk.END, "=== Authorization Successful ===\n"
                    )
                    self.output_text.see(ctk.END)
                    self.output_text.configure(state="disabled")
                case _:
                    raise Exception(
                        "Uncaught response status code {}".format(response.status_code)
                    )

            self.request_button.configure(state="normal")

        client_id = self.client_id_entry.get()
        api_key = self.api_key_entry.get()

        if client_id == "" or api_key == "":
            messagebox.showerror("Error", "Please provide client_id and api_key")
            return

        with open(self.secret_path, "w") as f:
            json.dump(
                {"client_id": client_id.strip(), "client_secret": api_key.strip()}, f
            )

        self.request_button.configure(state="disabled")
        thread = threading.Thread(target=fetch_data, args=(self,))
        thread.start()


# Create an instance of the DynuAPIUpdater class
dynu_updater = DynuAPIUpdater()
