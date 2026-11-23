# Tarea 3 — Procesamiento iterativo frente a recursivo

## Objetivo y alcance
Comparar implementaciones **iterativas y recursivas** en **Python, C++ y lenguaje MATLAB**, para N = **10, 100, 1 000, 10 000, 100 000, 1 000 000 y 10 000 000**. Aquí N representa elementos o pasos lógicos, no puntos geométricos: esta tarea usa los ejemplos de la Semana 2, no las distancias de Tarea2.

Se registraron **210 casos**, **210 correctos**, y **534 mediciones de tiempo**. Cada caso es una combinación de lenguaje, algoritmo, método y tamaño. Las tablas y gráficas proceden de los CSV adjuntos.

**Entorno del archivo `.m`:** se utilizó GNU Octave. Es código de lenguaje MATLAB ejecutado en Octave; **no son mediciones del producto MATLAB**. El orquestador permite sustituirlo por MATLAB mediante `--matlab`.

## 1. Relación con el notebook proporcionado
Fuente: `Semana 2 - Ejemplos Python.ipynb`. Se conservaron las operaciones que ilustran los ejemplos y se añadió el método que faltaba para compararlas.

| Ejemplos del notebook | Adaptación en esta entrega |
|---|---|
| Ejercicio 1: filtrar valores mayores que 5 | Filtrado iterativo y recorrido recursivo, conservando el orden |
| Ejercicio 4: contar recursivamente | Contar N pasos; se omite imprimir cada nivel para medir cálculo |
| Ejercicios 5 y 17: suma normal y de cola | Suma iterativa y recursiva por intervalos; se conserva además el diagnóstico de las funciones lineales originales |
| Ejercicios 6, 7 y 9: búsqueda binaria y comparaciones | Búsqueda iterativa y recursiva pura; contador de comparaciones |
| Ejercicios 10, 11 y 13: cuadrados | Cuadrados iterativos y recursivos; no se compara NumPy vectorizado porque ahora se pide iteración frente a recursión |
| Ejercicios 14–16: memoria y visualización | Pico RSS por proceso independiente y gráficas de tiempo y memoria |
| Ejercicio 2: listas y diccionarios heterogéneos | Contexto de representación; no es por sí mismo un algoritmo de recorrido que se pueda cronometrar para N elementos |

## 2. Datos y resultados que se calculan
- **Filtrado:** se repite `[2,3,4,5,6,7,8,9]` hasta N elementos y se conservan los valores `>5`. Para N=10, el resultado es `[6,7,8,9]`. Se reserva capacidad para N resultados; solo el prefijo de longitud `usados` contiene valores válidos. No se oculta esa reserva al medir memoria.
- **Conteo:** se incrementa un acumulador N veces y se obtiene N. Se eliminan las impresiones por elemento.
- **Suma:** se calcula `1+2+…+N`. Se valida contra `N*(N+1)/2`, pero **esa fórmula no reemplaza el algoritmo cronometrado**.
- **Búsqueda:** se utiliza el arreglo ordenado `[0,1,…,N−1]` y se busca el último elemento. El índice devuelto es N−1 en los tres programas; MATLAB convierte los índices internos de cero a uno al acceder al arreglo.
- **Cuadrados:** se genera un arreglo con `0²,1²,…,(N−1)²`. El resultado completo se valida por bloques.

Se utilizan arreglos `float64`/`double` para las entradas y salidas numéricas; los índices son enteros. Los valores y sumas del experimento son enteros representables exactamente en double. Los tres lenguajes generan los mismos datos deterministas, sin depender de generadores aleatorios ni de semillas distintas. En Octave la entrada de búsqueda se materializa explícitamente en un arreglo double; se evita que `0:N-1` quede almacenado como un rango compacto. No se almacena un archivo gigante de entrada innecesario.

## 3. Cómo se construyeron las dos versiones
### Versión iterativa
Un `for` procesa cada elemento y actualiza el resultado. La búsqueda binaria usa `while` y reduce el intervalo hasta encontrar el objetivo o dejarlo vacío. Los arreglos de salida se reservan dentro del cálculo; crear la entrada queda fuera del cronómetro.

### Versión recursiva de búsqueda binaria
Conserva la estructura del notebook: intervalo vacío como caso base, comparación con el elemento central y llamada recursiva sobre una mitad. No se copian subarreglos: se pasan índices. La profundidad es O(log N), alrededor de 24 niveles para diez millones de elementos.

