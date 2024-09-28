from scipy.signal import savgol_filter

# Lista de amplitudes (señal)
amplitudes = [1, 2, 3, -6, 5, 6, 7, 8, 9, 10]

# Aplicar filtro Savitzky-Golay
# Ventana (ajustable) debe ser un número impar, y el orden del polinomio (aquí 2) ajusta la suavidad
suavizado = savgol_filter(amplitudes, window_length=5, polyorder=2)

print(suavizado)

import matplotlib.pyplot as plt

plt.plot(amplitudes, label="Original")
plt.plot(suavizado, label="Suavizado")
plt.legend()
plt.show()