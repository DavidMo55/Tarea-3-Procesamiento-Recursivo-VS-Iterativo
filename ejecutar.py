"""Orquestador reproducible. Cada combinación corre en un proceso independiente.
Ejemplo: python3 ejecutar.py --reanudar
En macOS/Linux se usa wait4 para medir el pico RSS del proceso hijo completo.
"""
from pathlib import Path
import argparse
import csv
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import time

RAIZ = Path(__file__).resolve().parent
ALGORITMOS = ('filtrado','conteo','suma','busqueda','cuadrados')
TAMANOS = (10,100,1000,10000,100000,1000000,10000000)
FLAGS = ['-std=c++17','-O2','-fno-optimize-sibling-calls']


def configuracion():
    ruta=RAIZ/'runtime_local.json'
    c=json.loads(ruta.read_text()) if ruta.exists() else {}
    python=os.environ.get('TAREA3_PYTHON',c.get('python',sys.executable))
    octave=os.environ.get('TAREA3_OCTAVE',c.get('octave',shutil.which('octave-cli') or shutil.which('octave') or 'octave'))
    matlab=os.environ.get('TAREA3_MATLAB',shutil.which('matlab') or 'matlab')
    env=os.environ.copy()
    if c.get('python_packages') and Path(c['python_packages']).exists():
        env['PYTHONPATH']=c['python_packages']+os.pathsep+env.get('PYTHONPATH','')
    if Path(octave).is_absolute() and Path(octave).exists():
        env['OCTAVE_HOME']=str(Path(octave).parent.parent)
    env['OCTAVE_IMAGE_PATH']=str(RAIZ)
    env['MPLCONFIGDIR']=str(RAIZ/'.cache_matplotlib')
    env['MPLBACKEND']='Agg'
    return python,octave,matlab,env


def comando(lenguaje,a,m,n,reps,python,octave,matlab):
    if lenguaje=='Python':
        return [python,str(RAIZ/'algoritmos_python.py'),a,m,str(n),str(reps)]
    if lenguaje=='C++':
        return [str(RAIZ/'algoritmos_cpp'),a,m,str(n),str(reps)]
    expr=f"algoritmos_matlab('{a}','{m}',{n},{reps});"
    if lenguaje=='MATLAB':
        return [matlab,'-batch',expr]
    return [octave,'--no-init-file','--no-site-file','--no-history','--quiet','--eval',expr]


def lanzar(cmd,env,log):
    with log.open('w') as archivo:
        inicio=time.perf_counter()
        proceso=subprocess.Popen(cmd,cwd=RAIZ,env=env,stdout=archivo,stderr=subprocess.STDOUT)
        _,estado,uso=os.wait4(proceso.pid,0)
        proceso.returncode=os.waitstatus_to_exitcode(estado)
        # Darwin expresa ru_maxrss en bytes; Linux, en KiB.
        rss=int(uso.ru_maxrss if sys.platform=='darwin' else uso.ru_maxrss*1024)
    return proceso.returncode,rss,time.perf_counter()-inicio


def guardar_csv(ruta,filas):
    if not filas: return
    with ruta.open('w',newline='') as archivo:
        w=csv.DictWriter(archivo,fieldnames=list(filas[0]),lineterminator="\n")
        w.writeheader(); w.writerows(filas)