### Versión recursiva de los otros recorridos: híbrida
Para filtrado, conteo, suma y cuadrados se divide `[inicio,fin)` en dos mitades. El **caso base es un bloque de hasta 256 elementos**, procesado con el mismo bucle escalar usado por la versión iterativa. Las llamadas recorren primero la mitad izquierda y luego la derecha; la salida es compartida y se conserva el orden.

```text
recorrer(inicio, fin):
    si fin - inicio <= 256:
        procesar_escalarmente(inicio, fin)
        regresar
    medio = (inicio + fin) // 2
    recorrer(inicio, medio)
    recorrer(medio, fin)
```

**Esta es recursión híbrida, no recursión lineal ni una versión totalmente recursiva por elemento.** Para N=10 y N=100 se entra directamente en el caso base y no hay subdivisión; eso explica que esos puntos midan sobre todo el mismo bucle y los costos de llamada. Para N=10 000 000, la profundidad de `recorrer` es 17 niveles; hay hasta 65 536 hojas, sin millones de llamadas anidadas. El umbral 256 permanece fijo en los tres lenguajes.

Este cambio permite completar los tamaños pedidos con una pila acotada y sin aumentar artificialmente los límites de recursión. Ambos métodos conservan las operaciones escalares; la diferencia medida incluye la administración de intervalos y llamadas recursivas. No se usa vectorización para acelerar solo uno de los dos métodos.

## 4. Qué pasa con la recursión lineal original
`suma_lineal(n)` llama a `suma_lineal(n-1)`; `suma_cola` y el conteo lineal también requieren profundidad O(N) si no hay eliminación de llamadas de cola. En Python, no se aumentó el límite de recursión. Se ejecutó el diagnóstico adjunto y se registraron los fallos como fallos, no como cálculos rápidos de diez millones de elementos.

| Función Python | N | Estado |
|---|---:|---|
| suma_lineal | 10 | correcto |
| suma_lineal | 100 | correcto |
| suma_lineal | 1,000 | RecursionError: no resuelve este tamaño |
| suma_lineal | 10,000 | RecursionError: no resuelve este tamaño |
| suma_lineal | 100,000 | RecursionError: no resuelve este tamaño |
| suma_lineal | 1,000,000 | RecursionError: no resuelve este tamaño |
| suma_lineal | 10,000,000 | RecursionError: no resuelve este tamaño |
| suma_cola | 10 | correcto |
| suma_cola | 100 | correcto |
| suma_cola | 1,000 | RecursionError: no resuelve este tamaño |
| suma_cola | 10,000 | RecursionError: no resuelve este tamaño |
| suma_cola | 100,000 | RecursionError: no resuelve este tamaño |
| suma_cola | 1,000,000 | RecursionError: no resuelve este tamaño |
| suma_cola | 10,000,000 | RecursionError: no resuelve este tamaño |
| conteo_lineal | 10 | correcto |
| conteo_lineal | 100 | correcto |
| conteo_lineal | 1,000 | RecursionError: no resuelve este tamaño |
| conteo_lineal | 10,000 | RecursionError: no resuelve este tamaño |
| conteo_lineal | 100,000 | RecursionError: no resuelve este tamaño |
| conteo_lineal | 1,000,000 | RecursionError: no resuelve este tamaño |
| conteo_lineal | 10,000,000 | RecursionError: no resuelve este tamaño |

Las tres funciones lineales están incluidas también en C++ y MATLAB como ejemplos didácticos y se prueban con N=10. **No se ejecutaron a diez millones de niveles en esos lenguajes**: no se presentan tiempos ficticios ni se provoca deliberadamente un desbordamiento de pila. Los gráficos principales corresponden a las variantes recursivas descritas arriba.

