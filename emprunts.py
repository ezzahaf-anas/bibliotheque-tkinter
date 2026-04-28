import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
def connect():
    return sqlite3.connect("biblio.db")
def get_livres():
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT id, titre FROM livres")
    data = cur.fetchall(); conn.close(); return data
def get_membres():
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT id, nom FROM membres")
    data = cur.fetchall(); conn.close(); return data
def make_btn(parent, text, cmd, C, F, variant="primary", width=15):
    colors = {
        "primary": (C["primary"],    C["primary_dark"], "#FFFFFF"),
        "danger":  (C["danger"],     C["danger_dark"],  "#FFFFFF"),
        "neutral": (C["border"],     "#CCCCCC",         C["text"]),
        "success": ("#1E8449",       "#196F3D",         "#FFFFFF"),
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
def create_emprunts_tab(tab, C, F, style):
    global livre_combo, membre_combo, tree
    outer = tk.Frame(tab, bg=C["bg"])
    outer.pack(fill="both", expand=True, padx=16, pady=16)
    card = tk.Frame(outer, bg=C["surface"],
                    highlightthickness=1, highlightbackground=C["border"])
    card.pack(fill="x", pady=(0, 12))
    inner = tk.Frame(card, bg=C["surface"])
    inner.pack(fill="x", padx=20, pady=16)
    section_label(inner, "Nouvel Emprunt", C, F).grid(
        row=0, column=0, columnspan=4, sticky="ew", pady=(0, 12))
    combo_style = "Custom.TCombobox"
    style.configure(combo_style,
        fieldbackground=C["surface"], background=C["surface"],
        foreground=C["text"], font=F["label"], padding=6)
    tk.Label(inner, text="Livre", font=F["label_bold"],
             fg=C["text"], bg=C["surface"]).grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
    livre_combo = ttk.Combobox(inner, style=combo_style, width=35, state="readonly")
    livre_combo.grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=4)
    tk.Label(inner, text="Membre", font=F["label_bold"],
             fg=C["text"], bg=C["surface"]).grid(row=1, column=2, sticky="w", padx=(0, 8), pady=4)
    membre_combo = ttk.Combobox(inner, style=combo_style, width=35, state="readonly")
    membre_combo.grid(row=1, column=3, sticky="ew", pady=4)
    livres = get_livres()
    membres = get_membres()
    livre_combo["values"]  = [f"{l[0]} - {l[1]}" for l in livres]
    membre_combo["values"] = [f"{m[0]} - {m[1]}" for m in membres]
    inner.columnconfigure(1, weight=1)
    inner.columnconfigure(3, weight=1)
    btn_row = tk.Frame(card, bg=C["surface"])
    btn_row.pack(fill="x", padx=20, pady=(0, 16))
    make_btn(btn_row, "📤  Emprunter", ajouter_emprunt, C, F, "primary").pack(side="left", padx=(0, 10))
    make_btn(btn_row, "📥  Retour",    retour_livre,    C, F, "success").pack(side="left")
    tree_frame = tk.Frame(outer, bg=C["surface"],
                          highlightthickness=1, highlightbackground=C["border"])
    tree_frame.pack(fill="both", expand=True)
    cols = ("id", "livre", "membre", "date_emprunt", "date_retour")
    widths = {"id": 50, "livre": 230, "membre": 170, "date_emprunt": 120, "date_retour": 120}
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", style="Custom.Vertical.TScrollbar")
    vsb.pack(side="right", fill="y")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                        style="Custom.Treeview", yscrollcommand=vsb.set,
                        selectmode="browse")
    vsb.config(command=tree.yview)
    labels = {"id": "ID", "livre": "Livre", "membre": "Membre",
              "date_emprunt": "Date Emprunt", "date_retour": "Date Retour"}
    for col in cols:
        tree.heading(col, text=labels[col])
        tree.column(col, width=widths.get(col, 120), anchor="w", minwidth=40)
    tree.tag_configure("odd",      background=C["surface"])
    tree.tag_configure("even",     background=C["row_alt"])
    tree.tag_configure("en_cours", foreground="#1A5276")   # blue = active loan
    tree.tag_configure("rendu",    foreground="#196F3D")   # green = returned
    tree.pack(side="left", fill="both", expand=True)
    afficher_emprunts()
def ajouter_emprunt():
    sel_l = livre_combo.get()
    sel_m = membre_combo.get()
    if not sel_l or not sel_m:
        messagebox.showwarning("Attention", "Sélectionnez un livre et un membre"); return
    livre_id  = sel_l.split(" - ")[0]
    membre_id = sel_m.split(" - ")[0]
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT stock FROM livres WHERE id=?", (livre_id,))
    row = cur.fetchone()
    if not row or row[0] <= 0:
        messagebox.showerror("Erreur", "Livre non disponible"); conn.close(); return
    cur.execute("SELECT * FROM emprunts WHERE livre_id=? AND membre_id=? AND date_retour IS NULL",
                (livre_id, membre_id))
    if cur.fetchone():
        messagebox.showerror("Erreur", "Ce membre a déjà emprunté ce livre"); conn.close(); return
    date_emprunt = datetime.now().strftime("%Y-%m-%d")
    cur.execute("INSERT INTO emprunts (livre_id, membre_id, date_emprunt, date_retour) VALUES (?,?,?,NULL)",
                (livre_id, membre_id, date_emprunt))
    cur.execute("UPDATE livres SET stock = stock - 1 WHERE id=?", (livre_id,))
    conn.commit(); conn.close(); afficher_emprunts()

def afficher_emprunts():
    for row in tree.get_children(): tree.delete(row)
    conn = connect(); cur = conn.cursor()
    cur.execute("""
        SELECT emprunts.id, livres.titre, membres.nom,
               emprunts.date_emprunt, emprunts.date_retour
        FROM emprunts
        JOIN livres  ON emprunts.livre_id  = livres.id
        JOIN membres ON emprunts.membre_id = membres.id
        ORDER BY emprunts.id DESC
    """)
    for i, row in enumerate(cur.fetchall()):
        base_tag = "even" if i % 2 == 0 else "odd"
        status   = "rendu" if row[4] else "en_cours"
        tree.insert("", tk.END, values=row, tags=(base_tag, status))
    conn.close()
def retour_livre():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Attention", "Sélectionnez un emprunt"); return
    values = tree.item(sel[0])["values"]
    if values[4]:
        messagebox.showinfo("Info", "Ce livre a déjà été retourné"); return
    emprunt_id = values[0]
    conn = connect(); cur = conn.cursor()
    cur.execute("UPDATE emprunts SET date_retour=? WHERE id=?",
                (datetime.now().strftime("%Y-%m-%d"), emprunt_id))
    cur.execute("UPDATE livres SET stock = stock + 1 WHERE id=(SELECT livre_id FROM emprunts WHERE id=?)",
                (emprunt_id,))
    conn.commit(); conn.close(); afficher_emprunts()