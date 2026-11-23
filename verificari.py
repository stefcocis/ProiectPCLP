"""Verificari cu assert pentru logica si baza de date (la L6 devin teste automate)."""
from logica import (
    cauta_alimente,
    citeste_grame,
    citeste_zi,
    creeaza_aliment,
    creeaza_masa,
    creeaza_utilizator,
    medie_zilnica,
    total_pe_zi,
    valori_pentru_cantitate,
    valori_reteta,
    valori_zero,
    verifica_parola,
)
from stocare import BazaDeDate, incarca_alimente


def aliment_test(identificator, kcal):
    return creeaza_aliment(identificator, f"Test {identificator}", {
        "kcal": kcal, "proteine": 1, "grasimi": 1, "carbohidrati": 10, "fibre": 2})


def este_respins(functie, *argumente):
    """True daca functia ridica ValueError pentru argumentele date."""
    try:
        functie(*argumente)
    except ValueError:
        return True
    return False


# --- Logica: intrari valide ---
aliment = aliment_test(1, 50)
assert valori_pentru_cantitate(aliment, 200)["kcal"] == 100
masa_1 = creeaza_masa(1, aliment_test(2, 100), 300, "2026-11-16 08:00")
masa_2 = creeaza_masa(2, aliment_test(2, 100), 500, "2026-11-16 19:00")
assert total_pe_zi([masa_1, masa_2], "2026-11-16")["kcal"] == 800
reteta = valori_reteta([(aliment_test(3, 100), 100), (aliment_test(4, 300), 100)])
assert reteta["la_100g"]["kcal"] == 200
utilizator = creeaza_utilizator("ana", "secret123")
assert verifica_parola(utilizator, "secret123")
assert "secret123" not in str(utilizator)
assert citeste_grame(" 150,5 ") == 150.5
assert citeste_zi(" 2026-11-17 ") == "2026-11-17"

catalog = incarca_alimente()
assert len(catalog) == 56
mar = cauta_alimente(catalog, "măr")[0]
assert valori_pentru_cantitate(mar, 200)["kcal"] == 104

# --- Logica: intrari invalide ---
assert este_respins(valori_pentru_cantitate, aliment, -5)
assert este_respins(creeaza_aliment, 5, "   ", aliment["valori_100g"])
assert este_respins(creeaza_masa, 3, aliment, 100, "16.11.2026 8:00")
assert este_respins(creeaza_masa, 4, aliment, 100, "2099-01-01 10:00")
assert este_respins(creeaza_utilizator, "ana", "123")
assert not verifica_parola(utilizator, "gresit")
assert este_respins(citeste_grame, "abc")
assert este_respins(citeste_zi, "17.11.2026")
assert este_respins(incarca_alimente, "nu_exista.json")

# --- Logica: cazuri-limita ---
assert medie_zilnica([]) == valori_zero()
assert total_pe_zi([masa_1], "2026-11-17") == valori_zero()
assert este_respins(valori_reteta, [])
assert cauta_alimente(catalog, "ciocolata") == []

# --- Baza de date (in memorie, nu atinge date.db) ---
baza = BazaDeDate(":memory:")
ana = baza.inregistreaza("ana", "secret123")
dan = baza.inregistreaza("dan", "parola99")
assert baza.autentifica("ana", "secret123") == ana
assert este_respins(baza.autentifica, "ana", "gresit")
assert este_respins(baza.autentifica, "nimeni", "secret123")
assert este_respins(baza.inregistreaza, "ana", "altaparola")

pui = cauta_alimente(baza.alimente(ana["id"]), "piept de pui la")[0]
baza.adauga_masa(ana["id"], pui, 100, "2026-11-10 13:00")
baza.adauga_masa(ana["id"], pui, 200, "2026-11-10 20:00")
baza.adauga_masa(ana["id"], pui, 100, "2026-11-09 13:00")
assert total_pe_zi(baza.mese(ana["id"], "2026-11-10"), "2026-11-10")["kcal"] == 495
assert len(baza.mese(ana["id"])) == 3

# fiecare utilizator isi vede doar datele lui
propriu = baza.adauga_aliment(ana["id"], "Iaurt de casa", {
    "kcal": 60, "proteine": 3.5, "grasimi": 3, "carbohidrati": 5, "fibre": 0})
assert any(a["id"] == propriu["id"] for a in baza.alimente(ana["id"]))
assert not any(a["nume"] == "Iaurt de casa" for a in baza.alimente(dan["id"]))
assert baza.mese(dan["id"]) == []
assert este_respins(baza.sterge_aliment, dan["id"], propriu["id"])
assert este_respins(baza.sterge_aliment, ana["id"], pui["id"])
baza.sterge_aliment(ana["id"], propriu["id"])
assert not any(a["id"] == propriu["id"] for a in baza.alimente(ana["id"]))
masa_ana = baza.mese(ana["id"])[0]
assert este_respins(baza.sterge_masa, dan["id"], masa_ana["id"])
baza.sterge_masa(ana["id"], masa_ana["id"])
assert len(baza.mese(ana["id"])) == 2
assert este_respins(baza.adauga_masa, ana["id"], pui, -10, "2026-11-10 13:00")
baza.inchide()

print("Toate verificarile au trecut.")