## 5. Método de cronometraje
- Cada combinación de lenguaje, algoritmo, método y N se ejecuta en un **proceso nuevo**, de forma secuencial. El orden iterativo/recursivo alterna entre tamaños.
- Se realiza un calentamiento pequeño, de hasta 10 elementos, fuera del tiempo medido. No es un calentamiento completo del tamaño grande; esto debe tenerse en cuenta al interpretar cachés y asignadores.
- Se usa `perf_counter` en Python, `steady_clock` en C++ y `tic/toc` en MATLAB/Octave.
- Para los recorridos hay **3 mediciones hasta N=100 000** y **1 medición para N=1 000 000 y N=10 000 000**. La columna conserva el número real de repeticiones. Cuando hay una sola medición, la “mediana” es esa observación, sin estimación de variabilidad.
- La búsqueda es muy breve: cada medición cronometra **1 000 búsquedas** del mismo objetivo y divide el tiempo entre 1 000. Se realizan tres lotes para todos los tamaños. El CSV registra ese lote; los tiempos son **por búsqueda**, con caché caliente en la mayor parte del lote.
- Se incluye la reserva de la salida y el cálculo. Se excluyen la generación de entradas, el arranque del proceso, las comprobaciones y la escritura de archivos. El cronómetro externo del proceso se conserva aparte en el registro, pero no se confunde con el tiempo del algoritmo.
- C++ se compila con `-O2 -fno-optimize-sibling-calls`, sin `-ffast-math`. Se evita la eliminación de llamadas de cola para conservar la estructura recursiva y se utiliza el resultado para impedir su eliminación por no usarse.

## 6. Cómo se midió la memoria
Se registró **el pico de memoria residente (RSS) del proceso hijo** mediante `wait4`, convirtiendo las unidades del sistema operativo a bytes. Las gráficas lo expresan en **MiB = bytes / 1 048 576**.

Esta medición incluye **intérprete/bibliotecas, entrada, salida, pila, temporales, validación y todas las repeticiones de ese caso**. Es un pico del proceso completo, no la memoria incremental exclusiva de la función ni el tamaño exacto de cada marco recursivo. Python reserva la salida con `np.empty`; C++ y MATLAB/Octave inicializan su reserva con ceros. En el filtrado solo se utiliza un prefijo del búfer. La capacidad lógica reservada no implica que todas sus páginas estén residentes, y esa diferencia de asignación también puede influir en el RSS. Un proceso nuevo evita arrastrar picos de otros tamaños, pero la memoria de distintas ejecuciones todavía puede variar por carga de bibliotecas, asignadores y sistema operativo.

Por eso no se debe concluir que un algoritmo “necesita” todo el RSS del intérprete. Las pequeñas diferencias entre métodos pueden ser ruido. La búsqueda tiene entrada O(N), aunque la memoria auxiliar de su algoritmo sea O(1) iterativa y O(log N) recursiva. La memoria del arreglo puede ocultar esa diferencia de pila.

El CSV también incluye **bytes lógicos de entrada y capacidad de salida**, calculados exactamente a partir de N y double de 8 bytes. Esos tamaños son contabilidad de datos, no otra medición de RSS. Para diez millones:

| Algoritmo | Entrada | Capacidad de salida | Datos numéricos totales |
|---|---:|---:|---:|
| Filtrado | 80 000 000 bytes | 80 000 000 bytes | 152.59 MiB |
| Búsqueda | 80 000 000 bytes | resultado escalar | 76.29 MiB más escalar |
| Cuadrados | sin arreglo de entrada | 80 000 000 bytes | 76.29 MiB |
| Conteo y suma | N escalar | resultado escalar | O(1), además de la pila |

No se utiliza `sys.getsizeof(lista)` como si incluyera los objetos de todos sus elementos. Tampoco se comparan mediciones de `tracemalloc` de Python con RSS de otro lenguaje como si fueran la misma magnitud.

## 7. Validación
Antes de medir, los tres programas prueban los tamaños 0, 1, 8, 10 y 257, cubriendo datos vacíos y una subdivisión recursiva. La búsqueda prueba elementos primero, intermedio y último, y objetivos ausentes por debajo, dentro y por encima del rango. Las funciones lineales se prueban con resultados conocidos.

Después de cada medición se validan conteos, sumas e índices; filtrado y cuadrados se comprueban completos, no solo con una muestra. Las comprobaciones quedan fuera del tiempo medido, pero sí forman parte del proceso cuya memoria máxima se registra. Un error detiene el orquestador y deja el registro para poder diagnosticarlo.

## 8. Resultados: tiempos y memoria
Tiempos en **segundos por ejecución**; memoria en **MiB de RSS máximo del proceso**. `Rep.` es el número de mediciones temporales por método. La recursión de búsqueda es pura; las otras cuatro son híbridas.

### Filtrado: valores mayores que 5

