import tkinter as tk
import os
import sys

def placeholder(entry, texto, ocultar=False):
    entry.insert(0, texto)
    entry.config(fg="gray")

    def on_focus_in(event):
        if entry.get() == texto:
            entry.delete(0, tk.END)
            entry.config(fg="black")
            if ocultar:
                entry.config(show="*")

    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, texto)
            entry.config(fg="gray")
            if ocultar:
                entry.config(show="")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


def mostrar_frame(frame):
    frame.tkraise()


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(relative_path):
    base_dir = app_dir()
    candidate = os.path.join(base_dir, relative_path)
    if os.path.exists(candidate):
        return candidate

    if getattr(sys, "frozen", False):
        bundle_dir = getattr(sys, "_MEIPASS", base_dir)
        return os.path.join(bundle_dir, relative_path)

    return candidate
