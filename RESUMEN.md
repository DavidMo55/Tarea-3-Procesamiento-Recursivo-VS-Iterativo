# Tarea 3 — Condensado de resultados

### Comparación condensada: N = 10,000,000 elementos

Cada fila compara ambos métodos para un algoritmo y un lenguaje en el tamaño máximo. Los tiempos están en segundos y la memoria en MiB de RSS del proceso completo. **T_rec/T_iter < 1** favorece a la recursiva; **> 1** favorece a la iterativa.

| Algoritmo | Lenguaje / entorno | Iterativo (s) | Recursivo (s) | T_rec/T_iter | RSS iterativo (MiB) | RSS recursivo (MiB) |
|---|---|---:|---:|---:|---:|---:|
| Filtrado | Python | 1.6684 | 1.56941 | 0.941 | 150.66 | 150.47 |
| Filtrado | C++ | 0.0514056 | 0.0480898 | 0.935 | 153.91 | 153.91 |
| Filtrado | Lenguaje MATLAB · GNU Octave | 44.6674 | 42.7426 | 0.957 | 200.33 | 206.72 |
| Conteo | Python | 0.393128 | 0.430111 | 1.094 | 29.02 | 29.02 |
| Conteo | C++ | 0.0181161 | 0.0218845 | 1.208 | 1.27 | 1.27 |
| Conteo | Lenguaje MATLAB · GNU Octave | 5.8599 | 8.2144 | 1.402 | 47.16 | 47.66 |
| Suma | Python | 0.531486 | 0.585589 | 1.102 | 29.33 | 29.02 |
| Suma | C++ | 0.0192165 | 0.018787 | 0.978 | 1.27 | 1.27 |
| Suma | Lenguaje MATLAB · GNU Octave | 8.87602 | 11.3928 | 1.284 | 47.73 | 47.98 |
| Búsqueda | Python | 6.59446e-06 | 7.04479e-06 | 1.068 | 105.39 | 105.41 |
| Búsqueda | C++ | 1.12625e-07 | 7.5709e-08 | 0.672 | 77.59 | 77.58 |
| Búsqueda | Lenguaje MATLAB · GNU Octave | 0.000256124 | 0.000496987 | 1.940 | 124.05 | 124.89 |
| Cuadrados | Python | 2.04518 | 2.01561 | 0.986 | 112.72 | 113.39 |
| Cuadrados | C++ | 0.0152365 | 0.0209318 | 1.374 | 77.59 | 77.58 |
| Cuadrados | Lenguaje MATLAB · GNU Octave | 32.3893 | 29.8131 | 0.920 | 124.06 | 131.52 |

**Cobertura:** 15 comparaciones y 30 casos (cada combinación de algoritmo y lenguaje incluye los dos métodos).

**Lectura del cociente:** 1.20 significa que la recursiva tardó un 20% más; 0.80 significa que tardó un 20% menos. Un valor próximo a 1 indica tiempos similares.

**Conclusiones para este tamaño:**

- **Filtrado:** Python: recursiva 5.9% más rápida; C++: recursiva 6.5% más rápida; Lenguaje MATLAB · GNU Octave: recursiva 4.3% más rápida.
- **Conteo:** Python: recursiva 9.4% más lenta; C++: recursiva 20.8% más lenta; Lenguaje MATLAB · GNU Octave: recursiva 40.2% más lenta.
- **Suma:** Python: recursiva 10.2% más lenta; C++: recursiva 2.2% más rápida; Lenguaje MATLAB · GNU Octave: recursiva 28.4% más lenta.
- **Búsqueda:** Python: recursiva 6.8% más lenta; C++: recursiva 32.8% más rápida; Lenguaje MATLAB · GNU Octave: recursiva 94.0% más lenta.
- **Cuadrados:** Python: recursiva 1.4% más rápida; C++: recursiva 37.4% más lenta; Lenguaje MATLAB · GNU Octave: recursiva 8.0% más rápida.

**Memoria:** compara las dos columnas RSS dentro del mismo lenguaje. El total incluye intérprete, bibliotecas, entrada, salida y validación; no es la memoria exclusiva de la función ni permite atribuir diferencias pequeñas a la pila. Filtrado necesita entrada y salida; búsqueda conserva una entrada grande; cuadrados reserva la salida; conteo y suma usan acumuladores.

**Límites de esta comparación:** los cuatro recorridos tienen una sola medición temporal a este tamaño. La búsqueda usa la mediana de tres lotes de 1 000 búsquedas y reporta tiempo por búsqueda. La búsqueda recursiva es pura; los otros algoritmos usan recursión híbrida con bloques de 256 elementos. Las diferencias describen esta ejecución y no garantizan una ventaja estable. El código MATLAB fue ejecutado en GNU Octave; no son tiempos del producto MATLAB.

[Consultar el reporte completo y las tablas de todos los tamaños](README.md).