| Lenguaje / entorno | N | Rep. | Tiempo iterativo (s) | Tiempo recursivo (s) | RSS iterativo (MiB) | RSS recursivo (MiB) |
|---|---:|---:|---:|---:|---:|---:|
| Python | 10 | 3 | 1.0166001e-05 | 9.8340006e-06 | 39.45 | 39.50 |
| Python | 100 | 3 | 2.1125001e-05 | 2.1e-05 | 39.48 | 39.42 |
| Python | 1,000 | 3 | 0.000159041 | 0.000163875 | 39.53 | 39.30 |
| Python | 10,000 | 3 | 0.001541542 | 0.001622167 | 39.58 | 39.36 |
| Python | 100,000 | 3 | 0.015244375 | 0.015434458 | 42.23 | 42.17 |
| Python | 1,000,000 | 1 | 0.15019033 | 0.16031558 | 52.50 | 52.59 |
| Python | 10,000,000 | 1 | 1.4902383 | 1.5410544 | 155.75 | 156.23 |
| C++ | 10 | 3 | 1.25e-07 | 1.25e-07 | 1.27 | 1.27 |
| C++ | 100 | 3 | 2.92e-07 | 3.33e-07 | 1.27 | 1.27 |
| C++ | 1,000 | 3 | 1.667e-06 | 1.917e-06 | 1.30 | 1.30 |
| C++ | 10,000 | 3 | 1.8542e-05 | 1.9125e-05 | 1.45 | 1.45 |
| C++ | 100,000 | 3 | 0.00016675 | 0.000147042 | 2.83 | 2.83 |
| C++ | 1,000,000 | 1 | 0.002032416 | 0.0021735 | 16.59 | 16.59 |
| C++ | 10,000,000 | 1 | 0.023529166 | 0.021816417 | 153.91 | 153.91 |
| Lenguaje MATLAB · GNU Octave | 10 | 3 | 0.00011181831 | 0.00011396408 | 49.00 | 49.19 |
| Lenguaje MATLAB · GNU Octave | 100 | 3 | 0.00045800209 | 0.00046014786 | 48.88 | 48.41 |
| Lenguaje MATLAB · GNU Octave | 1,000 | 3 | 0.0039229393 | 0.0039141178 | 49.20 | 49.47 |
| Lenguaje MATLAB · GNU Octave | 10,000 | 3 | 0.040202141 | 0.042045832 | 49.22 | 48.97 |
| Lenguaje MATLAB · GNU Octave | 100,000 | 3 | 0.39075112 | 0.40954089 | 53.56 | 54.81 |
| Lenguaje MATLAB · GNU Octave | 1,000,000 | 1 | 3.846663 | 4.0144269 | 66.34 | 67.56 |
| Lenguaje MATLAB · GNU Octave | 10,000,000 | 1 | 37.785312 | 41.224572 | 204.83 | 204.91 |

![Tiempo y memoria: Filtrado: valores mayores que 5](graficas/filtrado_tiempo_memoria.png)

### Conteo de N elementos

| Lenguaje / entorno | N | Rep. | Tiempo iterativo (s) | Tiempo recursivo (s) | RSS iterativo (MiB) | RSS recursivo (MiB) |
|---|---:|---:|---:|---:|---:|---:|
| Python | 10 | 3 | 3.8340004e-06 | 4.5419984e-06 | 34.11 | 34.03 |
| Python | 100 | 3 | 6.3749994e-06 | 6.708e-06 | 33.86 | 34.09 |
| Python | 1,000 | 3 | 4.0708001e-05 | 4.3292001e-05 | 34.03 | 33.91 |
| Python | 10,000 | 3 | 0.00039625 | 0.000420791 | 33.89 | 34.09 |
| Python | 100,000 | 3 | 0.004023458 | 0.00408975 | 34.08 | 34.16 |
| Python | 1,000,000 | 1 | 0.040707875 | 0.041512916 | 34.08 | 34.08 |
| Python | 10,000,000 | 1 | 0.408707 | 0.41716871 | 34.11 | 33.89 |
| C++ | 10 | 3 | 4.1e-08 | 4.2e-08 | 1.27 | 1.27 |
| C++ | 100 | 3 | 2.08e-07 | 1.67e-07 | 1.27 | 1.27 |
| C++ | 1,000 | 3 | 1.583e-06 | 1.584e-06 | 1.27 | 1.27 |
| C++ | 10,000 | 3 | 1.5291e-05 | 1.5625e-05 | 1.27 | 1.27 |
| C++ | 100,000 | 3 | 0.000152458 | 0.000154958 | 1.27 | 1.27 |
| C++ | 1,000,000 | 1 | 0.001527583 | 0.001546875 | 1.27 | 1.27 |
| C++ | 10,000,000 | 1 | 0.015309459 | 0.015717625 | 1.27 | 1.27 |
| Lenguaje MATLAB · GNU Octave | 10 | 3 | 7.2002411e-05 | 8.7976456e-05 | 47.69 | 46.94 |
| Lenguaje MATLAB · GNU Octave | 100 | 3 | 0.00012779236 | 0.00013804436 | 47.22 | 47.45 |
| Lenguaje MATLAB · GNU Octave | 1,000 | 3 | 0.00063586235 | 0.00076699257 | 47.05 | 47.36 |
| Lenguaje MATLAB · GNU Octave | 10,000 | 3 | 0.0060369968 | 0.0078070164 | 47.89 | 46.88 |
| Lenguaje MATLAB · GNU Octave | 100,000 | 3 | 0.05654192 | 0.071954966 | 47.47 | 47.66 |
| Lenguaje MATLAB · GNU Octave | 1,000,000 | 1 | 0.57385206 | 0.69959903 | 47.36 | 47.41 |
| Lenguaje MATLAB · GNU Octave | 10,000,000 | 1 | 5.5494418 | 7.7726138 | 47.83 | 48.09 |

