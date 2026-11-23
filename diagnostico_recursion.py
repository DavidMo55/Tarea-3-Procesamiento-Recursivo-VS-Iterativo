"""Contrasta la recursión lineal original con el recorrido por intervalos.
No aumenta sys.setrecursionlimit ni intenta desbordar la pila nativa de C++.
Los intentos fallidos no son tiempos válidos para resolver N elementos.
"""
from pathlib import Path
import csv
import sys
from algoritmos_python import suma_lineal, suma_cola, contar_lineal

RAIZ=Path(__file__).resolve().parent
TAMANOS=(10,100,1000,10000,100000,1000000,10000000)


def main():
    filas=[]
    for nombre,f in [('suma_lineal',suma_lineal),('suma_cola',suma_cola),('conteo_lineal',contar_lineal)]:
        for n in TAMANOS:
            try:
                valor=f(n)
                esperado=n if nombre=='conteo_lineal' else n*(n+1)//2
                assert valor==esperado
                estado='correcto'
            except RecursionError:
                valor=''; estado='RecursionError: no resuelve este tamaño'
            filas.append({'funcion':nombre,'N':n,'estado':estado,'resultado':valor,
                          'limite_recursion_python':sys.getrecursionlimit()})
    with (RAIZ/'resultados'/'recursion_lineal.csv').open('w',newline='') as archivo:
        w=csv.DictWriter(archivo,fieldnames=list(filas[0]),lineterminator="\n"); w.writeheader(); w.writerows(filas)
    comparaciones=[]
    for n in TAMANOS:
        lo,hi=0,n-1; contador=0; objetivo=n-1
        while lo<=hi:
            contador+=1; medio=(lo+hi)//2
            if medio==objetivo: break
            lo=medio+1
        comparaciones.append({'N':n,'comparaciones':contador,'indice':medio})
    with (RAIZ/'resultados'/'comparaciones_busqueda.csv').open('w',newline='') as archivo:
        w=csv.DictWriter(archivo,fieldnames=list(comparaciones[0]),lineterminator="\n"); w.writeheader(); w.writerows(comparaciones)
    print('Diagnóstico de recursión lineal y contador de búsqueda: guardados.')


if __name__=='__main__': main()
