from __future__ import annotations
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from .scanner import scan_fortran_files
from .converter import convert_project
from .utils import diff_text, read_text, write_text, set_determinism_env


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("fort2py Converter")
        self.geometry("900x600")
        self._build()

    def _build(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.path_var = tk.StringVar()
        ttk.Label(frm, text="Local Folder Path or Cloned Repo Path:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.path_var, width=70).grid(row=1, column=0, sticky="we", padx=(0, 8))
        ttk.Button(frm, text="Browse", command=self._browse).grid(row=1, column=1, sticky="we")

        self.include_legacy = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Include legacy (.f, .for)", variable=self.include_legacy).grid(row=2, column=0, sticky="w")

        self.progress = ttk.Progressbar(frm, mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=2, sticky="we", pady=6)

        self.log = tk.Text(frm, height=20)
        self.log.grid(row=4, column=0, columnspan=2, sticky="nsew")
        frm.rowconfigure(4, weight=1)
        frm.columnconfigure(0, weight=1)

        btnfrm = ttk.Frame(frm)
        btnfrm.grid(row=5, column=0, columnspan=2, sticky="we", pady=6)
        ttk.Button(btnfrm, text="Scan", command=self._scan).pack(side=tk.LEFT)
        ttk.Button(btnfrm, text="Convert", command=self._convert).pack(side=tk.LEFT)
        ttk.Button(btnfrm, text="Show Diff (first module)", command=self._diff).pack(side=tk.LEFT)

        self.out_dir = None
        self.files = []

    def _browse(self):
        p = filedialog.askdirectory()
        if p:
            self.path_var.set(p)

    def _append_log(self, s: str):
        self.log.insert(tk.END, s + "\n")
        self.log.see(tk.END)

    def _scan(self):
        try:
            root = Path(self.path_var.get())
            self.files = scan_fortran_files(root, include_legacy=self.include_legacy.get())
            self._append_log(f"Found {len(self.files)} files")
            for f in self.files:
                self._append_log(str(f))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _convert(self):
        if not self.files:
            messagebox.showwarning("Warning", "No files scanned yet.")
            return
        out = filedialog.askdirectory(title="Select Output Directory")
        if not out:
            return
        self.out_dir = Path(out)
        self.progress["maximum"] = len(self.files)
        self.progress["value"] = 0

        def worker():
            try:
                set_determinism_env()
                convert_project(self.files, self.out_dir)
                self._append_log("Conversion completed")
            except Exception as e:
                self._append_log(f"Error: {e}")
                messagebox.showerror("Conversion Error", str(e))
            finally:
                self.progress["value"] = self.progress["maximum"]

        threading.Thread(target=worker, daemon=True).start()

    def _diff(self):
        if not self.files or not self.out_dir:
            messagebox.showwarning("Warning", "Scan and convert first.")
            return
        # Try to find first module output by heuristic: first generated .py
        outs = list(self.out_dir.glob("*.py"))
        if not outs:
            messagebox.showwarning("Warning", "No generated Python modules found.")
            return
        src = read_text(self.files[0])
        py = read_text(outs[0])
        d = diff_text(src, py, fromfile=str(self.files[0].name), tofile=str(outs[0].name))
        win = tk.Toplevel(self)
        win.title("Unified Diff")
        txt = tk.Text(win, width=120, height=40)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, d or "(No diff text available)")
        txt.configure(state="disabled")


def launch_gui():
    app = App()
    app.mainloop()