![Tiempo y memoria: Conteo de N elementos](graficas/conteo_tiempo_memoria.png)

### Suma de 1 a N

| Lenguaje / entorno | N | Rep. | Tiempo iterativo (s) | Tiempo recursivo (s) | RSS iterativo (MiB) | RSS recursivo (MiB) |
|---|---:|---:|---:|---:|---:|---:|
| Python | 10 | 3 | 4.6249988e-06 | 4.2920001e-06 | 34.12 | 33.97 |
| Python | 100 | 3 | 7.2080002e-06 | 8.166e-06 | 34.00 | 34.05 |
| Python | 1,000 | 3 | 5.6208e-05 | 5.5791999e-05 | 34.02 | 34.08 |
| Python | 10,000 | 3 | 0.000544459 | 0.000575458 | 34.03 | 34.19 |
| Python | 100,000 | 3 | 0.005444542 | 0.005400417 | 34.08 | 34.08 |
| Python | 1,000,000 | 1 | 0.057872209 | 0.05578225 | 34.08 | 34.11 |
| Python | 10,000,000 | 1 | 0.57643792 | 0.56638825 | 34.09 | 34.09 |
| C++ | 10 | 3 | 4.2e-08 | 4.2e-08 | 1.27 | 1.27 |
| C++ | 100 | 3 | 2.08e-07 | 1.67e-07 | 1.27 | 1.27 |
| C++ | 1,000 | 3 | 1.5e-06 | 1.584e-06 | 1.27 | 1.27 |
| C++ | 10,000 | 3 | 1.5292e-05 | 1.5583e-05 | 1.27 | 1.27 |
| C++ | 100,000 | 3 | 0.000152458 | 0.000155291 | 1.27 | 1.27 |
| C++ | 1,000,000 | 1 | 0.00153625 | 0.001556625 | 1.27 | 1.27 |
| C++ | 10,000,000 | 1 | 0.015407125 | 0.01557675 | 1.27 | 1.27 |
| Lenguaje MATLAB · GNU Octave | 10 | 3 | 8.0108643e-05 | 8.9883804e-05 | 47.27 | 48.08 |
| Lenguaje MATLAB · GNU Octave | 100 | 3 | 0.00016307831 | 0.00016593933 | 46.84 | 46.91 |
| Lenguaje MATLAB · GNU Octave | 1,000 | 3 | 0.00099611282 | 0.0010740757 | 47.88 | 47.80 |
| Lenguaje MATLAB · GNU Octave | 10,000 | 3 | 0.00897789 | 0.01137495 | 47.64 | 47.62 |
| Lenguaje MATLAB · GNU Octave | 100,000 | 3 | 0.08770895 | 0.10452509 | 47.91 | 47.80 |
| Lenguaje MATLAB · GNU Octave | 1,000,000 | 1 | 0.88092494 | 1.0181398 | 47.28 | 47.94 |
| Lenguaje MATLAB · GNU Octave | 10,000,000 | 1 | 9.1130359 | 10.974869 | 47.09 | 48.06 |

