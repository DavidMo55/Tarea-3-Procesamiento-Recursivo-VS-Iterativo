"""Ejemplos Semana 2: versiones iterativas y recursivas por intervalos.
La recursión de recorridos es híbrida: divide hasta bloques de 256 elementos;
en el caso base se usa el mismo bucle escalar de la versión iterativa.
La búsqueda binaria conserva la recursión pura del notebook.
"""
import argparse
import gc
import json
import sys
import time
import numpy as np

BLOQUE = 256
ALGORITMOS = ('filtrado', 'conteo', 'suma', 'busqueda', 'cuadrados')


def suma_lineal(n):
    return 0 if n == 0 else n + suma_lineal(n - 1)


def suma_cola(n, acumulador=0):
    return acumulador if n == 0 else suma_cola(n - 1, acumulador + n)


def contar_lineal(n):
    return 0 if n == 0 else 1 + contar_lineal(n - 1)


def busqueda_iterativa(datos, objetivo):
    inicio, fin = 0, len(datos) - 1
    while inicio <= fin:
        medio = (inicio + fin) // 2
        if datos[medio] == objetivo:
            return medio
        if objetivo < datos[medio]:
            fin = medio - 1
        else:
            inicio = medio + 1
    return -1


def busqueda_recursiva(datos, objetivo, inicio, fin):
    if inicio > fin:
        return -1
    medio = (inicio + fin) // 2
    if datos[medio] == objetivo:
        return medio
    if objetivo < datos[medio]:
        return busqueda_recursiva(datos, objetivo, inicio, medio - 1)
    return busqueda_recursiva(datos, objetivo, medio + 1, fin)


def ejecutar(algoritmo, metodo, n, datos):
    if algoritmo == 'busqueda':
        indice = (busqueda_iterativa(datos, n - 1) if metodo == 'iterativo'
                  else busqueda_recursiva(datos, n - 1, 0, n - 1))
        return indice, None, 0
    salida = np.empty(n, dtype=np.float64) if algoritmo in ('filtrado', 'cuadrados') else None
    acumulador, usados = 0.0, 0

    # Se selecciona el bucle fuera del recorrido, sin condicional por elemento.
    if algoritmo == 'filtrado':
        def hoja(lo, hi):
            nonlocal usados
            for i in range(lo, hi):
                valor = datos[i]
                if valor > 5:
                    salida[usados] = valor
                    usados += 1
    elif algoritmo == 'cuadrados':
        def hoja(lo, hi):
            for i in range(lo, hi):
                salida[i] = float(i) * float(i)
    elif algoritmo == 'suma':
        def hoja(lo, hi):
            nonlocal acumulador
            for i in range(lo, hi):
                acumulador += i + 1
    else:
        def hoja(lo, hi):
            nonlocal acumulador
            for i in range(lo, hi):
                acumulador += 1

    def dividir(lo, hi):
        if hi - lo <= BLOQUE:
            hoja(lo, hi)
            return
        medio = (lo + hi) // 2
        dividir(lo, medio)
        dividir(medio, hi)

    if metodo == 'iterativo':
        hoja(0, n)
    else:
        dividir(0, n)
    # Eliminar autorreferencia de la función local recursiva (evita ciclos de GC).
    dividir = None
    if algoritmo == 'filtrado':
        return float(usados), salida, usados
    if algoritmo == 'cuadrados':
        return 0.0 if n == 0 else float(salida[-1]), salida, n
    return acumulador, None, 0


def crear_datos(algoritmo, n):
    if algoritmo == 'busqueda':
        return np.arange(n, dtype=np.float64)
    if algoritmo == 'filtrado':
        # [2,3,...,9] del notebook se repite; todos los lenguajes usan lo mismo.
        datos = np.empty(n, dtype=np.float64)
        for valor in range(8):
            datos[valor::8] = valor + 2
        return datos
    return np.empty(0, dtype=np.float64)


def validar(algoritmo, n, resultado):
    valor, salida, usados = resultado
    if algoritmo == 'filtrado':
        esperado_n = (n // 8) * 4 + max(0, n % 8 - 4)
        assert valor == usados == esperado_n
        for lo in range(0, usados, 65536):
            hi = min(usados, lo + 65536)
            esperado = np.arange(lo, hi, dtype=np.float64) % 4 + 6
            np.testing.assert_array_equal(salida[lo:hi], esperado)
    elif algoritmo == 'cuadrados':
        for lo in range(0, n, 65536):
            hi = min(n, lo + 65536)
            esperado = np.arange(lo, hi, dtype=np.float64) ** 2
            np.testing.assert_array_equal(salida[lo:hi], esperado)
    else:
        esperado = {'conteo': n, 'suma': n * (n + 1) // 2, 'busqueda': n - 1}[algoritmo]
        assert valor == esperado, (valor, esperado)


def pruebas():
    for a in ALGORITMOS:
        for n in (0, 1, 8, 10, 257):
            datos = crear_datos(a, n)
            for m in ('iterativo', 'recursivo'):
                validar(a, n, ejecutar(a, m, n, datos))
    x = np.array([10., 20., 30.])
    for objetivo, esperado in ((10, 0), (20, 1), (30, 2), (25, -1), (40, -1), (0, -1)):
        assert busqueda_iterativa(x, objetivo) == esperado
        assert busqueda_recursiva(x, objetivo, 0, 2) == esperado
    assert suma_lineal(10) == suma_cola(10) == 55
    assert contar_lineal(10) == 10
    print('PRUEBAS PYTHON: correctas')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    p.add_argument('algoritmo', choices=ALGORITMOS, nargs='?')
    p.add_argument('metodo', choices=('iterativo', 'recursivo'), nargs='?')
    p.add_argument('n', type=int, nargs='?')
    p.add_argument('repeticiones', type=int, nargs='?', default=3)
    args = p.parse_args()
    if args.test:
        pruebas(); return
    a, m, n = args.algoritmo, args.metodo, args.n
    datos = crear_datos(a, n)
    # Calentamiento pequeño para no duplicar el trabajo de 10 millones.
    pequeno = min(n, 10)
    validar(a, pequeno, ejecutar(a, m, pequeno, crear_datos(a, pequeno)))
    lote = 1000 if a == 'busqueda' else 1
    for repeticion in range(args.repeticiones):
        gc.collect()
        inicio = time.perf_counter()
        for _ in range(lote):
            resultado = ejecutar(a, m, n, datos)
        segundos = (time.perf_counter() - inicio) / lote
        validar(a, n, resultado)
        print(json.dumps({'repeticion': repeticion + 1, 'segundos': segundos,
                          'valor': resultado[0], 'elementos_salida': resultado[2],
                          'lote': lote}), flush=True)
        del resultado


if __name__ == '__main__':
    main()
