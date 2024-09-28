import matplotlib
matplotlib.use('Agg')
from typing import Optional
from fastapi import FastAPI, UploadFile, File
from urllib.parse import unquote
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    'http://localhost:8000',
    "http://127.0.0.1:8000",
    'http://localhost:5173',
    'http://localhost:5174',
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
   return {"Hello": "World"}

class CSVPath(BaseModel):
    path: str

@app.post("/csv/")
def process_csv(file: UploadFile = File(...)):
    # Leemos csv
    data = file.file.read().decode("utf-8").replace("\r", "").split("\n")
    
    """
    with open("output.csv", "w", encoding="utf-8") as f:
        for line in data:
            f.write(line + "\n") 
    return
    """
    
    index1 = data.index("")
    header = data[:index1]
    index2 = data[index1+1:].index("")+index1+1
    fila = [x.split(";") for x in data[index1+2:index2]]
    data3 = [x.split(";") for x in data[index2+1:]]
    frequencies = [float(x[0].replace(",",".")) for x in fila]
    matrix = []
    for x in data3[3:-1]:
        fila = []
        for y in x[1:-1]:
            y = y.replace(",",".")
            fila.append(float(y))
        matrix.append(fila)
    
    matrix = np.array(matrix).T
    
            
    #matrix = np.array([[float(y.replace(",",".")) for y in x[1:-1]] for x in data3[3:]]).T
    # Suavizar
    matrix = np.array([savgol_filter(x, window_length=51, polyorder=2) for x in matrix])

    espurias = get_espurias(matrix, frequencies)

    ruido_promedio = quitar_ruido(matrix)
    # Procesamos csv
    return {
        "frecuencia central": get_frecuencia_central(matrix, frequencies),
        "ancho de banda": get_ancho_de_banda(matrix, frequencies),
        "amplitud": get_amplitud(matrix),
        "ruido promedio": ruido_promedio,
        "SNR": get_snr(matrix, ruido_promedio),
        "forma de señal": get_forma_de_senal(matrix, frequencies),
        "espurias": espurias, # TODO
        
    }

def get_espurias(matrix, frequencies):
    mas_derecha = (0,float("-inf"))
    mas_izquierda = (0,float("-inf"))

    l = len(matrix[0])

    for col in range(0,l//2):
        # MAyor de la columna
        if np.max(matrix[:,col]) >= mas_izquierda[1]:
            mas_izquierda = (col, np.max(matrix[:,col]))
        else:
            break
    
    for col in range(l-1,l//2, -1):
        # MAyor de la columna
        if np.max(matrix[:,col]) >= mas_derecha[1]:
            mas_derecha = (col, np.max(matrix[:,col]))
        else:
            break
    
    izquierda = mas_izquierda[0]
    derecha = mas_derecha[0]

    # TODO
    

def get_forma_de_senal(matrix, frequencies):

    l = len(matrix[0])

    for col in range(0,l//2):
        # MAyor de la columna
        mayor_columna = np.max(matrix[:,col])
        if mayor_columna != -100:
            # Buscar fila
            index = 0
            while matrix[index][col] != mayor_columna:
                index += 1
            break
    inicio = col
    while matrix[index][col] != -100:
        col += 1
    fin = col

    para_graficar = [round(x,2) for x in matrix[index,inicio:fin].tolist()]
    graf_freq = frequencies[inicio:fin]
    plt.plot(graf_freq, para_graficar)
    plt.title("Forma de Señal Izquierda")
    plt.xlabel("Frecuencia")
    plt.ylabel("Amplitud")
    plt.savefig("images/izquierda.png")
    plt.close()

    for col in range(l-1,l//2,-1):
        # MAyor de la columna
        mayor_columna = np.max(matrix[:,col])
        if mayor_columna != -100:
            # Buscar fila
            index = 0
            while matrix[index][col] != mayor_columna:
                index += 1
            break
    inicio = col
    while matrix[index][col] != -100:
        col -= 1
    fin = col

    para_graficar = [round(x,2) for x in matrix[index,fin+1:inicio].tolist()]
    graf_freq = frequencies[fin+1:inicio]
    plt.plot(graf_freq, para_graficar)
    plt.title("Forma de Señal Derecha")
    plt.xlabel("Frecuencia")
    plt.ylabel("Amplitud")
    plt.savefig("images/derecha.png")
    plt.close()

    return "images/izquierda.png", "images/derecha.png"

def get_snr(matrix, ruido_promedio):
    amplitud = get_amplitud(matrix)
    return (amplitud[0]/ruido_promedio, amplitud[1]/ruido_promedio)

def quitar_ruido(matrix):
    total = 0
    conteo = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] < -60:
                total += matrix[i][j]
                conteo += 1
                matrix[i][j] = -100
    return total/conteo

def get_frecuencia_central(matrix, frequencies):
    mas_derecha = (0,float("-inf"))
    mas_izquierda = (0,float("-inf"))

    l = len(matrix[0])

    for col in range(0,l//2):
        # MAyor de la columna
        if np.max(matrix[:,col]) >= mas_izquierda[1]:
            mas_izquierda = (col, np.max(matrix[:,col]))
        else:
            break
    
    for col in range(l-1,l//2, -1):
        # MAyor de la columna
        if np.max(matrix[:,col]) >= mas_derecha[1]:
            mas_derecha = (col, np.max(matrix[:,col]))
        else:
            break
    
    return (frequencies[mas_izquierda[0]], frequencies[mas_derecha[0]])

def get_ancho_de_banda(matrix, frequencies):

    l = len(matrix[0])

    for col in range(0,l//2):
        # MAyor de la columna
        mayor_columna = np.max(matrix[:,col])
        if mayor_columna != -100:
            # Buscar fila
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
        # MAyor de la columna
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

def get_amplitud(matrix):
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