![Tiempo y memoria: Suma de 1 a N](graficas/suma_tiempo_memoria.png)

### Búsqueda binaria del último elemento

| Lenguaje / entorno | N | Rep. | Tiempo iterativo (s) | Tiempo recursivo (s) | RSS iterativo (MiB) | RSS recursivo (MiB) |
|---|---:|---:|---:|---:|---:|---:|
| Python | 10 | 3 | 1.162833e-06 | 1.267875e-06 | 34.03 | 34.05 |
| Python | 100 | 3 | 1.80775e-06 | 2.007334e-06 | 34.06 | 34.06 |
| Python | 1,000 | 3 | 2.8315e-06 | 3.041834e-06 | 34.06 | 34.16 |
| Python | 10,000 | 3 | 3.987416e-06 | 4.202333e-06 | 34.06 | 34.05 |
| Python | 100,000 | 3 | 4.671625e-06 | 5.117459e-06 | 34.38 | 34.38 |
| Python | 1,000,000 | 3 | 5.494083e-06 | 5.920166e-06 | 41.73 | 41.73 |
| Python | 10,000,000 | 3 | 6.415875e-06 | 7.06575e-06 | 110.53 | 110.34 |
| C++ | 10 | 3 | 9.208e-09 | 1.4875e-08 | 1.27 | 1.27 |
| C++ | 100 | 3 | 1.4417e-08 | 2.1917e-08 | 1.27 | 1.27 |
| C++ | 1,000 | 3 | 2.5375e-08 | 2.9666e-08 | 1.28 | 1.28 |
| C++ | 10,000 | 3 | 4.3833e-08 | 3.9833e-08 | 1.36 | 1.36 |
| C++ | 100,000 | 3 | 5.9125e-08 | 4.7334e-08 | 2.05 | 2.05 |
| C++ | 1,000,000 | 3 | 7.4916e-08 | 5.5333e-08 | 8.94 | 8.94 |
| C++ | 10,000,000 | 3 | 9.5917e-08 | 7.6625e-08 | 77.59 | 77.59 |
| Lenguaje MATLAB · GNU Octave | 10 | 3 | 6.237793e-05 | 8.9547873e-05 | 48.00 | 47.09 |
| Lenguaje MATLAB · GNU Octave | 100 | 3 | 9.6110821e-05 | 0.0001479969 | 47.17 | 47.55 |
| Lenguaje MATLAB · GNU Octave | 1,000 | 3 | 0.0001215241 | 0.00020070601 | 47.59 | 48.22 |
| Lenguaje MATLAB · GNU Octave | 10,000 | 3 | 0.00016090989 | 0.00027227497 | 47.72 | 48.23 |
| Lenguaje MATLAB · GNU Octave | 100,000 | 3 | 0.00018389702 | 0.00033685112 | 49.19 | 49.47 |
| Lenguaje MATLAB · GNU Octave | 1,000,000 | 3 | 0.000211972 | 0.00037633801 | 56.34 | 55.58 |
| Lenguaje MATLAB · GNU Octave | 10,000,000 | 3 | 0.00024725294 | 0.00046399879 | 125.11 | 125.00 |

![Tiempo y memoria: Búsqueda binaria del último elemento](graficas/busqueda_tiempo_memoria.png)

### Cuadrados de 0 a N−1

