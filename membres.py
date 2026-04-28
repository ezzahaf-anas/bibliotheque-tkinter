import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
def connect():
    return sqlite3.connect("biblio.db")
def make_entry(parent, C, F, width=28):
    return tk.Entry(parent, width=width, font=F["label"],
                    bg=C["surface"], fg=C["text"], insertbackground=C["text"],
                    relief="flat", highlightthickness=1,
                    highlightcolor=C["primary"], highlightbackground=C["border"])
def make_btn(parent, text, cmd, C, F, variant="primary", width=13):
    colors = {
        "primary": (C["primary"],    C["primary_dark"], "#FFFFFF"),
        "danger":  (C["danger"],     C["danger_dark"],  "#FFFFFF"),
        "neutral": (C["border"],     "#CCCCCC",         C["text"]),
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
def create_membres_tab(tab, C, F, style):
    global nom_entry, prenom_entry, email_entry, numero_entry, tree
    outer = tk.Frame(tab, bg=C["bg"])
    outer.pack(fill="both", expand=True, padx=16, pady=16)
    card = tk.Frame(outer, bg=C["surface"],
                    highlightthickness=1, highlightbackground=C["border"])
    card.pack(fill="x", pady=(0, 12))
    inner = tk.Frame(card, bg=C["surface"])
    inner.pack(fill="x", padx=20, pady=16)
    section_label(inner, "Ajouter / Modifier un Membre", C, F).grid(
        row=0, column=0, columnspan=4, sticky="ew", pady=(0, 12))
    fields = ["Nom", "Prénom", "Email", "Numéro"]
    entries_refs = []
    for i, label in enumerate(fields):
        r, c = divmod(i, 2)
        tk.Label(inner, text=label, font=F["label_bold"],
                 fg=C["text"], bg=C["surface"]).grid(
            row=r + 1, column=c * 2, sticky="w", padx=(0, 8), pady=4)
        e = make_entry(inner, C, F)
        e.grid(row=r + 1, column=c * 2 + 1, sticky="ew", padx=(0, 20), pady=4)
        entries_refs.append(e)
    nom_entry, prenom_entry, email_entry, numero_entry = entries_refs
    inner.columnconfigure(1, weight=1)
    inner.columnconfigure(3, weight=1)
    btn_row = tk.Frame(card, bg=C["surface"])
    btn_row.pack(fill="x", padx=20, pady=(0, 16))
    make_btn(btn_row, "➕  Ajouter",   ajouter_membre,   C, F, "primary").pack(side="left", padx=(0, 8))
    make_btn(btn_row, "✏️  Modifier",  modifier_membre,  C, F, "neutral").pack(side="left", padx=(0, 8))
    make_btn(btn_row, "🗑  Supprimer", supprimer_membre, C, F, "danger").pack(side="left", padx=(0, 8))
    make_btn(btn_row, "✖  Vider",     vider_champs,     C, F, "neutral").pack(side="left")
    tree_frame = tk.Frame(outer, bg=C["surface"],
                          highlightthickness=1, highlightbackground=C["border"])
    tree_frame.pack(fill="both", expand=True)
    cols = ("id", "nom", "prenom", "email", "numero")
    widths = {"id": 50, "nom": 160, "prenom": 160, "email": 230, "numero": 130}
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", style="Custom.Vertical.TScrollbar")
    vsb.pack(side="right", fill="y")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                        style="Custom.Treeview", yscrollcommand=vsb.set,
                        selectmode="browse")
    vsb.config(command=tree.yview)
    for col in cols:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=widths.get(col, 120), anchor="w", minwidth=40)
    tree.tag_configure("odd",  background=C["surface"])
    tree.tag_configure("even", background=C["row_alt"])
    tree.pack(side="left", fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", select_membre)
    afficher_membres()
def ajouter_membre():
    conn = connect(); cur = conn.cursor()
    cur.execute("INSERT INTO membres (nom, prenom, email, numero) VALUES (?,?,?,?)",
                (nom_entry.get(), prenom_entry.get(), email_entry.get(), numero_entry.get()))
    conn.commit(); conn.close(); afficher_membres(); vider_champs()
def afficher_membres():
    for row in tree.get_children(): tree.delete(row)
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM membres")
    for i, row in enumerate(cur.fetchall()):
        tree.insert("", tk.END, values=row, tags=("even" if i % 2 == 0 else "odd",))
    conn.close()
def supprimer_membre():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Attention", "Sélectionnez un membre"); return
    id_m = tree.item(sel[0])["values"][0]
    conn = connect(); cur = conn.cursor()
    cur.execute("DELETE FROM membres WHERE id=?", (id_m,))
    conn.commit(); conn.close(); afficher_membres()
def select_membre(event):
    sel = tree.selection()
    if sel:
        v = tree.item(sel[0])["values"]
        for entry, val in zip(
            [nom_entry, prenom_entry, email_entry, numero_entry], v[1:]
        ):
            entry.delete(0, tk.END); entry.insert(0, val)
def modifier_membre():
    sel = tree.selection()
    if not sel: return
    id_m = tree.item(sel[0])["values"][0]
    conn = connect(); cur = conn.cursor()
    cur.execute("UPDATE membres SET nom=?,prenom=?,email=?,numero=? WHERE id=?",
                (nom_entry.get(), prenom_entry.get(), email_entry.get(),
                 numero_entry.get(), id_m))
    conn.commit(); conn.close(); afficher_membres(); vider_champs()
def vider_champs():
    for e in [nom_entry, prenom_entry, email_entry, numero_entry]:
        e.delete(0, tk.END)