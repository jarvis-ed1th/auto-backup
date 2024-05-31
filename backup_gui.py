import configparser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from backup_logic import backup, check_auto_backup, keep_recent_backups
import os
import sys
import pystray
from PIL import Image
import threading


class BackupApp:
    def __init__(self, master):

        self.tray_icon = None
        self.master = master
        master.title("Backup Application")
        master.iconbitmap("icon_s.ico")

        self.background = False

        # Si l'argument "--background" est passé, lancer l'application en arrière-plan
        if "--background" in sys.argv:
            self.background = True
            self.master.withdraw()
            self.create_tray_icon()

        # Variables pour stocker les paramètres
        self.config_folder = os.path.join(os.environ['APPDATA'], 'Auto-Backup')
        self.config_file = os.path.join(self.config_folder, 'backup_app.ini')

        # Créer le dossier de configuration s'il n'existe pas
        if not os.path.exists(self.config_folder):
            os.makedirs(self.config_folder)

        self.config = configparser.ConfigParser()
        self.destination_folder = tk.StringVar()
        self.source_folders = []
        self.exclusion_folders = []
        self.history = tk.IntVar(value=3)
        self.frequency = tk.StringVar(value="daily")
        self.auto_backup_enabled = tk.BooleanVar(value=False)

        # Création des widgets
        self.destination_label = tk.Label(master, text="Destination Folder:")
        self.destination_entry = tk.Entry(master, textvariable=self.destination_folder, width=50)
        self.destination_button = tk.Button(master, text="Browse", command=self.browse_destination)

        self.source_label = tk.Label(master, text="Source Folders:")
        self.source_listbox = tk.Listbox(master, selectmode=tk.MULTIPLE, width=50)
        self.add_source_button = tk.Button(master, text="Add Source", command=self.add_source)
        self.remove_source_button = tk.Button(master, text="Remove Source", command=self.remove_source)

        self.exclusion_label = tk.Label(master, text="Excluded Folders:")
        self.exclusion_listbox = tk.Listbox(master, selectmode=tk.MULTIPLE, width=50)
        self.add_exclusion_button = tk.Button(master, text="Add Exclusion", command=self.add_exclusion)
        self.remove_exclusion_button = tk.Button(master, text="Remove Exclusion", command=self.remove_exclusion)

        self.history_label = tk.Label(master, text="Number of History:")
        self.history_spinbox = tk.Spinbox(master, from_=1, to=99, textvariable=self.history, width=5)

        self.frequency_label = tk.Label(master, text="Backup Frequency:")
        self.daily_radio = tk.Radiobutton(master, text="Daily", variable=self.frequency, value="daily")
        self.weekly_radio = tk.Radiobutton(master, text="Weekly", variable=self.frequency, value="weekly")
        self.monthly_radio = tk.Radiobutton(master, text="Monthly", variable=self.frequency, value="monthly")

        self.auto_backup_checkbox = tk.Checkbutton(master, text="Enable Auto Backup", variable=self.auto_backup_enabled)

        self.save_settings_button = tk.Button(master, text="Save Settings", command=self.save_settings, width=15)
        self.force_backup_button = tk.Button(master, text="Force Backup", command=lambda: self.init_backup('Backup'),
                                             width=15)

        # Placement des widgets
        self.destination_label.grid(row=0, column=0, sticky="e")
        self.destination_entry.grid(row=0, column=1, padx=5, sticky="we")
        self.destination_button.grid(row=0, column=2, padx=5, sticky="we")

        self.source_label.grid(row=1, column=0, sticky="e")
        self.source_listbox.grid(row=1, column=1, columnspan=2, padx=5, sticky="we")
        self.add_source_button.grid(row=2, column=1, padx=5, pady=5, sticky="we")
        self.remove_source_button.grid(row=2, column=2, padx=5, pady=5, sticky="we")

        self.exclusion_label.grid(row=3, column=0, sticky="e")
        self.exclusion_listbox.grid(row=3, column=1, columnspan=2, padx=5, sticky="we")
        self.add_exclusion_button.grid(row=4, column=1, padx=5, pady=5, sticky="we")
        self.remove_exclusion_button.grid(row=4, column=2, padx=5, pady=5, sticky="we")

        self.history_label.grid(row=5, column=0, sticky="e")
        self.history_spinbox.grid(row=5, column=1, padx=5, sticky="w")

        self.frequency_label.grid(row=6, column=0, sticky="e")
        self.daily_radio.grid(row=6, column=1, padx=5, sticky="w")
        self.weekly_radio.grid(row=6, column=1, padx=80, sticky="w")
        self.monthly_radio.grid(row=6, column=1, padx=150, sticky="w")

        self.auto_backup_checkbox.grid(row=7, column=0, columnspan=3, pady=10)

        self.save_settings_button.grid(row=8, column=1, padx=5, pady=10, sticky="e")
        self.force_backup_button.grid(row=8, column=2, padx=5, pady=10, sticky="we")

        # Charger les paramètres sauvegardés
        self.load_settings()
        self.auto_backup()

    def create_tray_icon(self):
        icon_image = Image.open("icon_s.ico")
        self.tray_icon = pystray.Icon("name", icon_image, "Auto-Backup", self.create_menu())
        self.tray_icon.run_detached()

    def create_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Open", self.show_app),
            pystray.MenuItem("Exit", self.exit_app)
        )

    def show_app(self):
        self.background = False
        self.master.deiconify()
        self.tray_icon.stop()

    def exit_app(self):
        self.tray_icon.stop()
        self.master.quit()
        os._exit(0)

    def browse_destination(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.destination_folder.set(folder_selected)

    def add_source(self):
        folders_selected = filedialog.askdirectory()
        if folders_selected:
            self.source_listbox.insert(tk.END, folders_selected)
            self.source_folders.append(folders_selected)

    def remove_source(self):
        selected_indices = self.source_listbox.curselection()
        for index in reversed(selected_indices):
            del self.source_folders[index]
            self.source_listbox.delete(index)

    def add_exclusion(self):
        folders_selected = filedialog.askdirectory()
        if folders_selected:
            self.exclusion_listbox.insert(tk.END, folders_selected)
            self.exclusion_folders.append(folders_selected)

    def remove_exclusion(self):
        selected_indices = self.exclusion_listbox.curselection()
        for index in reversed(selected_indices):
            del self.exclusion_folders[index]
            self.exclusion_listbox.delete(index)

    def save_settings(self):
        self.config['Settings'] = {
            "destination_folder": self.destination_folder.get(),
            "source_folders": ','.join(self.source_folders),
            "exclusion_folders": ','.join(self.exclusion_folders),
            "history": str(self.history.get()),
            "frequency": self.frequency.get(),
            "auto_backup_enabled": str(self.auto_backup_enabled.get())
        }
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
        messagebox.showinfo("Settings Saved", "Settings saved successfully.")
        self.auto_backup()

    def load_settings(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            if 'Settings' in self.config:
                settings = self.config['Settings']
                self.destination_folder.set(settings.get("destination_folder", ""))
                self.source_folders = settings.get("source_folders", "").split(',')
                self.exclusion_folders = settings.get("exclusion_folders", "").split(',')
                for folder in self.source_folders:
                    self.source_listbox.insert(tk.END, folder)
                for folder in self.exclusion_folders:
                    self.exclusion_listbox.insert(tk.END, folder)
                self.history.set(int(settings.get("history", "3")))
                self.frequency.set(settings.get("frequency", "daily"))
                self.auto_backup_enabled.set(settings.get("auto_backup_enabled", "False") == "True")

    def auto_backup(self):
        if self.auto_backup_enabled.get():
            if check_auto_backup(self.frequency.get(), self.destination_folder.get()):
                self.init_backup("auto-backup")

    def init_backup(self, backup_name):
        progress_window = ProgressWindow(self.master, self.background)
        backup_thread = threading.Thread(
            target=backup, args=(
                self.destination_folder.get(), self.source_folders, self.exclusion_folders, backup_name,
                self.history.get(), progress_window, callback))
        backup_thread.start()


def callback(progress_window, backup_name, destination_folder, history):
    progress_window.window.destroy()
    if not progress_window.background:
        messagebox.showinfo("Backup Complete", f"{backup_name} completed successfully.")
    keep_recent_backups(destination_folder, history)


class ProgressWindow:
    def __init__(self, parent, background):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Sauvegarde en cours")
        self.window.geometry("300x100")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self.disable_close_button)

        self.background = background

        self.progress_label = ttk.Label(self.window, text="Sauvegarde en cours...")
        self.progress_label.pack(pady=10)

        self.cancel_button = ttk.Button(self.window, text="Force stop (not recommended)", command=self.cancel_backup)
        self.cancel_button.pack(pady=5)

        self.progressbar = ttk.Progressbar(self.window, orient="horizontal", length=200, mode="indeterminate")
        self.progressbar.pack(pady=5)
        self.progressbar.start()

    def disable_close_button(self):
        pass

    def cancel_backup(self):
        self.window.destroy()
        os._exit(0)


# Créer et exécuter l'application
root = tk.Tk()
app = BackupApp(root)
root.mainloop()