def exportar(registros):
    resumen=[]; mediciones=[]
    for r in registros:
        muestras=r['muestras']
        t=[m['segundos'] for m in muestras]
        n=r['N']; a=r['algoritmo']
        entrada=8*n if a in ('filtrado','busqueda') else 0
        salida=8*n if a in ('filtrado','cuadrados') else 0
        resumen.append({
            'lenguaje':r['lenguaje'],'algoritmo':a,'metodo':r['metodo'],'N':n,
            'estado':r['estado'],'repeticiones':len(t),
            'tiempo_mediana_s':statistics.median(t) if t else '',
            'rss_pico_bytes':r['rss_pico_bytes'],'datos_entrada_bytes':entrada,
            'capacidad_salida_bytes':salida,
            'lote_busquedas':muestras[0]['lote'] if muestras else '',
            'valor':muestras[0]['valor'] if muestras else '',
            'elementos_salida':muestras[0]['elementos_salida'] if muestras else ''})
        for m in muestras:
            mediciones.append({'lenguaje':r['lenguaje'],'algoritmo':a,'metodo':r['metodo'],
                'N':n,**m})
    guardar_csv(RAIZ/'resultados'/'resumen.csv',resumen)
    guardar_csv(RAIZ/'resultados'/'mediciones.csv',mediciones)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reanudar',action='store_true',help='Reutiliza solamente casos terminados correctamente')
    p.add_argument('--matlab',action='store_true',help='Usa MATLAB real en lugar de Octave')
    p.add_argument('--lenguajes',nargs='+',choices=['Python','C++','Octave','MATLAB'],default=None)
    p.add_argument('--tamanos',nargs='+',type=int,default=TAMANOS)
    p.add_argument('--solo-graficas',action='store_true')
    args=p.parse_args()
    if not hasattr(os,'wait4'):
        raise SystemExit('La medición externa de RSS requiere macOS o Linux; los algoritmos se pueden ejecutar por separado.')
    python,octave,matlab,env=configuracion()
    resultados=RAIZ/'resultados'; resultados.mkdir(exist_ok=True)
    logs=resultados/'logs'; logs.mkdir(exist_ok=True)
    if args.solo_graficas:
        subprocess.run([python,str(RAIZ/'graficar_reporte.py')],cwd=RAIZ,env=env,check=True); return
    lenguajes=args.lenguajes or ['Python','C++','MATLAB' if args.matlab else 'Octave']
    if 'C++' in lenguajes:
        subprocess.run(['c++',*FLAGS,str(RAIZ/'algoritmos_cpp.cpp'),'-o',str(RAIZ/'algoritmos_cpp')],check=True)
        subprocess.run([str(RAIZ/'algoritmos_cpp'),'--test'],check=True)
    if 'Python' in lenguajes:
        subprocess.run([python,str(RAIZ/'algoritmos_python.py'),'--test'],env=env,check=True)
    if any(l in lenguajes for l in ('Octave','MATLAB')):
        cmd=([matlab,'-batch',"algoritmos_matlab('test');"] if 'MATLAB' in lenguajes else
             [octave,'--no-init-file','--no-site-file','--no-history','--quiet','--eval',"algoritmos_matlab('test');"])
        subprocess.run(cmd,cwd=RAIZ,env=env,check=True)
    version_python=subprocess.check_output([python,'-c','import sys,numpy; print(sys.version); print("NumPy",numpy.__version__)'],env=env,text=True)
    version_cpp=subprocess.check_output(['c++','--version'],text=True).splitlines()[0]
    entorno={'fecha':time.strftime('%Y-%m-%d %H:%M:%S %z'),'sistema':platform.platform(),
             'python_numpy':version_python,'compilador':version_cpp,'flags_cpp':FLAGS,
             'unidad_ru_maxrss':'bytes' if sys.platform=='darwin' else 'KiB',
             'repeticiones':'3 hasta 100000; 1 para 1000000 y 10000000; búsqueda: 3 lotes de 1000',
             'bloque_recursivo':256,'lenguajes':lenguajes}
    if 'Octave' in lenguajes:
        entorno['octave']=subprocess.check_output([octave,'--version'],env=env,text=True).splitlines()[0]
    if 'MATLAB' in lenguajes:
        entorno['matlab']=subprocess.check_output([matlab,'-batch','disp(version)'],cwd=RAIZ,env=env,text=True)
    (resultados/'entorno.json').write_text(json.dumps(entorno,ensure_ascii=False,indent=2))
    journal=resultados/'registros.jsonl'
    anteriores=[json.loads(l) for l in journal.read_text().splitlines()] if args.reanudar and journal.exists() else []
    clave=lambda r:(r['lenguaje'],r['algoritmo'],r['metodo'],r['N'])
    registros={clave(r):r for r in anteriores if r['estado']=='correcto'}
    if not args.reanudar: journal.write_text('')
    total=len(lenguajes)*len(ALGORITMOS)*len(args.tamanos)*2
    avance=0
    for lenguaje in lenguajes:
        for a in ALGORITMOS:
            for j,n in enumerate(args.tamanos):
                # Alternar el orden de métodos por tamaño; cada uno tiene su propio proceso.
                metodos=('iterativo','recursivo') if j%2==0 else ('recursivo','iterativo')
                for m in metodos:
                    avance+=1; key=(lenguaje,a,m,n)
                    if key in registros: continue
                    print(f'[{avance}/{total}] {lenguaje} | {a} | {m} | N={n:,}',flush=True)
                    reps=3 if n<=100000 or a=='busqueda' else 1
                    archivo=logs/f'{lenguaje.replace("+","p")}_{a}_{m}_{n}.log'
                    cmd=comando(lenguaje,a,m,n,reps,python,octave,matlab)
                    code,rss,wall=lanzar(cmd,env,archivo)
                    muestras=[]
                    for linea in archivo.read_text().splitlines():
                        if linea.startswith('{"repeticion"'):
                            muestras.append(json.loads(linea))
                    correcto=code==0 and len(muestras)==reps
                    r={'lenguaje':lenguaje,'algoritmo':a,'metodo':m,'N':n,
                       'estado':'correcto' if correcto else f'error_exit_{code}',
                       'rss_pico_bytes':rss,'tiempo_proceso_s':wall,'muestras':muestras}
                    with journal.open('a') as f: f.write(json.dumps(r)+'\n')
                    registros[key]=r
                    exportar(list(registros.values()))
                    print(f'  {r["estado"]}; RSS={rss/2**20:.2f} MiB; proceso={wall:.2f} s',flush=True)
                    if not correcto:
                        print(archivo.read_text()[-2000:],flush=True)
                        raise SystemExit(f'Falló el caso; consulta {archivo}. Se puede reanudar.')
    subprocess.run([python,str(RAIZ/'diagnostico_recursion.py')],cwd=RAIZ,env=env,check=True)
    subprocess.run([python,str(RAIZ/'graficar_reporte.py')],cwd=RAIZ,env=env,check=True)
    print('TERMINADO: resultados, gráficas y README.md.',flush=True)


if __name__=='__main__':
    main()
