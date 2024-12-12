from Reconocedor import Reconocedor
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

if __name__ == "__main__":
    reconocedor = Reconocedor(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    archivos = ["letra_m", "letra_a", "letra_s", "letra_e", "letra_r", "letra_o"]

    for archivo in archivos:
        letras_matriz = reconocedor.entrenar("archivos_entrenamiento/" + archivo + ".txt")
        for letra, matriz in letras_matriz:
            reconocedor.calcular_frecuencias(letra, matriz)

    reconocedor.mostrar_matriz_letra("m")
    reconocedor.mostrar_matriz_letra("a")
    reconocedor.mostrar_matriz_letra("s")
    reconocedor.mostrar_matriz_letra("e")
    reconocedor.mostrar_matriz_letra("r")
    reconocedor.mostrar_matriz_letra("o")

    frase = reconocedor.predecir_frase("archivos_lectura/letravarias.txt")
    if len(frase) > 1:
        print(f"Frase: {frase}")
    else:
        print(f"Letra: {frase}")