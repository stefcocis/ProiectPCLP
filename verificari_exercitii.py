"""Exercitiul 4 din L3: verificari cu assert pentru exercitii_l3.py."""
from exercitii_l3 import celsius_in_fahrenheit, finalizeaza_sarcina, sarcini_active

assert celsius_in_fahrenheit(0) == 32
assert celsius_in_fahrenheit(100) == 212
assert celsius_in_fahrenheit(-40) == -40

sarcini = [
    {"id": 1, "titlu": "Alegerea temei", "gata": False},
    {"id": 2, "titlu": "Citirea cerintelor", "gata": True},
]
active = sarcini_active(sarcini)
assert [s["id"] for s in active] == [1]
assert len(sarcini) == 2
assert sarcini_active([]) == []

finalizeaza_sarcina(sarcini, 1)
assert sarcini[0]["gata"] is True
try:
    finalizeaza_sarcina(sarcini, 99)
    assert False, "Un ID inexistent trebuia respins."
except ValueError:
    pass

print("Toate verificarile pentru exercitii au trecut.")