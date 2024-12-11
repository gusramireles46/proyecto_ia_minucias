from Reconocedor import Reconocedor

if __name__ == "__main__":
    reconocedor = Reconocedor("localhost", "reconocedor", "@admin", "reconocedor")
    archivos = ["letra_m", "letra_a", "letra_s", "letra_e", "letra_r", "letra_o"]

    # for archivo in archivos:
    #     letras_matriz = reconocedor.entrenar(archivo + ".txt")
    #     for letra, matriz in letras_matriz:
    #         reconocedor.calcular_frecuencias(letra, matriz)

    reconocedor.mostrar_matriz_letra("m")
    reconocedor.mostrar_matriz_letra("a")
    reconocedor.mostrar_matriz_letra("s")
    reconocedor.mostrar_matriz_letra("e")
    reconocedor.mostrar_matriz_letra("r")
    reconocedor.mostrar_matriz_letra("o")

    # frase = reconocedor.predecir_frase("letravarias.txt")
    # print(f"Frase predicha: {frase}")
