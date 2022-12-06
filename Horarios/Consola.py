import codecs
import pathlib
import os
import sys
import tempfile
import time
import traceback
import matplotlib.pyplot as plt
import numpy as np

from model.Datos import Datos
from algorithm.NsgaII import NsgaII
from algorithm.Hgasso import Hgasso
from TablaHorarios import TablaHorarios


def main(nombre_del_archivo):
    tiempo_inicio = int(round(time.time() * 1000))

    datos = Datos()
    archivo_destino = str(pathlib.Path().absolute()) + nombre_del_archivo
    datos.parseFile(archivo_destino)

    #alg = NsgaII(datos)
    alg = Hgasso(datos)
    print("CARGANDO HORARIO ", alg, ".\n")
    print("ESPERE UN MOMENTITO. \n")
    alg.run()
    TablaHorarios_resultado = TablaHorarios.getResult(alg.result)

    archivo_temporal = tempfile.gettempdir() + nombre_del_archivo.replace(".json", ".htm")
    writer = codecs.open(archivo_temporal, "w", "utf-8")
    writer.write(TablaHorarios_resultado)
    writer.close()

    segundos = (int(round(time.time() * 1000)) - tiempo_inicio) / 1000.0
    print("\nCompletado en  {} segundos.\n".format(segundos))
    os.startfile(archivo_temporal)

if __name__ == "__main__":
    nombre_del_archivo = "/HorariosUAEM.json"
    if len(sys.argv) > 1:
        nombre_del_archivo = sys.argv[1]

    try:
        main(nombre_del_archivo)
    except:
        traceback.print_exc()
