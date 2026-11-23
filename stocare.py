"""Stocarea datelor intr-o baza SQLite.

Fiecare utilizator are propriile mese si alimente personale; catalogul
comun (alimente.json) este vizibil tuturor. Validarea datelor se face
cu functiile din logica.py, deci aici ajung doar date corecte.
"""
import json
import sqlite3
from pathlib import Path

from logica import NUTRIENTI, creeaza_aliment, creeaza_masa, creeaza_utilizator, verifica_parola

FOLDER = Path(__file__).parent
FISIER_ALIMENTE = FOLDER / "alimente.json"
FISIER_BAZA = FOLDER / "date.db"


def incarca_alimente(cale=FISIER_ALIMENTE):
    """Citeste alimentele din fisierul JSON si le valideaza.

    Ridica ValueError daca fisierul lipseste, nu e JSON valid
    sau contine un aliment invalid ori un id repetat.
    """
    try:
        with open(cale, encoding="utf-8") as fisier:
            date = json.load(fisier)
    except FileNotFoundError:
        raise ValueError(f"Nu exista fisierul {cale}.") from None
    except json.JSONDecodeError:
        raise ValueError(f"Fisierul {cale} nu este JSON valid.") from None

    alimente = []
    iduri = set()
    for rand in date:
        if rand["id"] in iduri:
            raise ValueError(f"Id repetat in catalog: {rand['id']}.")
        iduri.add(rand["id"])
        aliment = creeaza_aliment(rand["id"], rand["nume"], rand["valori_100g"])
        aliment["categorie"] = rand.get("categorie", "Altele")
        aliment["sursa"] = rand.get("sursa", "")
        alimente.append(aliment)
    return alimente


