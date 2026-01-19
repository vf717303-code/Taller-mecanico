import tkinter as tk

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
