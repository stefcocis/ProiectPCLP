"""Stocarea datelor: deocamdata citirea catalogului de alimente din JSON.

Mai tarziu aici vor intra si utilizatorii si mesele (SQLite).
"""
import json
from pathlib import Path

from logica import creeaza_aliment

FISIER_ALIMENTE = Path(__file__).parent / "alimente.json"


def incarca_alimente(cale=FISIER_ALIMENTE):
    """Citeste alimentele din fisierul JSON si le valideaza.

    Rezultat: lista de alimente (dictionare), fiecare cu categorie si sursa.
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