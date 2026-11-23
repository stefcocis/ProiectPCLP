"""Aplicatia in terminal: autentificare, adaugarea meselor si rezumatul zilei."""
import sys
from getpass import getpass

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
    "proteine": "Proteine (g)",
    "grasimi": "Grasimi (g)",
    "carbohidrati": "Carbohidrati (g)",
    "fibre": "Fibre (g)",
}


def citeste_parola(mesaj):
    """Ascunde parola intr-un terminal real; in consola PyCharm o citeste normal."""
    if sys.stdin.isatty():
        return getpass(mesaj)
    return input(mesaj)


def afiseaza_valori(valori):
    for nutrient in NUTRIENTI:
        print(f"   {ETICHETE[nutrient]:<17} {valori[nutrient]:>8.1f}")


def alege_aliment(baza, utilizator):
    """Cauta in catalog si intoarce alimentul ales, sau None."""
    text = input("Cauta aliment (ex. pui, orez; Enter = toate): ")
    gasite = cauta_alimente(baza.alimente(utilizator["id"]), text)
    if not gasite:
        print("Niciun aliment gasit. Il poti adauga din meniu (optiunea 3).")
        return None
    for numar, aliment in enumerate(gasite, start=1):
        kcal = aliment["valori_100g"]["kcal"]
        marcaj = " *" if aliment.get("personal") else ""
        print(f"{numar:>3}. {aliment['nume']}{marcaj} ({kcal:g} kcal/100 g)")
    alegere = input("Numarul alimentului (Enter = renunta): ").strip()
    if not alegere:
        return None
    if not alegere.isdigit() or not 1 <= int(alegere) <= len(gasite):
        raise ValueError(f"Alege un numar intre 1 si {len(gasite)}.")
    return gasite[int(alegere) - 1]


def adauga_masa(baza, utilizator):
    aliment = alege_aliment(baza, utilizator)
    if aliment is None:
        return
    grame = citeste_grame(input(f"Cate grame de {aliment['nume']}? "))
    data_ora = input(f"Data si ora (AAAA-LL-ZZ HH:MM, Enter = acum {acum_text()}): ").strip()
    masa = baza.adauga_masa(utilizator["id"], aliment, grame, data_ora or acum_text())
    print(f"\nAm salvat: {masa['grame']:g} g {masa['nume']} la {masa['data_ora']}")
    afiseaza_valori(masa["valori"])


def adauga_aliment_nou(baza, utilizator):
    print("Aliment nou (valorile de pe eticheta, la 100 g)")
    nume = input("Nume: ")
    valori = {}
    for nutrient in NUTRIENTI:
        text = input(f"{ETICHETE[nutrient]} la 100 g: ").replace(",", ".")
        try:
            valori[nutrient] = float(text)
        except ValueError:
            raise ValueError(f"Valoarea pentru {ETICHETE[nutrient]} trebuie sa fie un numar.") from None
    aliment = baza.adauga_aliment(utilizator["id"], nume, valori)
    print(f"Am adaugat \"{aliment['nume']}\" in alimentele tale.")


def sterge_aliment(baza, utilizator):
    personale = [a for a in baza.alimente(utilizator["id"]) if a["personal"]]
    if not personale:
        print("Nu ai alimente adaugate de tine.")
        return
    for numar, aliment in enumerate(personale, start=1):
        print(f"{numar:>3}. {aliment['nume']}")
    alegere = input("Numarul alimentului de sters (Enter = renunta): ").strip()
    if not alegere:
        return
    if not alegere.isdigit() or not 1 <= int(alegere) <= len(personale):
        raise ValueError(f"Alege un numar intre 1 si {len(personale)}.")
    aliment = personale[int(alegere) - 1]
    if input(f"Stergi \"{aliment['nume']}\"? (da/nu): ").strip().lower() != "da":
        print("Nu am sters nimic.")
        return
    baza.sterge_aliment(utilizator["id"], aliment["id"])
    print(f"Am sters \"{aliment['nume']}\".")


def rezumatul_zilei(baza, utilizator):
    text = input(f"Ziua (AAAA-LL-ZZ, Enter = azi {acum_text()[:10]}): ").strip()
    zi = citeste_zi(text) if text else acum_text()[:10]
    mese = baza.mese(utilizator["id"], zi)
    print(f"\n=== Rezumatul zilei {zi} ===")
    if not mese:
        print("Nicio masa inregistrata in aceasta zi.")
        return
    print(f"{'Ora':<6} {'Aliment':<38} {'Grame':>6} {'kcal':>7}")
    for masa in mese:
        print(f"{masa['data_ora'][11:]:<6} {masa['nume'][:38]:<38} "
              f"{masa['grame']:>6g} {masa['valori']['kcal']:>7.1f}")
    print(f"\nTotal ({len(mese)} mese):")
    afiseaza_valori(total_pe_zi(mese, zi))


def meniu_utilizator(baza, utilizator):
    optiuni = {
        "1": ("Adauga o masa", adauga_masa),
        "2": ("Rezumatul zilei", rezumatul_zilei),
        "3": ("Adauga un aliment nou", adauga_aliment_nou),
        "4": ("Sterge un aliment adaugat de mine", sterge_aliment),
    }
    while True:
        print(f"\n--- {utilizator['nume']} ---")
        for cheie, (text, _) in optiuni.items():
            print(f"{cheie}. {text}")
        print("0. Deconectare")
        alegere = input("Alege: ").strip()
        if alegere == "0":
            return
        if alegere not in optiuni:
            print("Optiune necunoscuta.")
            continue
        try:
            optiuni[alegere][1](baza, utilizator)
        except ValueError as eroare:
            print("Eroare:", eroare)


def main():
    baza = BazaDeDate()
    try:
        while True:
            print("\n=== Calculator de calorii ===")
            print("1. Autentificare")
            print("2. Cont nou")
            print("0. Iesire")
            alegere = input("Alege: ").strip()
            if alegere == "0":
                break
            if alegere not in ("1", "2"):
                print("Optiune necunoscuta.")
                continue
            nume = input("Utilizator: ")
            parola = citeste_parola("Parola: ")
            try:
                if alegere == "1":
                    utilizator = baza.autentifica(nume, parola)
                else:
                    if citeste_parola("Confirma parola: ") != parola:
                        raise ValueError("Parolele nu coincid.")
                    utilizator = baza.inregistreaza(nume, parola)
                    print("Cont creat.")
            except ValueError as eroare:
                print("Eroare:", eroare)
                continue
            meniu_utilizator(baza, utilizator)
    finally:
        baza.inchide()
    print("La revedere!")


if __name__ == "__main__":
    main()