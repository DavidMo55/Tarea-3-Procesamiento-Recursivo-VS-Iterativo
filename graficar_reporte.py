"""Gráficas de mediciones reales e informe Markdown; no inventa datos faltantes."""
from pathlib import Path
import csv
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RAIZ=Path(__file__).resolve().parent
NOMBRES={'filtrado':'Filtrado: valores mayores que 5','conteo':'Conteo de N elementos',
         'suma':'Suma de 1 a N','busqueda':'Búsqueda binaria del último elemento',
         'cuadrados':'Cuadrados de 0 a N−1'}
LABEL={'Python':'Python','C++':'C++','Octave':'Lenguaje MATLAB · GNU Octave','MATLAB':'MATLAB'}
TAMANOS=(10,100,1000,10000,100000,1000000,10000000)


def leer():
    with (RAIZ/'resultados'/'resumen.csv').open() as f: filas=list(csv.DictReader(f))
    for r in filas:
        for k in ('N','repeticiones','rss_pico_bytes','datos_entrada_bytes','capacidad_salida_bytes'):
            r[k]=int(r[k])
        r['tiempo_mediana_s']=float(r['tiempo_mediana_s']) if r['tiempo_mediana_s'] else math.nan
    return filas


def main():
    filas=leer(); graficas=RAIZ/'graficas'; graficas.mkdir(exist_ok=True)
    lenguajes=list(dict.fromkeys(r['lenguaje'] for r in filas))
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    for a,nombre in NOMBRES.items():
        fig,ejes=plt.subplots(len(lenguajes),2,figsize=(13,3.7*len(lenguajes)),squeeze=False,
                             constrained_layout=True)
        fig.suptitle(nombre+'\nIteración frente a recursión · 10 a 10 000 000 elementos',fontsize=16)
        for fila_ejes,l in zip(ejes,lenguajes):
            for m,color,marca in [('iterativo','#176d9c','o'),('recursivo','#c55726','s')]:
                datos=sorted([r for r in filas if r['algoritmo']==a and r['lenguaje']==l
                              and r['metodo']==m and r['estado']=='correcto'],key=lambda r:r['N'])
                ns=[r['N'] for r in datos]
                etiqueta=m.capitalize()+(' (híbrido)' if m=='recursivo' and a!='busqueda' else '')
                fila_ejes[0].loglog(ns,[r['tiempo_mediana_s'] for r in datos],marker=marca,color=color,label=etiqueta)
                fila_ejes[1].semilogx(ns,[r['rss_pico_bytes']/2**20 for r in datos],marker=marca,color=color,label=etiqueta)
            fila_ejes[0].set(title=LABEL[l]+' · Tiempo',ylabel='Segundos por ejecución',xlabel='N (elementos)')
            fila_ejes[1].set(title=LABEL[l]+' · Pico RSS del proceso',ylabel='Memoria (MiB)',xlabel='N (elementos)')
            pico=max(r['rss_pico_bytes']/2**20 for r in filas if r['algoritmo']==a and r['lenguaje']==l)
            fila_ejes[1].set_ylim(0,pico*1.15)
            for eje in fila_ejes:
                eje.grid(True,alpha=.25); eje.legend(); eje.set_xticks(TAMANOS)
                eje.set_xticklabels(['10','100','1k','10k','100k','1M','10M'])
        fig.savefig(graficas/f'{a}_tiempo_memoria.png',dpi=150)
        plt.close(fig)
    with (RAIZ/'resultados'/'comparaciones_busqueda.csv').open() as f: comps=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(8,4.5),constrained_layout=True)
    ax.semilogx([int(r['N']) for r in comps],[int(r['comparaciones']) for r in comps],'o-',color='#176d9c')
    ax.set(title='Búsqueda binaria: comparaciones para encontrar N−1',xlabel='N (elementos)',ylabel='Comparaciones')
    ax.set_xticks(TAMANOS); ax.set_xticklabels(['10','100','1k','10k','100k','1M','10M']); ax.grid(alpha=.25)
    fig.savefig(graficas/'comparaciones_busqueda.png',dpi=150); plt.close(fig)
    informe(filas,lenguajes)
    print('Gráficas y REPORTE.md generados.')


