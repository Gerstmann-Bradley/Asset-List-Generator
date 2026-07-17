import json
import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

CONFIG_FILE = "settings.json"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote Asset Listing Generator")
        self.root.geometry("720x420")

        tk.Label(root, text="Blender Executable").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))

        self.blender_var = tk.StringVar()
        tk.Entry(root, textvariable=self.blender_var, width=70).grid(row=1, column=0, padx=10)
        tk.Button(root, text="Browse...", command=self.pick_blender).grid(row=1, column=1, padx=5)

        tk.Label(root, text="Asset Library Folder").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 2))

        self.asset_var = tk.StringVar()
        tk.Entry(root, textvariable=self.asset_var, width=70).grid(row=3, column=0, padx=10)
        tk.Button(root, text="Browse...", command=self.pick_asset).grid(row=3, column=1, padx=5)

        self.run_btn = tk.Button(root, text="Generate Asset Listing", command=self.run)
        self.run_btn.grid(row=4, column=0, pady=12)

        self.output = scrolledtext.ScrolledText(root, height=14)
        self.output.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(5, weight=1)

        self.load_settings()

    def pick_blender(self):
        path = filedialog.askopenfilename(
            title="Select blender.exe",
            filetypes=[("Blender", "blender.exe"), ("Executable", "*.exe"), ("All files", "*.*")]
        )
        if path:
            self.blender_var.set(path)

    def pick_asset(self):
        path = filedialog.askdirectory(title="Select Asset Library")
        if path:
            self.asset_var.set(path)

    def load_settings(self):
        if not os.path.exists(CONFIG_FILE):
            return

        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            self.blender_var.set(data.get("blender", ""))
            self.asset_var.set(data.get("asset", ""))
        except Exception:
            pass

    def save_settings(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "blender": self.blender_var.get(),
                "asset": self.asset_var.get()
            }, f, indent=4)

    def log(self, text):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)

    def run(self):
        blender = self.blender_var.get().strip()
        asset = self.asset_var.get().strip()

        if not os.path.isfile(blender):
            messagebox.showerror("Error", "Invalid Blender executable.")
            return

        if not os.path.isdir(asset):
            messagebox.showerror("Error", "Invalid Asset Library.")
            return

        self.save_settings()

        self.output.delete("1.0", tk.END)
        self.run_btn.config(state="disabled")

        threading.Thread(target=self.worker, args=(blender, asset), daemon=True).start()

    def worker(self, blender, asset):
        cmd = [
            blender,
            "-b",
            "-c",
            "asset_listing",
            "generate",
            "."
        ]

        process = subprocess.Popen(
            cmd,
            cwd=asset,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            self.root.after(0, self.log, line)

        process.wait()

        if process.returncode == 0:
            self.root.after(0, lambda: self.log("\nFinished successfully.\n"))
        else:
            self.root.after(0, lambda: self.log(f"\nFailed (Exit Code {process.returncode}).\n"))

        self.root.after(0, lambda: self.run_btn.config(state="normal"))


root = tk.Tk()
App(root)
root.mainloop()