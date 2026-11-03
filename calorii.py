alimente = [
    {"id": 1, "nume": "Mere", "kcal": 52, "proteine": 0.3, "grasimi": 0.2, "carbohidrati": 14}
]


def valori_pentru_cantitate(aliment, grame):
    if grame <= 0:
        raise ValueError("Cantitatea trebuie sa fie pozitiva.")

    factor = grame / 100

    return {
        "kcal": aliment["kcal"] * factor,
        "proteine": aliment["proteine"] * factor,
        "grasimi": aliment["grasimi"] * factor,
        "carbohidrati": aliment["carbohidrati"] * factor,
    }


# Testăm pentru 200g de mere
print(valori_pentru_cantitate(alimente[0], 200))