class BazaDeDate:
    """Pastreaza conexiunea la fisierul SQLite si ofera operatiile aplicatiei.

    Este o clasa pentru ca toate operatiile folosesc aceeasi conexiune,
    deschisa o singura data si inchisa la final.
    """

    def __init__(self, cale=FISIER_BAZA):
        self.conexiune = sqlite3.connect(cale)
        self.conexiune.row_factory = sqlite3.Row
        self._creeaza_tabele()
        self._incarca_catalogul()

    def _creeaza_tabele(self):
        coloane = ", ".join(f"{n} REAL NOT NULL" for n in NUTRIENTI)
        self.conexiune.executescript(f"""
            CREATE TABLE IF NOT EXISTS utilizatori (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nume TEXT NOT NULL UNIQUE,
                sare TEXT NOT NULL,
                hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS alimente (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilizator_id INTEGER REFERENCES utilizatori(id),
                nume TEXT NOT NULL,
                categorie TEXT NOT NULL,
                sursa TEXT NOT NULL,
                {coloane}
            );
            CREATE TABLE IF NOT EXISTS mese (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilizator_id INTEGER NOT NULL REFERENCES utilizatori(id),
                aliment_id INTEGER NOT NULL,
                nume TEXT NOT NULL,
                grame REAL NOT NULL,
                data_ora TEXT NOT NULL,
                {coloane}
            );
        """)

    def _incarca_catalogul(self):
        """La prima pornire copiaza alimente.json in baza (catalogul comun)."""
        gol = self.conexiune.execute(
            "SELECT COUNT(*) FROM alimente WHERE utilizator_id IS NULL").fetchone()[0] == 0
        if not gol:
            return
        for aliment in incarca_alimente():
            self._insereaza_aliment(None, aliment, aliment["id"])
        self.conexiune.commit()

    def _insereaza_aliment(self, utilizator_id, aliment, identificator=None):
        valori = [aliment["valori_100g"][n] for n in NUTRIENTI]
        cursor = self.conexiune.execute(
            f"INSERT INTO alimente (id, utilizator_id, nume, categorie, sursa, {', '.join(NUTRIENTI)}) "
            f"VALUES (?, ?, ?, ?, ?, {', '.join('?' * len(NUTRIENTI))})",
            [identificator, utilizator_id, aliment["nume"],
             aliment.get("categorie", "Alimentele mele"), aliment.get("sursa", "Introdus de utilizator")]
            + valori,
        )
        return cursor.lastrowid

    # --- Utilizatori ---

    def inregistreaza(self, nume, parola):
        """Creeaza un cont nou. Ridica ValueError daca numele e deja folosit."""
        utilizator = creeaza_utilizator(nume, parola)
        try:
            cursor = self.conexiune.execute(
                "INSERT INTO utilizatori (nume, sare, hash) VALUES (?, ?, ?)",
                (utilizator["nume"], utilizator["sare"], utilizator["hash"]),
            )
        except sqlite3.IntegrityError:
            raise ValueError("Exista deja un cont cu acest nume.") from None
        self.conexiune.commit()
        return {"id": cursor.lastrowid, "nume": utilizator["nume"]}

    def autentifica(self, nume, parola):
        """Intoarce utilizatorul daca numele si parola sunt corecte."""
        rand = self.conexiune.execute(
            "SELECT * FROM utilizatori WHERE nume = ?", (nume.strip(),)).fetchone()
        if rand is None or not verifica_parola(dict(rand), parola):
            raise ValueError("Utilizator sau parola gresita.")
        return {"id": rand["id"], "nume": rand["nume"]}

    # --- Alimente ---

    def _aliment_din_rand(self, rand):
        return {
            "id": rand["id"],
            "nume": rand["nume"],
            "categorie": rand["categorie"],
            "sursa": rand["sursa"],
            "personal": rand["utilizator_id"] is not None,
            "valori_100g": {n: rand[n] for n in NUTRIENTI},
        }

    def alimente(self, utilizator_id):
        """Catalogul comun plus alimentele personale ale utilizatorului."""
        randuri = self.conexiune.execute(
            "SELECT * FROM alimente WHERE utilizator_id IS NULL OR utilizator_id = ? "
            "ORDER BY nume COLLATE NOCASE", (utilizator_id,)).fetchall()
        return [self._aliment_din_rand(r) for r in randuri]

    def adauga_aliment(self, utilizator_id, nume, valori_100g):
        """Adauga un aliment personal (vizibil doar acestui utilizator)."""
        aliment = creeaza_aliment(None, nume, valori_100g)
        identificator = self._insereaza_aliment(utilizator_id, aliment)
        self.conexiune.commit()
        aliment["id"] = identificator
        aliment["personal"] = True
        return aliment

    # --- Mese ---

    def adauga_masa(self, utilizator_id, aliment, grame, data_ora_text):
        """Valideaza si salveaza o masa. Intoarce masa cu valorile calculate."""
        masa = creeaza_masa(None, aliment, grame, data_ora_text)
        valori = [masa["valori"][n] for n in NUTRIENTI]
        cursor = self.conexiune.execute(
            f"INSERT INTO mese (utilizator_id, aliment_id, nume, grame, data_ora, {', '.join(NUTRIENTI)}) "
            f"VALUES (?, ?, ?, ?, ?, {', '.join('?' * len(NUTRIENTI))})",
            [utilizator_id, masa["aliment_id"], masa["nume"], masa["grame"], masa["data_ora"]] + valori,
        )
        self.conexiune.commit()
        masa["id"] = cursor.lastrowid
        return masa

    def mese(self, utilizator_id, zi=None):
        """Mesele utilizatorului, in ordine cronologica; doar din ziua data, daca e data."""
        interogare = "SELECT * FROM mese WHERE utilizator_id = ?"
        parametri = [utilizator_id]
        if zi:
            interogare += " AND data_ora LIKE ?"
            parametri.append(f"{zi}%")
        randuri = self.conexiune.execute(interogare + " ORDER BY data_ora", parametri).fetchall()
        return [{
            "id": r["id"],
            "aliment_id": r["aliment_id"],
            "nume": r["nume"],
            "grame": r["grame"],
            "data_ora": r["data_ora"],
            "valori": {n: r[n] for n in NUTRIENTI},
        } for r in randuri]

    def sterge_aliment(self, utilizator_id, aliment_id):
        """Sterge un aliment personal al utilizatorului.

        Alimentele din catalogul comun nu se pot sterge. Mesele deja salvate
        raman, pentru ca fiecare masa isi pastreaza numele si valorile.
        """
        cursor = self.conexiune.execute(
            "DELETE FROM alimente WHERE id = ? AND utilizator_id = ?", (aliment_id, utilizator_id))
        self.conexiune.commit()
        if cursor.rowcount == 0:
            raise ValueError("Poti sterge doar alimentele adaugate de tine.")

    def sterge_masa(self, utilizator_id, masa_id):
        """Sterge o masa a utilizatorului. ValueError daca nu exista."""
        cursor = self.conexiune.execute(
            "DELETE FROM mese WHERE id = ? AND utilizator_id = ?", (masa_id, utilizator_id))
        self.conexiune.commit()
        if cursor.rowcount == 0:
            raise ValueError("Masa nu exista.")

    def inchide(self):
        self.conexiune.close()