| Lenguaje / entorno | N | Rep. | Tiempo iterativo (s) | Tiempo recursivo (s) | RSS iterativo (MiB) | RSS recursivo (MiB) |
|---|---:|---:|---:|---:|---:|---:|
| Python | 10 | 3 | 8.5000011e-06 | 1.1667e-05 | 39.31 | 39.48 |
| Python | 100 | 3 | 1.7208e-05 | 1.7041999e-05 | 39.47 | 39.31 |
| Python | 1,000 | 3 | 0.000117166 | 0.000111917 | 39.36 | 39.50 |
| Python | 10,000 | 3 | 0.00111925 | 0.00109575 | 39.42 | 39.55 |
| Python | 100,000 | 3 | 0.011589583 | 0.011450375 | 41.67 | 41.59 |
| Python | 1,000,000 | 1 | 0.11402667 | 0.11483192 | 48.83 | 48.78 |
| Python | 10,000,000 | 1 | 1.1539707 | 1.1798795 | 117.44 | 117.41 |
| C++ | 10 | 3 | 8.3e-08 | 1.25e-07 | 1.27 | 1.27 |
| C++ | 100 | 3 | 1.67e-07 | 1.25e-07 | 1.27 | 1.27 |
| C++ | 1,000 | 3 | 7.91e-07 | 7.5e-07 | 1.30 | 1.30 |
| C++ | 10,000 | 3 | 1.1042e-05 | 1.0584e-05 | 1.38 | 1.38 |
| C++ | 100,000 | 3 | 4.3833e-05 | 4.7042e-05 | 2.06 | 2.06 |
| C++ | 1,000,000 | 1 | 0.001159042 | 0.001391709 | 8.94 | 8.94 |
| C++ | 10,000,000 | 1 | 0.013205834 | 0.01346425 | 77.59 | 77.59 |
| Lenguaje MATLAB · GNU Octave | 10 | 3 | 9.5844269e-05 | 0.00011205673 | 48.97 | 49.27 |
| Lenguaje MATLAB · GNU Octave | 100 | 3 | 0.00032496452 | 0.00033092499 | 48.78 | 49.31 |
| Lenguaje MATLAB · GNU Octave | 1,000 | 3 | 0.0025949478 | 0.0026209354 | 48.34 | 48.69 |
| Lenguaje MATLAB · GNU Octave | 10,000 | 3 | 0.024338961 | 0.026743889 | 48.92 | 49.61 |
| Lenguaje MATLAB · GNU Octave | 100,000 | 3 | 0.25019193 | 0.26897597 | 53.52 | 54.20 |
| Lenguaje MATLAB · GNU Octave | 1,000,000 | 1 | 2.516705 | 2.6718512 | 57.81 | 57.47 |
| Lenguaje MATLAB · GNU Octave | 10,000,000 | 1 | 24.263931 | 27.757135 | 127.61 | 127.84 |

![Tiempo y memoria: Cuadrados de 0 a N−1](graficas/cuadrados_tiempo_memoria.png)

## 9. Interpretación
Las gráficas tienen N en escala logarítmica. El tiempo también usa escala logarítmica; la memoria se muestra en MiB con escala vertical lineal. Cada fila representa un lenguaje/entorno. **Las escalas verticales se ajustan por panel**, por lo que comparar alturas entre filas no sustituye comparar sus etiquetas o las tablas.

En filtrado, conteo, suma y cuadrados ambos métodos realizan O(N) trabajo. Dividir recursivamente no convierte una suma o un recorrido en un algoritmo O(log N): la **profundidad** es logarítmica, pero se siguen procesando N elementos. La recursión añade administración de intervalos y llamadas; no garantiza que el tiempo sea menor. También puede cambiar la localidad y la reserva temporal de recursos.

La búsqueda binaria sí realiza O(log N) comparaciones en ambas versiones. Su memoria auxiliar es O(1) en la iterativa y O(log N) en la recursiva, aunque ambas comparten una entrada O(N).

![Comparaciones de búsqueda binaria](graficas/comparaciones_busqueda.png)

Para N=10 se necesitan 4 comparaciones para encontrar el último valor; para N=10 000 000, 24. Esta es la evidencia del crecimiento logarítmico del trabajo de búsqueda, independientemente del ruido de cronometraje.

### Observaciones medidas a N=10 000 000

- **Filtrado: valores mayores que 5:** Python: 1.49024 s iterativo y 1.54105 s recursivo (T_rec/T_iter=1.03); C++: 0.0235292 s iterativo y 0.0218164 s recursivo (T_rec/T_iter=0.93); Lenguaje MATLAB · GNU Octave: 37.7853 s iterativo y 41.2246 s recursivo (T_rec/T_iter=1.09).
- **Conteo de N elementos:** Python: 0.408707 s iterativo y 0.417169 s recursivo (T_rec/T_iter=1.02); C++: 0.0153095 s iterativo y 0.0157176 s recursivo (T_rec/T_iter=1.03); Lenguaje MATLAB · GNU Octave: 5.54944 s iterativo y 7.77261 s recursivo (T_rec/T_iter=1.40).
- **Suma de 1 a N:** Python: 0.576438 s iterativo y 0.566388 s recursivo (T_rec/T_iter=0.98); C++: 0.0154071 s iterativo y 0.0155768 s recursivo (T_rec/T_iter=1.01); Lenguaje MATLAB · GNU Octave: 9.11304 s iterativo y 10.9749 s recursivo (T_rec/T_iter=1.20).
- **Búsqueda binaria del último elemento:** Python: 6.41588e-06 s iterativo y 7.06575e-06 s recursivo (T_rec/T_iter=1.10); C++: 9.5917e-08 s iterativo y 7.6625e-08 s recursivo (T_rec/T_iter=0.80); Lenguaje MATLAB · GNU Octave: 0.000247253 s iterativo y 0.000463999 s recursivo (T_rec/T_iter=1.88).
- **Cuadrados de 0 a N−1:** Python: 1.15397 s iterativo y 1.17988 s recursivo (T_rec/T_iter=1.02); C++: 0.0132058 s iterativo y 0.0134643 s recursivo (T_rec/T_iter=1.02); Lenguaje MATLAB · GNU Octave: 24.2639 s iterativo y 27.7571 s recursivo (T_rec/T_iter=1.14).

