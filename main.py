import mysql.connector as mysql
import numpy as np
import matplotlib.pyplot as plt

def connect():
    return mysql.connect(
        host="localhost",
        user="reconocedor",
        passwd="@admin",
        database="reconocedor"
    )

def entrenar(ruta_archivo):
    letras = []
    with open(ruta_archivo, 'r') as archivo:
        contenido = archivo.read().strip().split("\n\n")
        for bloque in contenido:
            lineas = bloque.split("\n")
            letra = lineas[0]
            matriz = [list(map(int, fila.split())) for fila in lineas[1:]]
            letras.append((letra, np.array(matriz)))
    return letras

def calcular_frecuencias(letra, matriz, conexion):
    x, y = np.where(matriz == 1)
    nuevas_coordenadas = list(zip(x, y))

    cursor = conexion.cursor(dictionary=True)

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

    recalcular_frecuencia_relativa(id_letra, conexion)

def recalcular_frecuencia_relativa(id_letra, conexion):
    cursor = conexion.cursor(dictionary=True)

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
        conexion.commit()

def mostrar_matriz_letra(letra, conexion):
    cursor = conexion.cursor(dictionary=True)

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

        # print(f"Max frecuencia: {max_frecuencia}, Min frecuencia: {min_frecuencia}")

        for fila in data:
            x, y = fila['coorx'], fila['coory']
            frecuencia = fila['frecuencia_acumulada']
            escala_gris = 200 - int(200 * (frecuencia - min_frecuencia) / (max_frecuencia - min_frecuencia))
            matriz[x, y] = max(escala_gris, 50)

    plt.imshow(matriz, cmap="gray", interpolation="nearest")
    plt.title(f"Frecuencias para la letra '{letra}'")
    plt.colorbar(label="Escala de grises (frecuencia)")
    plt.show()

conexion = connect()
archivos = ["S.txt", "A.txt"]

for archivo in archivos:
    letras_matriz = entrenar(archivo)
    for letra, matriz in letras_matriz:
        calcular_frecuencias(letra, matriz, conexion)


mostrar_matriz_letra("s", conexion)
mostrar_matriz_letra("a", conexion)