def informe(filas,lenguajes):
    entorno=json.loads((RAIZ/'resultados'/'entorno.json').read_text())
    total=len(filas); ok=sum(r['estado']=='correcto' for r in filas)
    mediciones=sum(r['repeticiones'] for r in filas)
    texto=f'''# Tarea 3 — Procesamiento iterativo frente a recursivo

## Objetivo y alcance
Comparar implementaciones **iterativas y recursivas** en **Python, C++ y lenguaje MATLAB**, para N = **10, 100, 1 000, 10 000, 100 000, 1 000 000 y 10 000 000**. Aquí N representa elementos o pasos lógicos, no puntos geométricos: esta tarea usa los ejemplos de la Semana 2, no las distancias de Tarea2.

Se registraron **{total} casos**, **{ok} correctos**, y **{mediciones} mediciones de tiempo**. Cada caso es una combinación de lenguaje, algoritmo, método y tamaño. Las tablas y gráficas proceden de los CSV adjuntos.

**Entorno del archivo `.m`:** '''
    texto += ('se utilizó GNU Octave. Es código de lenguaje MATLAB ejecutado en Octave; **no son mediciones del producto MATLAB**. El orquestador permite sustituirlo por MATLAB mediante `--matlab`.\n\n' if 'Octave' in lenguajes else 'se utilizó MATLAB.\n\n')
    texto += '''## 1. Relación con el notebook proporcionado
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

'''
    with (RAIZ/'resultados'/'recursion_lineal.csv').open() as f: diag=list(csv.DictReader(f))
    texto+='| Función Python | N | Estado |\n|---|---:|---|\n'
    for r in diag:
        texto+=f"| {r['funcion']} | {int(r['N']):,} | {r['estado']} |\n"
    texto+='''
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

'''
    for a,nombre in NOMBRES.items():
        texto+=f'### {nombre}\n\n| Lenguaje / entorno | N | Rep. | Tiempo iterativo (s) | Tiempo recursivo (s) | RSS iterativo (MiB) | RSS recursivo (MiB) |\n|---|---:|---:|---:|---:|---:|---:|\n'
        for l in lenguajes:
            for n in TAMANOS:
                par={r['metodo']:r for r in filas if r['algoritmo']==a and r['lenguaje']==l and r['N']==n}
                if set(par)!={'iterativo','recursivo'}: continue
                i,r=par['iterativo'],par['recursivo']
                texto+=f"| {LABEL[l]} | {n:,} | {i['repeticiones']} | {i['tiempo_mediana_s']:.8g} | {r['tiempo_mediana_s']:.8g} | {i['rss_pico_bytes']/2**20:.2f} | {r['rss_pico_bytes']/2**20:.2f} |\n"
        texto+=f'\n![Tiempo y memoria: {nombre}](graficas/{a}_tiempo_memoria.png)\n\n'
    texto+='''## 9. Interpretación
Las gráficas tienen N en escala logarítmica. El tiempo también usa escala logarítmica; la memoria se muestra en MiB con escala vertical lineal. Cada fila representa un lenguaje/entorno. **Las escalas verticales se ajustan por panel**, por lo que comparar alturas entre filas no sustituye comparar sus etiquetas o las tablas.

En filtrado, conteo, suma y cuadrados ambos métodos realizan O(N) trabajo. Dividir recursivamente no convierte una suma o un recorrido en un algoritmo O(log N): la **profundidad** es logarítmica, pero se siguen procesando N elementos. La recursión añade administración de intervalos y llamadas; no garantiza que el tiempo sea menor. También puede cambiar la localidad y la reserva temporal de recursos.

La búsqueda binaria sí realiza O(log N) comparaciones en ambas versiones. Su memoria auxiliar es O(1) en la iterativa y O(log N) en la recursiva, aunque ambas comparten una entrada O(N).

![Comparaciones de búsqueda binaria](graficas/comparaciones_busqueda.png)

Para N=10 se necesitan 4 comparaciones para encontrar el último valor; para N=10 000 000, 24. Esta es la evidencia del crecimiento logarítmico del trabajo de búsqueda, independientemente del ruido de cronometraje.

### Observaciones medidas a N=10 000 000

'''
    for a,nombre in NOMBRES.items():
        texto+=f'- **{nombre}:** '
        partes=[]
        for l in lenguajes:
            par={r['metodo']:r for r in filas if r['algoritmo']==a and r['lenguaje']==l and r['N']==10000000}
            if set(par)=={'iterativo','recursivo'}:
                i,r=par['iterativo'],par['recursivo']
                ratio=r['tiempo_mediana_s']/i['tiempo_mediana_s']
                partes.append(f"{LABEL[l]}: {i['tiempo_mediana_s']:.6g} s iterativo y {r['tiempo_mediana_s']:.6g} s recursivo (T_rec/T_iter={ratio:.2f})")
        texto+='; '.join(partes)+'.\n'
    texto+='''
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
'''+json.dumps(entorno,ensure_ascii=False,indent=2)+'''
```

La memoria se mide con el mismo mecanismo externo para los tres procesos. Aun así, no se pretende aislar el consumo de la función de su entorno. Para mayor rigor estadístico, deben repetirse también los casos grandes en condiciones controladas; aquí se informa el número real de observaciones.

La comparación distingue tres cosas: iteración, recursión lineal que puede superar la pila y recursión balanceada con profundidad pequeña. La solución no modifica el límite de recursión para ocultar el problema y no etiqueta como exitosa una ejecución que lanzó una excepción.

## Referencias técnicas
- [Python: resource.getrusage](https://docs.python.org/3/library/resource.html#resource.getrusage).
- [Python: límite de recursión](https://docs.python.org/3/library/sys.html#sys.getrecursionlimit).
- [GNU Octave: información del sistema](https://docs.octave.org/interpreter/System-Information.html).
- [MathWorks: memory](https://www.mathworks.com/help/matlab/ref/memory.html). Se eligió medición externa de RSS; la función `memory` de MATLAB tiene restricciones de plataforma.
'''
    (RAIZ/'REPORTE.md').write_text(texto)


if __name__=='__main__': main()
