"""
PROYECTO PARA INTELIGENCIA ARTIFICIAL
* ARREOLA GARCIA VANESSA FERNANDA   21031024
* RAMIREZ MIRELES GUSTAVO           21030017
"""

import mysql.connector as mysql
import numpy as np
import matplotlib.pyplot as plt

class Reconocedor:
    def __init__(self, host, user, password, database):
        self.conexion = self._connect(host, user, password, database)

    def _connect(self, host, user, password, database):
        return mysql.connect(host=host, user=user, passwd=password, database=database)

    def entrenar(self, ruta_archivo):
        letras = []
        with open(ruta_archivo, 'r') as archivo:
            contenido = archivo.read().strip().split("\n\n")
            for bloque in contenido:
                lineas = [linea.strip() for linea in bloque.split("\n") if linea.strip()]
                if not lineas:
                    continue
                letra = lineas[0]
                try:
                    matriz = [list(map(int, fila.split())) for fila in lineas[1:]]
                    letras.append((letra, np.array(matriz)))
                except ValueError as e:
                    print(f"Error al procesar bloque: {bloque}\nDetalles del error: {e}")
        return letras

    def calcular_frecuencias(self, letra, matriz):
        x, y = np.where(matriz == 1)
        nuevas_coordenadas = list(zip(x, y))
        cursor = self.conexion.cursor(dictionary=True)

        cursor.execute("SELECT id_letra FROM letra WHERE letra = %s;", (letra,))
        result = cursor.fetchone()

        if result:
            id_letra = result['id_letra']
            cursor.execute(
                "SELECT coorx, coory, frecuencia_acumulada FROM coordenada WHERE id_letra = %s;",
                (id_letra,)
            )
            coordenadas_actuales = {
                (fila['coorx'], fila['coory']): fila['frecuencia_acumulada']
                for fila in cursor.fetchall()
            }

            for coord in nuevas_coordenadas:
                coord = (int(coord[0]), int(coord[1]))
                if coord in coordenadas_actuales:
                    nueva_frecuencia = coordenadas_actuales[coord] + 1
                    cursor.execute(
                        "UPDATE coordenada SET frecuencia_acumulada = %s WHERE id_letra = %s AND coorx = %s AND coory = %s;",
                        (nueva_frecuencia, id_letra, coord[0], coord[1])
                    )
                else:
                    cursor.execute(
                        "INSERT INTO coordenada (coorx, coory, frecuencia_acumulada, frecuencia_relativa, id_letra) VALUES (%s, %s, %s, %s, %s);",
                        (coord[0], coord[1], 1, 0, id_letra)
                    )
        else:
            cursor.execute("INSERT INTO letra (letra) VALUES (%s);", (letra,))
            id_letra = cursor.lastrowid

            for coord in nuevas_coordenadas:
                coord = (int(coord[0]), int(coord[1]))
                cursor.execute(
                    "INSERT INTO coordenada (coorx, coory, frecuencia_acumulada, frecuencia_relativa, id_letra) VALUES (%s, %s, %s, %s, %s);",
                    (coord[0], coord[1], 1, 1 / len(nuevas_coordenadas), id_letra)
                )

        self.recalcular_frecuencia_relativa(id_letra)

    def recalcular_frecuencia_relativa(self, id_letra):
        cursor = self.conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT SUM(frecuencia_acumulada) AS total_acumulado FROM coordenada WHERE id_letra = %s;",
            (id_letra,)
        )
        total_acumulado = cursor.fetchone()['total_acumulado']

        if total_acumulado > 0:
            cursor.execute(
                "UPDATE coordenada SET frecuencia_relativa = frecuencia_acumulada / %s WHERE id_letra = %s;",
                (float(total_acumulado), id_letra)
            )
            self.conexion.commit()

    def mostrar_matriz_letra(self, letra):
        cursor = self.conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_letra FROM letra WHERE letra = %s;", (letra,))
        result = cursor.fetchone()

        if not result:
            print(f"La letra '{letra}' no está registrada en la base de datos.")
            return

        id_letra = result['id_letra']
        cursor.execute(
            "SELECT coorx, coory, frecuencia_acumulada FROM coordenada WHERE id_letra = %s;",
            (id_letra,)
        )
        data = cursor.fetchall()

        matriz = np.full((24, 24), 255)

        if data:
            max_frecuencia = max(fila['frecuencia_acumulada'] for fila in data)
            min_frecuencia = min(fila['frecuencia_acumulada'] for fila in data if fila['frecuencia_acumulada'] > 0)

            for fila in data:
                x, y = fila['coorx'], fila['coory']
                frecuencia = fila['frecuencia_acumulada']
                escala_gris = 200 - int(200 * (frecuencia - min_frecuencia) / (max_frecuencia - min_frecuencia))
                matriz[x, y] = max(escala_gris, 50)

        plt.imshow(matriz, cmap="gray", interpolation="nearest")
        plt.title(f"Frecuencias para la letra '{letra}'")
        plt.colorbar(label="Escala de grises (frecuencia)")
        plt.show()

    def predecir_letra(self, matriz):
        cursor = self.conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_letra, letra FROM letra;")
        letras = cursor.fetchall()
        puntajes = {}
        mejor_matriz = np.full(matriz.shape, 255)

        for letra in letras:
            id_letra = letra['id_letra']
            caracter = letra['letra']

            cursor.execute(
                "SELECT coorx, coory, frecuencia_acumulada FROM coordenada WHERE id_letra = %s;",
                (id_letra,)
            )
            coordenadas = cursor.fetchall()

            frecuencia_por_coordenada = {
                (fila['coorx'], fila['coory']): fila['frecuencia_acumulada'] for fila in coordenadas
            }

            puntaje = 0
            matriz_coincidencia = np.full(matriz.shape, 255)

            for x in range(matriz.shape[0]):
                for y in range(matriz.shape[1]):
                    if matriz[x, y] == 1 and (x, y) in frecuencia_por_coordenada:
                        puntaje += frecuencia_por_coordenada[(x, y)]
                        matriz_coincidencia[x, y] = 0

            puntajes[caracter] = puntaje

            if puntaje == max(puntajes.values()):
                mejor_matriz = matriz_coincidencia

        letra_predicha = max(puntajes, key=puntajes.get)

        plt.imshow(mejor_matriz, cmap="gray", interpolation="nearest")
        plt.title(f"Coincidencias para la letra '{letra_predicha}'")
        plt.colorbar(label="Escala de grises (coincidencias)")
        plt.show()

        return letra_predicha

    def predecir_frase(self, ruta_archivo):
        bloques = self.leer_matriz_completa(ruta_archivo)
        return ''.join(self.predecir_letra(bloque) for bloque in bloques)

    @staticmethod
    def leer_matriz_completa(ruta_archivo):
        with open(ruta_archivo, 'r') as archivo_leido:
            lineas = archivo_leido.read().strip().split('\n')

        bloques = []
        bloque_actual = []

        for linea in lineas:
            if linea.strip() == "x":
                if bloque_actual:
                    bloques.append(np.array(bloque_actual))
                    bloque_actual = []
            else:
                fila = list(map(int, linea.strip().split()))
                bloque_actual.append(fila)

        if bloque_actual:
            bloques.append(np.array(bloque_actual))

        return bloques
