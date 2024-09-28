import matplotlib
from matplotlib.colors import LinearSegmentedColormap
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
def process_csv(file: UploadFile = File(...), ruidoUmbral:int = -60, freqInicialOcupacion:int=435, freqFinalOcupacion:int=440, freqInicialPorcentaje:int=433, freqFinalPorcentaje:int=440):
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
    
    matrix = np.array(matrix, dtype="float64").T
    matrix_sin_ruido = [x.copy() for x in matrix]

    ruido_promedio = quitarRuido(matrix_sin_ruido, ruidoUmbral)

    matrix_sin_ruido = np.array([savgol_filter(x, window_length=51, polyorder=2) for x in matrix_sin_ruido])
    

    return {
        "frecuencia_central": getFrecuenciaCentral(matrix_sin_ruido, frequencies),
        "ancho_de_banda": getAnchoBanda(matrix_sin_ruido, frequencies),
        "amplitud": getAmplitud(matrix_sin_ruido),
        "ruido_promedio": round(ruido_promedio,2),
        "snr": getSNR(matrix_sin_ruido, ruido_promedio),
        "forma_señal_ruido": getFormaSenal(matrix, 150, frequencies, isRuido=True),
        "forma_senal_no_ruido": getFormaSenal(matrix_sin_ruido, 150, frequencies),
        "ocupacion": getOcupacion(matrix_sin_ruido, frequencies, freqInicialOcupacion*10**6, freqFinalOcupacion*10**6),
        "porcentaje_banda": getPorcentajeBanda(matrix_sin_ruido, freqInicialPorcentaje*10**6, freqFinalPorcentaje*10**6, frequencies),
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
        
        if round(mayor_columna,2) != -100:
            index = 0
            while matrix[index][col] != mayor_columna:
                index += 1
            break
    inicio = frequencies[col]

    while round(matrix[index][col],2) != -100:
        col += 1

    fin = frequencies[col]

    izquierda = fin-inicio

    for col in range(l-1,l//2,-1):
        mayor_columna = np.max(matrix[:,col])
        if round(mayor_columna,2) != -100:
            # Buscar fila
            index = 0
            while matrix[index][col] != mayor_columna:
                index += 1
            break
    inicio = frequencies[col]
    while round(matrix[index][col],2) != -100:
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