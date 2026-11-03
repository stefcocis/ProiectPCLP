sarcini = [
    {"id": 1, "titlu": "Alegerea temei", "gata": False},
    {"id": 2, "titlu": "Citirea cerintelor", "gata": True},
    {"id": 3, "titlu": "Crearea depozitului GitHub", "gata": False},
]

# Marcăm sarcina 1 drept finalizată
for sarcina in sarcini:
    if sarcina["id"] == 1:
        sarcina["gata"] = True

# Numărăm sarcinile rămase
ramase = 0
for sarcina in sarcini:
    if not sarcina["gata"]:
        ramase += 1

print("Sarcini ramase:", ramase)