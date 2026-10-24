"""A compact dark desktop theme for the consumer-facing Folder -2 edition.

Purely presentational. Does not alter the file-handling engine.
"""
import tkinter as tk
from tkinter import ttk


def apply_consumer_theme(root: tk.Tk) -> None:
    bg = "#101720"
    card = "#192330"
    field = "#111c29"
    text = "#eef3fa"
    subtle = "#bcc9d8"
    blue = "#448df0"
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    root.configure(background=bg)

    style.configure(".", background=bg, foreground=text, font=("Segoe UI", 10))
    style.configure("TFrame", background=bg)
    style.configure("Card.TFrame", background=card)
    style.configure("TLabel", background=bg, foreground=text, font=("Segoe UI", 10))
    style.configure("Muted.TLabel", background=bg, foreground=subtle, font=("Segoe UI", 10))
    style.configure("Card.TLabel", background=card, foreground=text, font=("Segoe UI", 10))
    style.configure("Hero.TLabel", background=bg, foreground=text, font=("Segoe UI", 19, "bold"))
    style.configure("TLabelFrame", background=card, borderwidth=1, relief="solid")
    style.configure("TLabelFrame.Label", background=card, foreground=text,
                    font=("Segoe UI", 11, "bold"))
    style.configure("TEntry", padding=6, fieldbackground=field, foreground=text,
                    insertcolor=text, borderwidth=1)
    style.map("TEntry", fieldbackground=[("readonly", field), ("disabled", card)],
              foreground=[("readonly", text), ("disabled", subtle)])
    style.configure("TCombobox", padding=5, fieldbackground=field,
                    foreground=text, background=card, arrowcolor=text)
    style.map("TCombobox", fieldbackground=[("readonly", field), ("disabled", card)],
              foreground=[("readonly", text), ("disabled", subtle)])
    style.configure("TButton", background="#283749", foreground=text, padding=(13, 8),
                    borderwidth=0, font=("Segoe UI", 10, "bold"))
    style.map("TButton", background=[("active", "#364b62"), ("disabled", card)],
              foreground=[("disabled", "#7b91a8")])
    style.configure("Action.TButton", background=blue, foreground="#ffffff",
                    padding=(16, 10), font=("Segoe UI", 10, "bold"))
    style.map("Action.TButton", background=[("active", "#3177d5"), ("disabled", "#253d5b")],
              foreground=[("disabled", "#9cabc0")])
    style.configure("TScrollbar", background=card, troughcolor=bg)
    style.configure("Treeview", background=field, foreground=text, fieldbackground=field,
                    borderwidth=0, rowheight=29, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", background=card, foreground=text,
                    font=("Segoe UI", 10, "bold"), padding=6)
    style.map("Treeview", background=[("selected", "#264d78")],
              foreground=[("selected", "#ffffff")])
    # The status stays readable as the rest of the page scrolls.
    root.option_add("*Listbox.background", field)
    root.option_add("*Listbox.foreground", text)
    root.option_add("*Text.background", field)
    root.option_add("*Text.foreground", text)
