function algoritmos_matlab(algoritmo, metodo, n, repeticiones)
% Compatible con MATLAB y GNU Octave. Intervalos internos: índices 0..N-1.
% Recorridos recursivos híbridos, caso base de hasta 256 elementos.
if nargin == 1 && strcmp(algoritmo, 'test')
    nombres = {'filtrado','conteo','suma','busqueda','cuadrados'};
    metodos = {'iterativo','recursivo'};
    for a = 1:numel(nombres)
        for cantidad = [0 1 8 10 257]
            d = crear_datos(nombres{a}, cantidad);
            for m = 1:2
                [v,s,k] = ejecutar(nombres{a},metodos{m},cantidad,d);
                validar(nombres{a},cantidad,v,s,k);
            end
        end
    end
    d = [10 20 30]; objetivos = [10 20 30 25 40 0]; esperados = [0 1 2 -1 -1 -1];
    for j=1:numel(objetivos)
        assert(busqueda_iterativa(d,objetivos(j))==esperados(j));
        assert(busqueda_recursiva(d,objetivos(j),0,2)==esperados(j));
    end
    assert(suma_lineal(10)==55 && suma_cola(10,0)==55 && contar_lineal(10)==10);
    fprintf('PRUEBAS MATLAB/Octave: correctas\n');
    return;
end
assert(n>=0 && n==fix(n) && repeticiones>=1);
datos = crear_datos(algoritmo,n);
pequeno = min(n,10);
[v,s,k] = ejecutar(algoritmo,metodo,pequeno,crear_datos(algoritmo,pequeno));
validar(algoritmo,pequeno,v,s,k);
clear v s k;
if strcmp(algoritmo,'busqueda'), lote=1000; else, lote=1; end
for repeticion=1:repeticiones
    inicio=tic;
    for j=1:lote
        [valor,salida,usados]=ejecutar(algoritmo,metodo,n,datos);
    end
    segundos=toc(inicio)/lote;
    validar(algoritmo,n,valor,salida,usados);
    fprintf('{"repeticion":%d,"segundos":%.17g,"valor":%.17g,"elementos_salida":%d,"lote":%d}\n', ...
            repeticion,segundos,valor,usados,lote);
    clear salida valor usados;
end
end

function datos=crear_datos(a,n)
if strcmp(a,'busqueda')
    % Materializar: Octave puede representar 0:n-1 como un rango compacto.
    datos=zeros(1,n);
    for lo=0:65536:n-1
        hi=min(n,lo+65536);
        datos(lo+1:hi)=lo:hi-1;
    end
elseif strcmp(a,'filtrado')
    datos=zeros(1,n);
    for j=0:7, datos(j+1:8:end)=j+2; end
else
    datos=zeros(1,0);
end
end

function [valor,salida,usados]=ejecutar(a,metodo,n,datos)
valor=0; usados=0; salida=zeros(1,0);
if strcmp(a,'busqueda')
    if strcmp(metodo,'iterativo'), valor=busqueda_iterativa(datos,n-1);
    else, valor=busqueda_recursiva(datos,n-1,0,n-1); end
    return;
end
if strcmp(a,'filtrado') || strcmp(a,'cuadrados'), salida=zeros(1,n); end
if strcmp(metodo,'iterativo'), hoja(0,n); else, dividir(0,n); end
if strcmp(a,'filtrado'), valor=usados; end
if strcmp(a,'cuadrados')
    usados=n;
    if n>0, valor=salida(end); end
end
    function dividir(lo,hi)
        if hi-lo<=256
            hoja(lo,hi);
            return;
        end
        medio=floor((lo+hi)/2);
        dividir(lo,medio);
        dividir(medio,hi);
    end
    function hoja(lo,hi)
        if strcmp(a,'filtrado')
            for i=lo:hi-1
                elemento=datos(i+1);
                if elemento>5
                    usados=usados+1;
                    salida(usados)=elemento;
                end
            end
        elseif strcmp(a,'cuadrados')
            for i=lo:hi-1, salida(i+1)=i*i; end
        elseif strcmp(a,'suma')
            for i=lo:hi-1, valor=valor+i+1; end
        else
            for i=lo:hi-1, valor=valor+1; end
        end
    end
end

function indice=busqueda_iterativa(datos,objetivo)
lo=0; hi=numel(datos)-1;
while lo<=hi
    medio=floor((lo+hi)/2);
    if datos(medio+1)==objetivo, indice=medio; return; end
    if objetivo<datos(medio+1), hi=medio-1; else, lo=medio+1; end
end
indice=-1;
end
function indice=busqueda_recursiva(datos,objetivo,lo,hi)
if lo>hi, indice=-1; return; end
medio=floor((lo+hi)/2);
if datos(medio+1)==objetivo, indice=medio; return; end
if objetivo<datos(medio+1), indice=busqueda_recursiva(datos,objetivo,lo,medio-1);
else, indice=busqueda_recursiva(datos,objetivo,medio+1,hi); end
end
function valor=suma_lineal(n)
if n==0, valor=0; else, valor=n+suma_lineal(n-1); end
end
function valor=suma_cola(n,acumulador)
if n==0, valor=acumulador; else, valor=suma_cola(n-1,acumulador+n); end
end
function valor=contar_lineal(n)
if n==0, valor=0; else, valor=1+contar_lineal(n-1); end
end
function validar(a,n,v,s,k)
if strcmp(a,'filtrado')
    cantidad=floor(n/8)*4+max(0,mod(n,8)-4);
    assert(v==cantidad && k==cantidad);
    for lo=0:65536:k-1
        hi=min(k,lo+65536);
        assert(isequal(s(lo+1:hi),mod(lo:hi-1,4)+6));
    end
elseif strcmp(a,'cuadrados')
    assert(k==n && numel(s)==n);
    for lo=0:65536:n-1
        hi=min(n,lo+65536);
        assert(isequal(s(lo+1:hi),(lo:hi-1).^2));
    end
elseif strcmp(a,'suma'), assert(v==n*(n+1)/2);
elseif strcmp(a,'conteo'), assert(v==n);
else, assert(v==n-1);
end
end
