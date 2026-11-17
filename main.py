from logica import (
    cauta_alimente,
    citeste_grame,
    creeaza_aliment,
    creeaza_masa,
    creeaza_utilizator,
    medie_zilnica,
    total_pe_zi,
    valori_reteta,
    verifica_parola,
)
from stocare import incarca_alimente


def main():
    # 1. Autentificare
    utilizator = creeaza_utilizator("stefan", "parola123")
    print("Logare cu parola corecta:", verifica_parola(utilizator, "parola123"))
    print("Logare cu parola gresita:", verifica_parola(utilizator, "parola000"))

    # 2. Catalogul de alimente, citit din alimente.json
    alimente = incarca_alimente()
    print("Alimente in catalog:", len(alimente))
    dupa_nume = {}
    for aliment in alimente:
        dupa_nume[aliment["nume"]] = aliment
    mar = dupa_nume["Măr"]
    ovaz = dupa_nume["Fulgi de ovăz (cruzi)"]
    lapte = dupa_nume["Lapte semidegresat (1.5% grăsime)"]
    pui = dupa_nume["Piept de pui la grătar"]
    orez = dupa_nume["Orez alb fiert"]

    # 3. Cautare dupa nume
    gasite = cauta_alimente(alimente, "orez")
    print("Cautare 'orez':", [a["nume"] for a in gasite])

    # 4. Reteta: se calculeaza la 100 g si devine un aliment nou
    reteta = valori_reteta([(ovaz, 50), (lapte, 200), (mar, 100)])
    print("Reteta terci, total:", reteta["total"])
    print("Reteta terci, la 100 g:", reteta["la_100g"])
    terci = creeaza_aliment(1000, "Terci cu mere", reteta["la_100g"])

    # 5. Mese si rezumat
    mese = [
        creeaza_masa(1, terci, 350, "2026-11-16 08:30"),
        creeaza_masa(2, pui, 150, "2026-11-16 13:00"),
        creeaza_masa(3, orez, 200, "2026-11-16 13:00"),
        creeaza_masa(4, ovaz, 60, "2026-11-17 08:00"),
    ]
    print("Total 16.11:", total_pe_zi(mese, "2026-11-16"))
    print("Media zilnica:", medie_zilnica(mese))

    # 6. Intrare de la utilizator, cu mesaj la date invalide
    try:
        grame = citeste_grame(input("Cate grame de mar ai mancat? "))
        data_ora = input("Data si ora (AAAA-LL-ZZ HH:MM): ")
        masa = creeaza_masa(5, mar, grame, data_ora)
        print("Masa adaugata:", masa["valori"])
    except ValueError as eroare:
        print("Eroare:", eroare)


if __name__ == "__main__":
    main()