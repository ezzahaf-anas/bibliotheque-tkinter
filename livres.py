import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
def connect():
    return sqlite3.connect("biblio.db")
def make_entry(parent, C, F, width=28):
    e = tk.Entry(parent, width=width, font=F["label"],
                 bg=C["surface"], fg=C["text"], insertbackground=C["text"],
                 relief="flat", highlightthickness=1,
                 highlightcolor=C["primary"], highlightbackground=C["border"])
    return e
def make_btn(parent, text, cmd, C, F, variant="primary", width=13):
    colors = {
        "primary": (C["primary"],      C["primary_dark"], "#FFFFFF"),
        "danger":  (C["danger"],       C["danger_dark"],  "#FFFFFF"),
        "neutral": (C["border"],       "#CCCCCC",         C["text"]),
    }
    bg, hbg, fg = colors.get(variant, colors["primary"])
    btn = tk.Button(parent, text=text, command=cmd, font=F["button"],
                    bg=bg, fg=fg, activebackground=hbg, activeforeground=fg,
                    relief="flat", cursor="hand2", width=width, bd=0,
                    padx=10, pady=6)
    btn.bind("<Enter>", lambda e: btn.config(bg=hbg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn
def section_label(parent, text, C, F):
    f = tk.Frame(parent, bg=C["surface"])
    tk.Label(f, text=text, font=F["heading"], fg=C["primary"],
             bg=C["surface"]).pack(side="left")
    tk.Frame(f, height=2, bg=C["primary"]).pack(
        side="left", fill="x", expand=True, padx=(8, 0))
    return f
def refresh_tags(tree):
    for i, item in enumerate(tree.get_children()):
        tree.item(item, tags=("even" if i % 2 == 0 else "odd",))
def create_livres_tab(tab, C, F, style):
    global titre_entry, auteur_entry, genre_entry, annee_entry, stock_entry, tree
    tab.configure(style="TFrame")
    outer = tk.Frame(tab, bg=C["bg"])
    outer.pack(fill="both", expand=True, padx=16, pady=16)
    card = tk.Frame(outer, bg=C["surface"], bd=0,
                    highlightthickness=1, highlightbackground=C["border"])
    card.pack(fill="x", pady=(0, 12))
    inner = tk.Frame(card, bg=C["surface"])
    inner.pack(fill="x", padx=20, pady=16)
    section_label(inner, "Ajouter / Modifier un Livre", C, F).grid(
        row=0, column=0, columnspan=4, sticky="ew", pady=(0, 12))
    fields = [("Titre", 1), ("Auteur", 2), ("Genre", 3), ("Année", 4), ("Stock", 5)]
    entries = {}
    for i, (label, row) in enumerate(fields):
        col_offset = (i % 2) * 2
        r = row // 2 + 1
        if i % 2 == 0:
            r = i // 2 + 1
        tk.Label(inner, text=label, font=F["label_bold"],
                 fg=C["text"], bg=C["surface"]).grid(
            row=i // 2 + 1, column=(i % 2) * 2, sticky="w", padx=(0, 8), pady=4)
        e = make_entry(inner, C, F)
        e.grid(row=i // 2 + 1, column=(i % 2) * 2 + 1, sticky="ew", padx=(0, 20), pady=4)
        entries[label] = e
    titre_entry  = entries["Titre"]
    auteur_entry = entries["Auteur"]
    genre_entry  = entries["Genre"]
    annee_entry  = entries["Année"]
    stock_entry  = entries["Stock"]
    inner.columnconfigure(1, weight=1)
    inner.columnconfigure(3, weight=1)
    btn_row = tk.Frame(card, bg=C["surface"])
    btn_row.pack(fill="x", padx=20, pady=(0, 16))
    make_btn(btn_row, "➕  Ajouter",   ajouter_livre,   C, F, "primary").pack(side="left", padx=(0, 8))
    make_btn(btn_row, "✏️  Modifier",  modifier_livre,  C, F, "neutral").pack(side="left", padx=(0, 8))
    make_btn(btn_row, "🗑  Supprimer", supprimer_livre, C, F, "danger").pack(side="left", padx=(0, 8))
    make_btn(btn_row, "✖  Vider",     vider_champs,    C, F, "neutral").pack(side="left")
    tree_frame = tk.Frame(outer, bg=C["surface"],
                          highlightthickness=1, highlightbackground=C["border"])
    tree_frame.pack(fill="both", expand=True)
    cols = ("id", "titre", "auteur", "genre", "annee", "stock")
    widths = {"id": 50, "titre": 220, "auteur": 160, "genre": 110, "annee": 70, "stock": 60}
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", style="Custom.Vertical.TScrollbar")
    vsb.pack(side="right", fill="y")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                        style="Custom.Treeview", yscrollcommand=vsb.set,
                        selectmode="browse")
    vsb.config(command=tree.yview)
    for col in cols:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=widths.get(col, 100), anchor="w", minwidth=40)
    tree.tag_configure("odd",  background=C["surface"])
    tree.tag_configure("even", background=C["row_alt"])
    tree.pack(side="left", fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", select_livre)

    afficher_livres()
def ajouter_livre():
    conn = connect(); cur = conn.cursor()
    cur.execute("INSERT INTO livres (titre, auteur, genre, annee, stock) VALUES (?,?,?,?,?)",
                (titre_entry.get(), auteur_entry.get(), genre_entry.get(),
                 annee_entry.get(), stock_entry.get()))
    conn.commit(); conn.close()
    afficher_livres(); vider_champs()
def afficher_livres():
    for row in tree.get_children(): tree.delete(row)
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM livres")
    for i, row in enumerate(cur.fetchall()):
        tree.insert("", tk.END, values=row, tags=("even" if i % 2 == 0 else "odd",))
    conn.close()
def supprimer_livre():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Attention", "Sélectionnez un livre"); return
    id_l = tree.item(sel[0])["values"][0]
    conn = connect(); cur = conn.cursor()
    cur.execute("DELETE FROM livres WHERE id=?", (id_l,))
    conn.commit(); conn.close(); afficher_livres()
def select_livre(event):
    sel = tree.selection()
    if sel:
        v = tree.item(sel[0])["values"]
        for entry, val in zip(
            [titre_entry, auteur_entry, genre_entry, annee_entry, stock_entry],
            v[1:]
        ):
            entry.delete(0, tk.END); entry.insert(0, val)

def modifier_livre():
    sel = tree.selection()
    if not sel: return
    id_l = tree.item(sel[0])["values"][0]
    conn = connect(); cur = conn.cursor()
    cur.execute("UPDATE livres SET titre=?,auteur=?,genre=?,annee=?,stock=? WHERE id=?",
                (titre_entry.get(), auteur_entry.get(), genre_entry.get(),
                 annee_entry.get(), stock_entry.get(), id_l))
    conn.commit(); conn.close(); afficher_livres(); vider_champs()
def vider_champs():
    for e in [titre_entry, auteur_entry, genre_entry, annee_entry, stock_entry]:
        e.delete(0, tk.END)