Un cociente T_rec/T_iter mayor que 1 indica que la recursiva tardó más. Los recorridos grandes tienen una sola observación por caso: estas cifras describen la ejecución, no prueban superioridad estadística. C++ ya es código compilado; Python y Octave tienen otros costos de interpretación y bibliotecas. Los tiempos de Octave no predicen los de MATLAB ni su compilador JIT.

## 10. Archivos y reproducción
- `algoritmos_python.py`, `algoritmos_cpp.cpp`, `algoritmos_matlab.m`: las implementaciones y sus pruebas.
- `ejecutar.py`: compila C++, ejecuta casos aislados, captura tiempos y RSS, valida y genera el reporte.
- `diagnostico_recursion.py`: registra la limitación de la recursión lineal original y el contador de búsqueda.
- `graficar_reporte.py`: convierte los CSV en seis gráficas y este documento.
- `resultados/resumen.csv`: los casos con sus tiempos y memoria.
- `resultados/mediciones.csv`: mediciones temporales individuales.
- `resultados/registros.jsonl`: registro completo de ejecución y RSS por proceso.
- `resultados/logs/`: salidas de cada proceso, para auditoría.
- `resultados/recursion_lineal.csv`, `comparaciones_busqueda.csv`, `entorno.json`: diagnósticos y versiones.
- `LEEME.md`: instrucciones para ejecutarlo en VS Code o en una terminal.

## 11. Entorno y límites de las conclusiones

```json
{
  "fecha": "2026-11-22 18:29:59 -0600",
  "sistema": "macOS-26.6.2-arm64-arm-64bit-Mach-O",
  "python_numpy": "3.12.14 (main, Aug 25 2026, 13:50:33) [Clang 22.1.3 ]\nNumPy 2.5.4\n",
  "compilador": "Apple clang version 21.0.0 (clang-2100.3.34.2)",
  "flags_cpp": [
    "-std=c++17",
    "-O2",
    "-fno-optimize-sibling-calls"
  ],
  "unidad_ru_maxrss": "bytes",
  "repeticiones": "3 hasta 100000; 1 para 1000000 y 10000000; búsqueda: 3 lotes de 1000",
  "bloque_recursivo": 256,
  "lenguajes": [
    "Python",
    "C++",
    "Octave"
  ],
  "octave": "GNU Octave, version 10.3.0"
}
```

La memoria se mide con el mismo mecanismo externo para los tres procesos. Aun así, no se pretende aislar el consumo de la función de su entorno. Para mayor rigor estadístico, deben repetirse también los casos grandes en condiciones controladas; aquí se informa el número real de observaciones.

La comparación distingue tres cosas: iteración, recursión lineal que puede superar la pila y recursión balanceada con profundidad pequeña. La solución no modifica el límite de recursión para ocultar el problema y no etiqueta como exitosa una ejecución que lanzó una excepción.

## Referencias técnicas
- [Python: resource.getrusage](https://docs.python.org/3/library/resource.html#resource.getrusage).
- [Python: límite de recursión](https://docs.python.org/3/library/sys.html#sys.getrecursionlimit).
- [GNU Octave: información del sistema](https://docs.octave.org/interpreter/System-Information.html).
- [MathWorks: memory](https://www.mathworks.com/help/matlab/ref/memory.html). Se eligió medición externa de RSS; la función `memory` de MATLAB tiene restricciones de plataforma.
