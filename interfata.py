"""Interfata grafica (Tkinter): autentificare, adaugarea meselor, rezumatul zilei.

Foloseste aceleasi functii ca aplicatia din terminal (logica.py si stocare.py),
deci calculele si validarile sunt identice.
"""
import calendar
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

from logica import (
    NUTRIENTI,
    acum_text,
    cauta_alimente,
    citeste_grame,
    citeste_zi,
    total_pe_zi,
)
from stocare import BazaDeDate

ETICHETE = {
    "kcal": "kcal",
    "proteine": "Proteine",
    "grasimi": "Grăsimi",
    "carbohidrati": "Carbohidrați",
    "fibre": "Fibre",
}

LUNI = ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie", "iulie",
        "august", "septembrie", "octombrie", "noiembrie", "decembrie"]
ZILE_SAPTAMANA = ["Lu", "Ma", "Mi", "Jo", "Vi", "Sâ", "Du"]

# Paleta de culori: se schimba aici si se aplica in toata aplicatia.
CULORI = {
    "fundal": "#E9E4E0",        # bej deschis
    "suprafata": "#F6F3F1",     # liste, tabel, campuri
    "text": "#172A39",          # albastru inchis
    "text_secundar": "#6E7575", # gri
    "principal": "#172A39",     # butoane principale
    "principal_activ": "#24425A",
    "accent": "#FC563C",        # portocaliu: selectie, zi aleasa, "Adauga masa"
    "accent_activ": "#E0452D",
    "accent_deschis": "#FDDCD5",
    "rand_alternat": "#EFEAE6",
    "margine": "#C9C2BC",
    "eroare": "#C2331F",
}
FONT = "Segoe UI"


def aplica_stilul(fereastra):
    """Configureaza stilurile ttk dupa paleta CULORI."""
    c = CULORI
    stil = ttk.Style(fereastra)
    if "clam" in stil.theme_names():
        stil.theme_use("clam")
    fereastra.configure(bg=c["fundal"])
    stil.configure(".", background=c["fundal"], foreground=c["text"], font=(FONT, 10),
                   bordercolor=c["margine"], lightcolor=c["fundal"], darkcolor=c["fundal"])
    stil.configure("TFrame", background=c["fundal"])
    stil.configure("TLabel", background=c["fundal"], foreground=c["text"])
    stil.configure("Titlu.TLabel", font=(FONT, 18, "bold"))
    stil.configure("Total.TLabel", font=(FONT, 10, "bold"))
    stil.configure("Secundar.TLabel", foreground=c["text_secundar"])
    stil.configure("Eroare.TLabel", foreground=c["eroare"])
    stil.configure("TLabelframe", background=c["fundal"], bordercolor=c["margine"])
    stil.configure("TLabelframe.Label", background=c["fundal"], foreground=c["text"],
                   font=(FONT, 10, "bold"))
    # butoane: implicit deschise cu text inchis; Principal = albastru; Accent = portocaliu
    stil.configure("TButton", background=c["suprafata"], foreground=c["text"],
                   bordercolor=c["margine"], focuscolor=c["accent"], padding=(10, 4))
    stil.map("TButton", background=[("active", c["accent_deschis"])])
    stil.configure("Principal.TButton", background=c["principal"], foreground="white",
                   bordercolor=c["principal"])
    stil.map("Principal.TButton", background=[("active", c["principal_activ"])])
    stil.configure("Accent.TButton", background=c["accent"], foreground="white",
                   bordercolor=c["accent"], font=(FONT, 10, "bold"))
    stil.map("Accent.TButton", background=[("active", c["accent_activ"])])
    stil.configure("TCheckbutton", background=c["fundal"], foreground=c["text"],
                   indicatorbackground=c["suprafata"], indicatorforeground=c["accent"])
    stil.map("TCheckbutton", background=[("active", c["fundal"])],
             indicatorbackground=[("selected", c["suprafata"])])
    stil.configure("TEntry", fieldbackground=c["suprafata"], foreground=c["text"],
                   insertcolor=c["text"], bordercolor=c["margine"])
    stil.map("TEntry", bordercolor=[("focus", c["accent"])], lightcolor=[("focus", c["accent"])])
    stil.configure("TSpinbox", fieldbackground=c["suprafata"], foreground=c["text"],
                   arrowcolor=c["text"], bordercolor=c["margine"])
    stil.configure("Treeview", background=c["suprafata"], fieldbackground=c["suprafata"],
                   foreground=c["text"], rowheight=24, bordercolor=c["margine"])
    stil.map("Treeview", background=[("selected", c["accent"])], foreground=[("selected", "white")])
    stil.configure("Treeview.Heading", background=c["principal"], foreground="white",
                   font=(FONT, 10, "bold"), bordercolor=c["principal"], relief="flat")
    stil.map("Treeview.Heading", background=[("active", c["principal_activ"])])
    stil.configure("Vertical.TScrollbar", background=c["fundal"], troughcolor=c["suprafata"],
                   bordercolor=c["margine"], arrowcolor=c["text"])


