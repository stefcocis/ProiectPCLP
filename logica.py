"""Logica aplicatiei: alimente, retete, mese, rezumate si parole.

Functiile de aici nu folosesc input() si print(). Primesc date prin
parametri, intorc un rezultat si ridica ValueError la date invalide.
"""
import hashlib
import secrets
from datetime import datetime

NUTRIENTI = ("kcal", "proteine", "grasimi", "carbohidrati", "fibre")
FORMAT_DATA_ORA = "%Y-%m-%d %H:%M"


def valori_zero():
    """Intoarce un dictionar cu toti nutrientii egali cu 0."""
    valori = {}
    for nutrient in NUTRIENTI:
        valori[nutrient] = 0.0
    return valori


def creeaza_aliment(identificator, nume, valori_100g):
    """Creeaza un aliment cu valorile nutritionale la 100 g.

    Intrare: id, nume (text), dictionar cu cei 5 nutrienti.
    Rezultat: dictionar nou. Ridica ValueError pentru nume gol,
    nutrient lipsa sau valoare negativa.
    """
    nume = nume.strip()
    if not nume:
        raise ValueError("Numele alimentului nu poate fi gol.")
    valori = {}
    for nutrient in NUTRIENTI:
        if nutrient not in valori_100g:
            raise ValueError(f"Lipseste valoarea pentru {nutrient}.")
        valoare = float(valori_100g[nutrient])
        if valoare < 0:
            raise ValueError(f"Valoarea pentru {nutrient} nu poate fi negativa.")
        valori[nutrient] = valoare
    return {"id": identificator, "nume": nume, "valori_100g": valori}


def cauta_alimente(alimente, text):
    """Intoarce alimentele al caror nume contine textul cautat.

    Cautarea nu tine cont de litere mari/mici. Text gol: toate alimentele.
    """
    text = text.strip().lower()
    gasite = []
    for aliment in alimente:
        if text in aliment["nume"].lower():
            gasite.append(aliment)
    return gasite


def citeste_grame(text):
    """Transforma textul introdus (ex. "150" sau "150,5") in numar de grame."""
    try:
        grame = float(text.strip().replace(",", "."))
    except ValueError:
        raise ValueError("Gramajul trebuie sa fie un numar, de exemplu 150.") from None
    if grame <= 0:
        raise ValueError("Cantitatea trebuie sa fie pozitiva.")
    return grame


def valori_pentru_cantitate(aliment, grame):
    """Calculeaza valorile nutritionale pentru o cantitate in grame.

    Nu modifica alimentul primit. Ridica ValueError daca grame <= 0.
    """
    if grame <= 0:
        raise ValueError("Cantitatea trebuie sa fie pozitiva.")
    factor = grame / 100
    valori = {}
    for nutrient in NUTRIENTI:
        valori[nutrient] = round(aliment["valori_100g"][nutrient] * factor, 2)
    return valori


def valori_reteta(ingrediente):
    """Calculeaza valorile unei retete.

    Intrare: lista de perechi (aliment, grame).
    Rezultat: {"grame": total grame, "total": valori totale,
               "la_100g": valori la 100 g de reteta}.
    """
    if not ingrediente:
        raise ValueError("Reteta trebuie sa aiba cel putin un ingredient.")
    total = valori_zero()
    total_grame = 0
    for aliment, grame in ingrediente:
        valori = valori_pentru_cantitate(aliment, grame)
        for nutrient in NUTRIENTI:
            total[nutrient] += valori[nutrient]
        total_grame += grame
    la_100g = {}
    for nutrient in NUTRIENTI:
        la_100g[nutrient] = round(total[nutrient] * 100 / total_grame, 2)
        total[nutrient] = round(total[nutrient], 2)
    return {"grame": total_grame, "total": total, "la_100g": la_100g}


def citeste_data_ora(text):
    """Transforma un text 'AAAA-LL-ZZ HH:MM' intr-un obiect datetime."""
    try:
        return datetime.strptime(text.strip(), FORMAT_DATA_ORA)
    except ValueError:
        raise ValueError("Data si ora trebuie sa fie de forma AAAA-LL-ZZ HH:MM.") from None


def creeaza_masa(identificator, aliment, grame, data_ora_text):
    """Creeaza o masa: ce aliment, cate grame si cand a fost mancat.

    Ridica ValueError pentru gramaj invalid, data gresita sau masa in viitor.
    """
    data_ora = citeste_data_ora(data_ora_text)
    if data_ora > datetime.now():
        raise ValueError("Masa nu poate fi in viitor.")
    return {
        "id": identificator,
        "aliment_id": aliment["id"],
        "nume": aliment["nume"],
        "grame": grame,
        "data_ora": data_ora.strftime(FORMAT_DATA_ORA),
        "valori": valori_pentru_cantitate(aliment, grame),
    }


def total_pe_zi(mese, zi):
    """Aduna valorile meselor din ziua 'AAAA-LL-ZZ'. Fara mese: totaluri 0."""
    total = valori_zero()
    for masa in mese:
        if masa["data_ora"].startswith(zi):
            for nutrient in NUTRIENTI:
                total[nutrient] += masa["valori"][nutrient]
    for nutrient in NUTRIENTI:
        total[nutrient] = round(total[nutrient], 2)
    return total


def medie_zilnica(mese):
    """Media pe zi, calculata doar pentru zilele cu cel putin o masa.

    Pentru o lista goala intoarce valori 0 (fara impartire la zero).
    """
    zile = set()
    for masa in mese:
        zile.add(masa["data_ora"][:10])
    medie = valori_zero()
    if not zile:
        return medie
    for zi in zile:
        total = total_pe_zi(mese, zi)
        for nutrient in NUTRIENTI:
            medie[nutrient] += total[nutrient]
    for nutrient in NUTRIENTI:
        medie[nutrient] = round(medie[nutrient] / len(zile), 2)
    return medie


def calculeaza_hash(parola, sare):
    """Calculeaza hash-ul unei parole cu o sare data (text hex)."""
    rezultat = hashlib.pbkdf2_hmac(
        "sha256", parola.encode("utf-8"), bytes.fromhex(sare), 100_000
    )
    return rezultat.hex()


def creeaza_utilizator(nume, parola):
    """Creeaza un utilizator. Parola NU se pastreaza, doar sarea si hash-ul."""
    nume = nume.strip()
    if not nume:
        raise ValueError("Numele de utilizator nu poate fi gol.")
    if len(parola) < 6:
        raise ValueError("Parola trebuie sa aiba cel putin 6 caractere.")
    sare = secrets.token_hex(16)
    return {"nume": nume, "sare": sare, "hash": calculeaza_hash(parola, sare)}


def verifica_parola(utilizator, parola):
    """Intoarce True daca parola corespunde utilizatorului, altfel False."""
    hash_nou = calculeaza_hash(parola, utilizator["sare"])
    return secrets.compare_digest(hash_nou, utilizator["hash"])