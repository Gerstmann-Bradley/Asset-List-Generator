import json
import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext

from asset_version_postprocess import process_library


def app_dir() -> Path:
    """Directory to store settings.json in -- next to the .exe when frozen,
    next to this .py file otherwise. Avoids writing into a temp extraction
    folder when bundled with PyInstaller's --onefile mode."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


CONFIG_FILE = app_dir() / "settings.json"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote Asset Listing Generator")
        self.root.geometry("720x480")

        tk.Label(root, text="Blender Executable").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))

        self.blender_var = tk.StringVar()
        tk.Entry(root, textvariable=self.blender_var, width=70).grid(row=1, column=0, padx=10)
        tk.Button(root, text="Browse...", command=self.pick_blender).grid(row=1, column=1, padx=5)

        tk.Label(root, text="Asset Library Folder").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 2))

        self.asset_var = tk.StringVar()
        tk.Entry(root, textvariable=self.asset_var, width=70).grid(row=3, column=0, padx=10)
        tk.Button(root, text="Browse...", command=self.pick_asset).grid(row=3, column=1, padx=5)

        self.fix_versions_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            root, text="Auto-fix bl_versions (min/until) from version folders after generating",
            variable=self.fix_versions_var,
        ).grid(row=4, column=0, sticky="w", padx=10, pady=(8, 0))

        self.dry_run_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            root, text="Preview only (dry run) -- don't write changes",
            variable=self.dry_run_var,
        ).grid(row=5, column=0, sticky="w", padx=10)

        self.run_btn = tk.Button(root, text="Generate Asset Listing", command=self.run)
        self.run_btn.grid(row=6, column=0, pady=12)

        self.output = scrolledtext.ScrolledText(root, height=14)
        self.output.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(7, weight=1)

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
        if not CONFIG_FILE.exists():
            return
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            self.blender_var.set(data.get("blender", ""))
            self.asset_var.set(data.get("asset", ""))
            self.fix_versions_var.set(data.get("fix_versions", True))
            self.dry_run_var.set(data.get("dry_run", False))
        except Exception:
            pass

    def save_settings(self):
        CONFIG_FILE.write_text(json.dumps({
            "blender": self.blender_var.get(),
            "asset": self.asset_var.get(),
            "fix_versions": self.fix_versions_var.get(),
            "dry_run": self.dry_run_var.get(),
        }, indent=4), encoding="utf-8")

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
        cmd = [blender, "-b", "-c", "asset_listing", "generate", "."]

        process = subprocess.Popen(
            cmd,
            cwd=asset,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        for line in process.stdout:
            self.root.after(0, self.log, line)

        process.wait()

        if process.returncode != 0:
            self.root.after(0, lambda: self.log(f"\nFailed (Exit Code {process.returncode}).\n"))
            self.root.after(0, lambda: self.run_btn.config(state="normal"))
            return

        self.root.after(0, lambda: self.log("\nGenerator finished successfully.\n"))

        if self.fix_versions_var.get():
            self.root.after(0, lambda: self.log("\n--- Post-processing bl_versions from folder structure ---\n"))

            def pp_log(msg: str) -> None:
                self.root.after(0, self.log, msg + "\n")

            try:
                process_library(Path(asset), dry_run=self.dry_run_var.get(), log=pp_log)
            except FileNotFoundError as ex:
                pp_log(f"error: {ex}")
            except Exception as ex:  # noqa: BLE001 -- surface any unexpected failure to the log, don't crash the GUI
                pp_log(f"error: version post-processing failed: {ex}")

        self.root.after(0, lambda: self.log("\nAll done.\n"))
        self.root.after(0, lambda: self.run_btn.config(state="normal"))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
