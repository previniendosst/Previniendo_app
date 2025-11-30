import random
from string import digits


def generar_cadena_aleatoria(longitud):
    cadena = ''
    for _ in range(longitud):
        cadena += random.choice(digits)

    return cadena
