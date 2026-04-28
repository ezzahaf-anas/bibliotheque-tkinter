import tkinter as tk
from tkinter import ttk
from database import create_tables
from livres import create_livres_tab
from membres import create_membres_tab
from emprunts import create_emprunts_tab
COLORS = {
    "bg":             "#F2F2F2",
    "surface":        "#FFFFFF",
    "primary":        "#2E86C1",
    "primary_dark":   "#2874A6",
    "danger":         "#C0392B",
    "danger_dark":    "#A93226",
    "text":           "#333333",
    "text_secondary": "#555555",
    "border":         "#DDDDDD",
    "selection":      "#D6EAF8",
    "row_alt":        "#F0F7FC",
    "sidebar":        "#1C3A57",
    "header_fg":      "#FFFFFF",
}
FONTS = {
    "title":        ("Segoe UI", 18, "bold"),
    "heading":      ("Segoe UI", 11, "bold"),
    "label":        ("Segoe UI", 10),
    "label_bold":   ("Segoe UI", 10, "bold"),
    "button":       ("Segoe UI", 10, "bold"),
    "tree":         ("Segoe UI", 10),
    "tree_heading": ("Segoe UI", 10, "bold"),
}
create_tables()
root = tk.Tk()
root.title("Gestion Bibliothèque")
root.geometry("1000x660")
root.configure(bg=COLORS["bg"])
root.resizable(True, True)
style = ttk.Style(root)
style.theme_use("clam")
style.configure("TNotebook",
    background=COLORS["bg"], borderwidth=0, tabmargins=[0, 0, 0, 0])
style.configure("TNotebook.Tab",
    background=COLORS["sidebar"], foreground="#A0BDD4",
    font=FONTS["label_bold"], padding=[22, 10], borderwidth=0)
style.map("TNotebook.Tab",
    background=[("selected", COLORS["primary"]), ("active", "#254f72")],
    foreground=[("selected", "#FFFFFF"), ("active", "#FFFFFF")])
style.configure("Custom.Treeview",
    background=COLORS["surface"], fieldbackground=COLORS["surface"],
    foreground=COLORS["text"], font=FONTS["tree"], rowheight=32, borderwidth=0)
style.configure("Custom.Treeview.Heading",
    background=COLORS["sidebar"], foreground=COLORS["header_fg"],
    font=FONTS["tree_heading"], relief="flat", padding=[10, 8])
style.map("Custom.Treeview",
    background=[("selected", COLORS["selection"])],
    foreground=[("selected", COLORS["text"])])
style.map("Custom.Treeview.Heading", relief=[("active", "flat")])
style.configure("Custom.Vertical.TScrollbar",
    background=COLORS["border"], troughcolor=COLORS["bg"],
    borderwidth=0, arrowsize=13)
style.configure("TFrame", background=COLORS["bg"])
header = tk.Frame(root, bg=COLORS["sidebar"], height=56)
header.pack(fill="x")
header.pack_propagate(False)
tk.Label(header, text="📚  Gestion de Bibliothèque",
         font=FONTS["title"], fg=COLORS["header_fg"],
         bg=COLORS["sidebar"]).pack(side="left", padx=24, pady=10)
notebook = ttk.Notebook(root)
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
notebook.add(tab1, text="  📖  Livres  ")
notebook.add(tab2, text="  👤  Membres  ")
notebook.add(tab3, text="  🔄  Emprunts  ")
notebook.pack(expand=1, fill="both")
create_livres_tab(tab1, COLORS, FONTS, style)
create_membres_tab(tab2, COLORS, FONTS, style)
create_emprunts_tab(tab3, COLORS, FONTS, style)
root.mainloop()