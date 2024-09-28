from matplotlib.colors import LinearSegmentedColormap
from matplotlib import pyplot as plt
from scipy.signal import savgol_filter
from urllib.parse import unquote
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use('Agg')  


app = FastAPI()


@app.get("/")
def read_root():
   return {"Hello": "World"}

class CSVPath(BaseModel):
    path: str

@app.get("/csv/")
def process_csv(csv_path: CSVPath, q: Optional[str] = None):

    data = open(unquote(csv_path.path), "r").readlines()
    index1 = data.index("\n")
    index2 = data[index1 + 1: ].index("\n") + index1 + 1

    filas = [x.split(";") for x in data[index1+2:index2]]

    data = [x.split(";") for x in data[index2+1:]]
    frequencies = [float(x[0].replace(",",".")) for x in filas]
    matrix = np.array([[float(y.replace(",",".")) for y in x[1:-1]] for x in data[3:]]).T
    matrix_sin_ruido = matrix.copy()

    ruido_promedio = quitarRuido(matrix_sin_ruido,-60)

    ##matrix = np.array([savgol_filter(x, window_length=51, polyorder=2) for x in matrix])

    

    return {
        "frecuencia_central": getFrecuenciaCentral(matrix_sin_ruido, frequencies),
        "ancho_de_banda": getAnchoBanda(matrix_sin_ruido, frequencies),
        "amplitud": getAmplitud(matrix_sin_ruido),
        "ruido_promedio": round(ruido_promedio,2),
        "snr": getSNR(matrix_sin_ruido, ruido_promedio),
        "forma_señal_ruido": getFormaSenal(matrix, 150, frequencies, isRuido=True),
        "forma_senal_no_ruido": getFormaSenal(matrix_sin_ruido, 150, frequencies),
        "ocupacion": getOcupacion(matrix_sin_ruido, frequencies, 435*10**6, 440*10**6),
        "porcentaje_banda": getPorcentajeBanda(matrix_sin_ruido, 432*10**6, 433*10**6, frequencies),
        "espectograma_no_ruido": getEspectograma(matrix_sin_ruido, frequencies)
    }

def getFrecuenciaCentral(matrix, frequencies):

    mas_derecha = (0,float("-inf"))
    mas_izquierda = (0,float("-inf"))

    l = len(matrix[0])

    for col in range(0,l//2):
        if np.max(matrix[:,col]) >= mas_izquierda[1]:
            mas_izquierda = (col, np.max(matrix[:,col]))
        else:
            break
    
    for col in range(l-1,l//2, -1):
        if np.max(matrix[:,col]) >= mas_derecha[1]:
            mas_derecha = (col, np.max(matrix[:,col]))
        else:
            break
    
    return (frequencies[mas_izquierda[0]], frequencies[mas_derecha[0]])

def getFormaSenal(matrix, index, frequencies, isRuido = False):

    data = [round(x,2) for x in matrix[index,:].tolist()]
    print(data)
    plt.plot(frequencies, data)
    plt.title("Forma de Señal")
    plt.xlabel("Frecuencia")
    plt.ylabel("Amplitud")
    if isRuido:
        plt.savefig("images/formaSenalRuido.png")
    else:
        plt.savefig("images/formaSenalNoRuido.png")
    plt.close()

    if isRuido:
        return "images/formaSenalRuido.png"
    else:
        return "images/formaSenalNoRuido.png"

def getAnchoBanda(matrix, frequencies):

    l = len(matrix[0])

    for col in range(0,l//2):
        mayor_columna = np.max(matrix[:,col])
        if mayor_columna != -100:
            index = 0
            while matrix[index][col] != mayor_columna:
                index += 1
            break
    inicio = frequencies[col]
    while matrix[index][col] != -100:
        col += 1
    fin = frequencies[col]

    izquierda = fin-inicio

    for col in range(l-1,l//2,-1):
        mayor_columna = np.max(matrix[:,col])
        if mayor_columna != -100:
            # Buscar fila
            index = 0
            while matrix[index][col] != mayor_columna:
                index += 1
            break
    inicio = frequencies[col]
    while matrix[index][col] != -100:
        col -= 1
    fin = frequencies[col]

    derecha = inicio-fin

    return (izquierda, derecha)

def getAmplitud(matrix):
    mas_derecha = float("-inf")
    mas_izquierda = float("-inf")

    l = len(matrix[0])

    for col in range(0,l//2):
        # MAyor de la columna
        if np.max(matrix[:,col]) >= mas_izquierda:
            mas_izquierda = np.max(matrix[:,col])
        else:
            break
    
    for col in range(l-1,l//2, -1):
        # MAyor de la columna
        if np.max(matrix[:,col]) >= mas_derecha:
            mas_derecha = np.max(matrix[:,col])
        else:
            break
    
    return (mas_izquierda, mas_derecha)

def getSNR(matrix, ruido_promedio):
    amplitud = getAmplitud(matrix)
    return (amplitud[0]/ruido_promedio, amplitud[1]/ruido_promedio)


def quitarRuido(matrix, umbral):
    total = 0
    conteo = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] < umbral:
                total += matrix[i][j]
                conteo += 1
                matrix[i][j] = -100
    return total/conteo

def getPorcentajeBanda(matrix, freqIni, freqFin, frequencies):
    
    count = 0

    inicio = 0

    while(frequencies[inicio] < freqIni):
        inicio += 1
    fin = inicio
    while(frequencies[fin] < freqFin and fin <len(frequencies)-1):
        fin += 1

    for index in range(len(matrix)):
        for i in range(inicio, fin):
            if matrix[index][i] != -100:
                count+=1
                
    return round(count/(len(matrix)*(fin-inicio))*100,2)

def getOcupacion(matrix, frequencies,inf, sup):
    inicio = 0

    while(frequencies[inicio] < inf):
        inicio += 1
    fin = inicio
    while(frequencies[fin] < sup and fin <len(frequencies)-1):
        fin += 1

    used = 0

    for index in range(len(matrix)):
        for i in range(inicio, fin):
            if matrix[index][i] != -100:
                used += 1
                break
    
    return round((used/len(matrix))*100,2)

def getEspectograma(matrix, frequencies):
    colors = [
    (0, '#00D3FF'),    
    (0.33, '#09FF00'), 
    (0.75, 'yellow'), 
    (1, 'red')     
    ]

    custom_cmap = LinearSegmentedColormap.from_list('custom_coolwarm', colors)


    plt.figure(figsize=(10, 10))
    plt.imshow(matrix, aspect='auto', origin='lower', cmap=custom_cmap)
    plt.title('Spectrogram')
    plt.xlabel('Frequency MHz')
    plt.ylabel('Time')
    plt.colorbar(label='Magnitude [dBm]')
    plt.savefig("images/espectograma.png")
    plt.close()
    plt.show()

    return "images/espectograma.png"