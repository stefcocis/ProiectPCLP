"""Exercitiile 1-3 din L3. Functiile nu folosesc input() si print()."""


def celsius_in_fahrenheit(celsius):
    """Intoarce temperatura in grade Fahrenheit."""
    return celsius * 9 / 5 + 32


def sarcini_active(sarcini):
    """Intoarce o lista NOUA cu sarcinile nefinalizate.

    Lista primita nu se modifica. Pentru lista goala intoarce [].
    """
    active = []
    for sarcina in sarcini:
        if not sarcina["gata"]:
            active.append(sarcina)
    return active


def finalizeaza_sarcina(sarcini, identificator):
    """Marcheaza drept finalizata sarcina cu identificatorul dat.

    ATENTIE: functia modifica lista primita.
    Ridica ValueError daca nu exista sarcina cu acest identificator.
    """
    for sarcina in sarcini:
        if sarcina["id"] == identificator:
            sarcina["gata"] = True
            return sarcina
    raise ValueError(f"Nu exista sarcina cu id {identificator}.")