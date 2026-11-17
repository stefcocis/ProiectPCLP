"""Verificari cu assert pentru logica proiectului (la L6 devin teste automate)."""
from logica import (
    cauta_alimente,
    citeste_grame,
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
from stocare import incarca_alimente


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


# Intrari valide
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

catalog = incarca_alimente()
assert len(catalog) == 56
assert len({a["id"] for a in catalog}) == len(catalog)
mar = cauta_alimente(catalog, "măr")[0]
assert valori_pentru_cantitate(mar, 200)["kcal"] == 104
assert all("orez" in a["nume"].lower() for a in cauta_alimente(catalog, "OREZ"))
assert len(cauta_alimente(catalog, "")) == len(catalog)

# Intrari invalide
assert este_respins(valori_pentru_cantitate, aliment, -5)
assert este_respins(creeaza_aliment, 5, "   ", aliment["valori_100g"])
assert este_respins(creeaza_masa, 3, aliment, 100, "16.11.2026 8:00")
assert este_respins(creeaza_masa, 4, aliment, 100, "2099-01-01 10:00")
assert este_respins(creeaza_utilizator, "ana", "123")
assert not verifica_parola(utilizator, "gresit")
assert este_respins(incarca_alimente, "nu_exista.json")
assert este_respins(citeste_grame, "abc")
assert este_respins(citeste_grame, "0")

# Cazuri-limita
assert valori_pentru_cantitate(aliment, 100)["kcal"] == 50
assert medie_zilnica([]) == valori_zero()
assert total_pe_zi([masa_1], "2026-11-17") == valori_zero()
assert este_respins(valori_reteta, [])
assert cauta_alimente(catalog, "ciocolata") == []

print("Toate verificarile au trecut.")