class AlegereDataOra(tk.Toplevel):
    """Fereastra cu un calendar lunar si, optional, ora si minutul.

    La "Alege", trimite textul ales ("AAAA-LL-ZZ HH:MM" sau "AAAA-LL-ZZ")
    functiei la_alegere. Zilele din viitor nu se pot alege.
    """

    def __init__(self, parinte, text_initial, la_alegere, cu_ora=True):
        super().__init__(parinte)
        self.configure(bg=CULORI["fundal"])
        self.title("Alege data și ora" if cu_ora else "Alege ziua")
        self.transient(parinte)
        self.resizable(False, False)
        self.la_alegere = la_alegere
        self.cu_ora = cu_ora
        try:
            initial = datetime.strptime(text_initial.strip()[:16], "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                initial = datetime.strptime(text_initial.strip()[:10], "%Y-%m-%d")
            except ValueError:
                initial = datetime.now()
        self.zi_aleasa = initial.date()
        self.an, self.luna = initial.year, initial.month

        cadru = ttk.Frame(self, padding=12)
        cadru.pack(fill="both", expand=True)

        antet = ttk.Frame(cadru)
        antet.pack(fill="x")
        ttk.Button(antet, text="◀", width=3, command=lambda: self.muta_luna(-1)).pack(side="left")
        self.titlu_luna = ttk.Label(antet, anchor="center", style="Total.TLabel")
        self.titlu_luna.pack(side="left", fill="x", expand=True)
        ttk.Button(antet, text="▶", width=3, command=lambda: self.muta_luna(1)).pack(side="right")

        self.grila = ttk.Frame(cadru)
        self.grila.pack(pady=8)

        if cu_ora:
            ora = ttk.Frame(cadru)
            ora.pack(pady=(0, 8))
            ttk.Label(ora, text="Ora").pack(side="left")
            self.ora = tk.StringVar(value=f"{initial.hour:02d}")
            self.minut = tk.StringVar(value=f"{initial.minute:02d}")
            ttk.Spinbox(ora, from_=0, to=23, width=4, format="%02.0f", wrap=True,
                        textvariable=self.ora).pack(side="left", padx=(8, 2))
            ttk.Label(ora, text=":").pack(side="left")
            ttk.Spinbox(ora, from_=0, to=59, width=4, format="%02.0f", wrap=True,
                        textvariable=self.minut).pack(side="left", padx=(2, 0))

        butoane = ttk.Frame(cadru)
        butoane.pack()
        ttk.Button(butoane, text="Alege", style="Principal.TButton",
                   command=self.confirma).pack(side="left", padx=4)
        ttk.Button(butoane, text="Renunță", command=self.destroy).pack(side="left", padx=4)

        self.deseneaza_luna()
        self.grab_set()

    def muta_luna(self, pas):
        luna = self.luna + pas
        self.an += (luna - 1) // 12
        self.luna = (luna - 1) % 12 + 1
        self.deseneaza_luna()

    def deseneaza_luna(self):
        for copil in self.grila.winfo_children():
            copil.destroy()
        self.titlu_luna.config(text=f"{LUNI[self.luna - 1]} {self.an}")
        for coloana, nume in enumerate(ZILE_SAPTAMANA):
            ttk.Label(self.grila, text=nume, width=4, anchor="center").grid(row=0, column=coloana)
        azi = datetime.now().date()
        saptamani = calendar.Calendar(firstweekday=0).monthdatescalendar(self.an, self.luna)
        for rand, saptamana in enumerate(saptamani, start=1):
            for coloana, zi in enumerate(saptamana):
                if zi.month != self.luna:
                    continue
                buton = tk.Button(self.grila, text=str(zi.day), width=3, relief="flat",
                                  bg=CULORI["suprafata"], fg=CULORI["text"], bd=0,
                                  activebackground=CULORI["accent_deschis"],
                                  disabledforeground=CULORI["margine"],
                                  highlightthickness=0, font=(FONT, 10),
                                  command=lambda z=zi: self.alege_zi(z))
                if zi > azi:
                    buton.config(state="disabled", bg=CULORI["fundal"])
                if zi == self.zi_aleasa:
                    buton.config(bg=CULORI["accent"], fg="white", activebackground=CULORI["accent_activ"],
                                 activeforeground="white", font=(FONT, 10, "bold"))
                elif zi == azi:
                    buton.config(fg=CULORI["accent"], font=(FONT, 10, "bold"))
                buton.grid(row=rand, column=coloana, padx=1, pady=1)

    def alege_zi(self, zi):
        self.zi_aleasa = zi
        self.deseneaza_luna()

    def confirma(self):
        text = self.zi_aleasa.strftime("%Y-%m-%d")
        if self.cu_ora:
            try:
                ora, minut = int(self.ora.get()), int(self.minut.get())
                if not (0 <= ora <= 23 and 0 <= minut <= 59):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Oră invalidă", "Ora trebuie să fie între 00 și 23, "
                                     "iar minutul între 00 și 59.", parent=self)
                return
            text += f" {ora:02d}:{minut:02d}"
        self.destroy()
        self.la_alegere(text)


class AplicatieCalorii(tk.Tk):
    """Fereastra principala. Schimba intre ecranul de logare si cel de lucru."""

    def __init__(self, baza):
        super().__init__()
        self.baza = baza
        self.utilizator = None
        self.alimente = []
        self.afisate = []
        self.title("Calculator de calorii")
        self.geometry("1200x680")
        self.minsize(1000, 600)
        self.protocol("WM_DELETE_WINDOW", self.inchide)
        aplica_stilul(self)
        self.ecran = None
        self.arata_logare()

    def schimba_ecran(self, ecran):
        if self.ecran is not None:
            self.ecran.destroy()
        self.ecran = ecran
        self.ecran.pack(fill="both", expand=True)

    # ---------- Ecranul de logare ----------

    def _cutie_centrala(self):
        ecran = ttk.Frame(self, padding=40)
        cutie = ttk.Frame(ecran)
        cutie.place(relx=0.5, rely=0.45, anchor="center")
        ttk.Label(cutie, text="Calculator de calorii", style="Titlu.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        return ecran, cutie

    def arata_logare(self):
        """Primul pas: utilizatorul spune daca are deja cont."""
        ecran, cutie = self._cutie_centrala()
        ttk.Label(cutie, text="Ai deja un cont?", style="Secundar.TLabel").grid(row=1, column=0, columnspan=2, pady=(0, 12))
        butoane = ttk.Frame(cutie)
        butoane.grid(row=2, column=0, columnspan=2)
        ttk.Button(butoane, text="Am deja cont", width=16, style="Principal.TButton",
                   command=lambda: self.arata_formular(cont_nou=False)).pack(side="left", padx=6)
        ttk.Button(butoane, text="Vreau cont nou", width=16, style="Accent.TButton",
                   command=lambda: self.arata_formular(cont_nou=True)).pack(side="left", padx=6)
        self.schimba_ecran(ecran)

    def arata_formular(self, cont_nou):
        """Al doilea pas: datele pentru autentificare sau pentru contul nou."""
        ecran, cutie = self._cutie_centrala()
        subtitlu = "Creează un cont nou" if cont_nou else "Autentificare"
        ttk.Label(cutie, text=subtitlu, style="Total.TLabel").grid(
            row=1, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(cutie, text="Utilizator").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=4)
        self.camp_nume = ttk.Entry(cutie, width=28)
        self.camp_nume.grid(row=2, column=1, pady=4)
        ttk.Label(cutie, text="Parolă").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=4)
        self.camp_parola = ttk.Entry(cutie, width=28, show="•")
        self.camp_parola.grid(row=3, column=1, pady=4)
        self.camp_confirmare = None
        if cont_nou:
            ttk.Label(cutie, text="Confirmă parola").grid(row=4, column=0, sticky="w", padx=(0, 10), pady=4)
            self.camp_confirmare = ttk.Entry(cutie, width=28, show="•")
            self.camp_confirmare.grid(row=4, column=1, pady=4)
            ttk.Label(cutie, text="Parola trebuie să aibă cel puțin 6 caractere.",
                      style="Secundar.TLabel").grid(row=6, column=0, columnspan=2, pady=(2, 0))

        self.arata_parola = tk.BooleanVar(value=False)
        ttk.Checkbutton(cutie, text="Arată parola", variable=self.arata_parola,
                        command=self.comuta_parola).grid(row=5, column=1, sticky="w", pady=(2, 0))

        actiune = self.cont_nou if cont_nou else self.autentifica
        butoane = ttk.Frame(cutie)
        butoane.grid(row=7, column=0, columnspan=2, pady=(16, 0))
        ttk.Button(butoane, text="Înapoi", command=self.arata_logare).pack(side="left", padx=4)
        ttk.Button(butoane, text="Creează contul" if cont_nou else "Intră în cont",
                   style="Principal.TButton", command=actiune).pack(side="left", padx=4)
        self.mesaj_logare = ttk.Label(cutie, text="", style="Eroare.TLabel")
        self.mesaj_logare.grid(row=8, column=0, columnspan=2, pady=(12, 0))

        ultimul_camp = self.camp_confirmare or self.camp_parola
        ultimul_camp.bind("<Return>", lambda _e: actiune())
        self.schimba_ecran(ecran)
        self.camp_nume.focus_set()

    def campuri_parola(self):
        return [c for c in (self.camp_parola, self.camp_confirmare) if c is not None]

    def comuta_parola(self):
        """Afiseaza sau ascunde parola, dupa casuta "Arata parola"."""
        caracter = "" if self.arata_parola.get() else "•"
        for camp in self.campuri_parola():
            camp.config(show=caracter)

    def eroare_logare(self, mesaj):
        """Afiseaza eroarea, goleste parola si muta cursorul in campul de parola."""
        self.mesaj_logare.config(text=mesaj)
        for camp in self.campuri_parola():
            camp.delete(0, "end")
        self.camp_parola.focus_set()

    def autentifica(self):
        self._intra(self.baza.autentifica)

    def cont_nou(self):
        if self.camp_parola.get() != self.camp_confirmare.get():
            self.eroare_logare("Parolele nu coincid.")
            return
        self._intra(self.baza.inregistreaza)

    def _intra(self, operatie):
        try:
            self.utilizator = operatie(self.camp_nume.get(), self.camp_parola.get())
        except ValueError as eroare:
            self.eroare_logare(str(eroare))
            return
        self.arata_aplicatia()

    # ---------- Ecranul principal ----------

    def arata_aplicatia(self):
        ecran = ttk.Frame(self, padding=12)
        sus = ttk.Frame(ecran)
        sus.pack(fill="x", pady=(0, 10))
        ttk.Label(sus, text=f"Conectat ca {self.utilizator['nume']}", style="Total.TLabel").pack(side="left")
        ttk.Button(sus, text="Deconectare", command=self.deconectare).pack(side="right")

        corp = ttk.Frame(ecran)
        corp.pack(fill="both", expand=True)
        corp.columnconfigure(0, weight=0)
        corp.columnconfigure(1, weight=1)
        corp.rowconfigure(0, weight=1)
        self._panou_adaugare(corp).grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._panou_rezumat(corp).grid(row=0, column=1, sticky="nsew")

        self.schimba_ecran(ecran)
        self.incarca_alimente()
        self.arata_ziua()

    def _panou_adaugare(self, parinte):
        panou = ttk.LabelFrame(parinte, text="Adaugă o masă", padding=10)
        panou.columnconfigure(0, weight=1)
        panou.rowconfigure(2, weight=1)

        ttk.Label(panou, text="Caută aliment").grid(row=0, column=0, sticky="w")
        self.text_cautare = tk.StringVar()
        self.text_cautare.trace_add("write", lambda *_: self.filtreaza())
        ttk.Entry(panou, textvariable=self.text_cautare).grid(row=1, column=0, sticky="ew", pady=(2, 6))

        lista = ttk.Frame(panou)
        lista.grid(row=2, column=0, sticky="nsew")
        lista.columnconfigure(0, weight=1)
        lista.rowconfigure(0, weight=1)
        self.lista_alimente = tk.Listbox(
            lista, exportselection=False, activestyle="none", font=(FONT, 10),
            bg=CULORI["suprafata"], fg=CULORI["text"], relief="flat", borderwidth=0,
            selectbackground=CULORI["accent"], selectforeground="white",
            highlightthickness=1, highlightbackground=CULORI["margine"],
            highlightcolor=CULORI["accent"])
        self.lista_alimente.grid(row=0, column=0, sticky="nsew")
        bara = ttk.Scrollbar(lista, orient="vertical", command=self.lista_alimente.yview)
        bara.grid(row=0, column=1, sticky="ns")
        self.lista_alimente.config(yscrollcommand=bara.set)
        self.lista_alimente.bind("<<ListboxSelect>>", lambda _e: self.arata_valori_aliment())

        self.valori_aliment = ttk.Label(panou, text="Alege un aliment din listă.", wraplength=300,
                                        style="Secundar.TLabel")
        self.valori_aliment.grid(row=3, column=0, sticky="w", pady=6)

        campuri = ttk.Frame(panou)
        campuri.grid(row=4, column=0, sticky="ew")
        campuri.columnconfigure(1, weight=1)
        ttk.Label(campuri, text="Grame").grid(row=0, column=0, sticky="w", pady=3)
        self.camp_grame = ttk.Entry(campuri, width=10)
        self.camp_grame.grid(row=0, column=1, sticky="w", pady=3)
        ttk.Label(campuri, text="Data și ora").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=3)
        self.camp_data = ttk.Entry(campuri, width=18)
        self.camp_data.grid(row=1, column=1, sticky="w", pady=3)
        ttk.Button(campuri, text="Alege…", width=7, command=self.alege_data_ora).grid(row=1, column=2, padx=(6, 0))
        ttk.Button(campuri, text="Acum", width=6, command=self.pune_acum).grid(row=1, column=3, padx=(4, 0))
        self.pune_acum()

        butoane = ttk.Frame(panou)
        butoane.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(butoane, text="Adaugă masa", style="Accent.TButton", command=self.adauga_masa).pack(side="left")
        ttk.Button(butoane, text="Aliment nou…", command=self.fereastra_aliment_nou).pack(side="right")
        self.buton_sterge_aliment = ttk.Button(panou, text="Șterge alimentul meu",
                                               command=self.sterge_aliment)
        self.buton_sterge_aliment.grid(row=6, column=0, sticky="e", pady=(6, 0))
        self.camp_grame.bind("<Return>", lambda _e: self.adauga_masa())
        return panou

    def _panou_rezumat(self, parinte):
        panou = ttk.LabelFrame(parinte, text="Rezumatul zilei", padding=10)
        panou.columnconfigure(0, weight=1)
        panou.rowconfigure(1, weight=1)

        zi = ttk.Frame(panou)
        zi.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(zi, text="◀", width=3, command=lambda: self.muta_ziua(-1)).pack(side="left")
        self.camp_zi = ttk.Entry(zi, width=12, justify="center")
        self.camp_zi.pack(side="left", padx=4)
        self.camp_zi.insert(0, acum_text()[:10])
        ttk.Button(zi, text="▶", width=3, command=lambda: self.muta_ziua(1)).pack(side="left")
        ttk.Button(zi, text="Calendar…", command=self.alege_ziua).pack(side="left", padx=(8, 0))
        ttk.Button(zi, text="Azi", command=self.ziua_de_azi).pack(side="left", padx=(8, 0))
        ttk.Button(zi, text="Afișează", command=self.arata_ziua).pack(side="left", padx=4)
        self.camp_zi.bind("<Return>", lambda _e: self.arata_ziua())

        coloane = ("ora", "aliment", "grame") + NUTRIENTI
        tabel = ttk.Frame(panou)
        tabel.grid(row=1, column=0, sticky="nsew")
        tabel.columnconfigure(0, weight=1)
        tabel.rowconfigure(0, weight=1)
        self.tabel_mese = ttk.Treeview(tabel, columns=coloane, show="headings", selectmode="browse")
        titluri = {"ora": "Ora", "aliment": "Aliment", "grame": "Grame"} | ETICHETE
        latimi = {"ora": 50, "aliment": 200, "grame": 56}
        for coloana in coloane:
            self.tabel_mese.heading(coloana, text=titluri[coloana])
            self.tabel_mese.column(coloana, width=latimi.get(coloana, 74), minwidth=40,
                                   anchor="w" if coloana == "aliment" else "e",
                                   stretch=coloana == "aliment")
        self.tabel_mese.grid(row=0, column=0, sticky="nsew")
        bara = ttk.Scrollbar(tabel, orient="vertical", command=self.tabel_mese.yview)
        bara.grid(row=0, column=1, sticky="ns")
        self.tabel_mese.config(yscrollcommand=bara.set)

        self.eticheta_total = ttk.Label(panou, text="", style="Total.TLabel")
        self.eticheta_total.grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Button(panou, text="Șterge masa selectată", command=self.sterge_masa).grid(
            row=3, column=0, sticky="e", pady=(8, 0))
        return panou

    # ---------- Actiuni ----------

    def incarca_alimente(self):
        self.alimente = self.baza.alimente(self.utilizator["id"])
        self.filtreaza()

    def filtreaza(self):
        self.afisate = cauta_alimente(self.alimente, self.text_cautare.get())
        self.lista_alimente.delete(0, "end")
        for aliment in self.afisate:
            marcaj = "  ★" if aliment.get("personal") else ""
            self.lista_alimente.insert("end", f"{aliment['nume']}{marcaj}")
        self.valori_aliment.config(text="Alege un aliment din listă.")

    def aliment_ales(self):
        selectie = self.lista_alimente.curselection()
        return self.afisate[selectie[0]] if selectie else None

    def arata_valori_aliment(self):
        aliment = self.aliment_ales()
        if aliment is None:
            return
        valori = aliment["valori_100g"]
        text = ", ".join(f"{ETICHETE[n]} {valori[n]:g}" for n in NUTRIENTI)
        self.valori_aliment.config(text=f"La 100 g: {text}\nSursa: {aliment['sursa']}")

    def alege_data_ora(self):
        def la_alegere(text):
            self.camp_data.delete(0, "end")
            self.camp_data.insert(0, text)
        AlegereDataOra(self, self.camp_data.get(), la_alegere, cu_ora=True)

    def alege_ziua(self):
        def la_alegere(text):
            self.camp_zi.delete(0, "end")
            self.camp_zi.insert(0, text)
            self.arata_ziua()
        AlegereDataOra(self, self.camp_zi.get(), la_alegere, cu_ora=False)

    def pune_acum(self):
        self.camp_data.delete(0, "end")
        self.camp_data.insert(0, acum_text())

    def adauga_masa(self):
        aliment = self.aliment_ales()
        if aliment is None:
            messagebox.showwarning("Alege un aliment", "Selectează mai întâi un aliment din listă.", parent=self)
            return
        try:
            grame = citeste_grame(self.camp_grame.get())
            masa = self.baza.adauga_masa(self.utilizator["id"], aliment, grame, self.camp_data.get())
        except ValueError as eroare:
            messagebox.showerror("Date invalide", str(eroare), parent=self)
            return
        self.camp_grame.delete(0, "end")
        self.camp_zi.delete(0, "end")
        self.camp_zi.insert(0, masa["data_ora"][:10])
        self.arata_ziua()

    def arata_ziua(self):
        try:
            zi = citeste_zi(self.camp_zi.get())
        except ValueError as eroare:
            messagebox.showerror("Zi invalidă", str(eroare), parent=self)
            return
        self.tabel_mese.delete(*self.tabel_mese.get_children())
        mese = self.baza.mese(self.utilizator["id"], zi)
        self.tabel_mese.tag_configure("alternat", background=CULORI["rand_alternat"])
        for numar, masa in enumerate(mese):
            valori = [f"{masa['valori'][n]:.1f}" for n in NUTRIENTI]
            self.tabel_mese.insert("", "end", iid=str(masa["id"]),
                                   tags=("alternat",) if numar % 2 else (),
                                   values=[masa["data_ora"][11:], masa["nume"], f"{masa['grame']:g}"] + valori)
        if not mese:
            self.eticheta_total.config(text="Nicio masă în această zi.")
            return
        total = total_pe_zi(mese, zi)
        text = "   ".join(f"{ETICHETE[n]}: {total[n]:.1f}" for n in NUTRIENTI)
        self.eticheta_total.config(text=f"Total ({len(mese)} mese)   {text}")

    def muta_ziua(self, zile):
        try:
            zi = datetime.strptime(citeste_zi(self.camp_zi.get()), "%Y-%m-%d")
        except ValueError:
            zi = datetime.now()
        self.camp_zi.delete(0, "end")
        self.camp_zi.insert(0, (zi + timedelta(days=zile)).strftime("%Y-%m-%d"))
        self.arata_ziua()

    def ziua_de_azi(self):
        self.camp_zi.delete(0, "end")
        self.camp_zi.insert(0, acum_text()[:10])
        self.arata_ziua()

    def sterge_masa(self):
        selectie = self.tabel_mese.selection()
        if not selectie:
            messagebox.showwarning("Alege o masă", "Selectează în tabel masa de șters.", parent=self)
            return
        if not messagebox.askyesno("Ștergere", "Ștergi masa selectată?", parent=self):
            return
        self.baza.sterge_masa(self.utilizator["id"], int(selectie[0]))
        self.arata_ziua()

    def sterge_aliment(self):
        aliment = self.aliment_ales()
        if aliment is None:
            messagebox.showwarning("Alege un aliment", "Selectează în listă alimentul de șters.", parent=self)
            return
        if not aliment.get("personal"):
            messagebox.showinfo("Aliment din catalog",
                                "Alimentele din catalogul comun nu se pot șterge.\n"
                                "Poți șterge doar alimentele adăugate de tine (marcate cu ★).", parent=self)
            return
        if not messagebox.askyesno("Ștergere", f"Ștergi „{aliment['nume']}” din alimentele tale?\n"
                                   "Mesele deja salvate rămân neschimbate.", parent=self):
            return
        self.baza.sterge_aliment(self.utilizator["id"], aliment["id"])
        self.text_cautare.set("")
        self.incarca_alimente()

    def fereastra_aliment_nou(self):
        fereastra = tk.Toplevel(self)
        fereastra.configure(bg=CULORI["fundal"])
        fereastra.title("Aliment nou")
        fereastra.transient(self)
        fereastra.resizable(False, False)
        cadru = ttk.Frame(fereastra, padding=16)
        cadru.pack(fill="both", expand=True)
        ttk.Label(cadru, text="Valorile de pe etichetă, la 100 g").grid(row=0, column=0, columnspan=2, pady=(0, 10))
        campuri = {}
        ttk.Label(cadru, text="Nume").grid(row=1, column=0, sticky="w", pady=3)
        campuri["nume"] = ttk.Entry(cadru, width=28)
        campuri["nume"].grid(row=1, column=1, pady=3)
        for rand, nutrient in enumerate(NUTRIENTI, start=2):
            unitate = "" if nutrient == "kcal" else " (g)"
            ttk.Label(cadru, text=ETICHETE[nutrient] + unitate).grid(row=rand, column=0, sticky="w", pady=3)
            campuri[nutrient] = ttk.Entry(cadru, width=28)
            campuri[nutrient].grid(row=rand, column=1, pady=3)

        def salveaza():
            try:
                valori = {}
                for nutrient in NUTRIENTI:
                    text = campuri[nutrient].get().strip().replace(",", ".")
                    try:
                        valori[nutrient] = float(text)
                    except ValueError:
                        raise ValueError(f"{ETICHETE[nutrient]} trebuie să fie un număr.") from None
                aliment = self.baza.adauga_aliment(self.utilizator["id"], campuri["nume"].get(), valori)
            except ValueError as eroare:
                messagebox.showerror("Date invalide", str(eroare), parent=fereastra)
                return
            fereastra.destroy()
            self.text_cautare.set(aliment["nume"])
            self.incarca_alimente()

        butoane = ttk.Frame(cadru)
        butoane.grid(row=len(NUTRIENTI) + 2, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(butoane, text="Salvează", style="Principal.TButton", command=salveaza).pack(side="left", padx=4)
        ttk.Button(butoane, text="Renunță", command=fereastra.destroy).pack(side="left", padx=4)
        campuri["nume"].focus_set()

    def deconectare(self):
        self.utilizator = None
        self.arata_logare()

    def inchide(self):
        self.baza.inchide()
        self.destroy()


def main():
    AplicatieCalorii(BazaDeDate()).mainloop()


if __name__ == "__main__":
    main()