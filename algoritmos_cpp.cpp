// C++17, biblioteca estándar. Recorridos recursivos híbridos: caso base <=256.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#define NOINLINE __attribute__((noinline))
constexpr std::int64_t BLOQUE = 256;
using I = std::int64_t;
struct Resultado { double valor=0; std::vector<double> salida; I usados=0; };

NOINLINE double suma_lineal(I n) { return n==0 ? 0 : n+suma_lineal(n-1); }
NOINLINE double suma_cola(I n, double acumulador=0) { return n==0 ? acumulador : suma_cola(n-1,acumulador+n); }
NOINLINE double contar_lineal(I n) { return n==0 ? 0 : 1+contar_lineal(n-1); }

NOINLINE I busqueda_iterativa(const std::vector<double>& datos, double objetivo) {
    I lo=0, hi=static_cast<I>(datos.size())-1;
    while(lo<=hi) {
        I medio=(lo+hi)/2;
        if(datos[medio]==objetivo) return medio;
        if(objetivo<datos[medio]) hi=medio-1; else lo=medio+1;
    }
    return -1;
}
NOINLINE I busqueda_recursiva(const std::vector<double>& datos, double objetivo, I lo, I hi) {
    if(lo>hi) return -1;
    I medio=(lo+hi)/2;
    if(datos[medio]==objetivo) return medio;
    if(objetivo<datos[medio]) return busqueda_recursiva(datos,objetivo,lo,medio-1);
    return busqueda_recursiva(datos,objetivo,medio+1,hi);
}

void hoja(const std::string& a,I lo,I hi,const std::vector<double>& datos,Resultado& r) {
    if(a=="filtrado") {
        for(I i=lo;i<hi;++i) if(datos[i]>5) r.salida[r.usados++]=datos[i];
    } else if(a=="cuadrados") {
        for(I i=lo;i<hi;++i) r.salida[i]=static_cast<double>(i)*static_cast<double>(i);
    } else if(a=="suma") {
        for(I i=lo;i<hi;++i) r.valor+=i+1;
    } else {
        for(I i=lo;i<hi;++i) r.valor+=1;
    }
}
void dividir(const std::string& a,I lo,I hi,const std::vector<double>& datos,Resultado& r) {
    if(hi-lo<=BLOQUE) { hoja(a,lo,hi,datos,r); return; }
    I medio=(lo+hi)/2;
    dividir(a,lo,medio,datos,r);
    dividir(a,medio,hi,datos,r);
}
NOINLINE Resultado ejecutar(const std::string& a,const std::string& m,I n,const std::vector<double>& datos) {
    Resultado r;
    if(a=="busqueda") {
        r.valor = m=="iterativo" ? busqueda_iterativa(datos,n-1) : busqueda_recursiva(datos,n-1,0,n-1);
        return r;
    }
    if(a=="filtrado" || a=="cuadrados") r.salida.resize(n);
    if(m=="iterativo") hoja(a,0,n,datos,r); else dividir(a,0,n,datos,r);
    if(a=="filtrado") r.valor=r.usados;
    if(a=="cuadrados") { r.usados=n; r.valor=n==0 ? 0 : r.salida.back(); }
    return r;
}
std::vector<double> crear_datos(const std::string& a,I n) {
    std::vector<double> datos;
    if(a=="filtrado" || a=="busqueda") {
        datos.resize(n);
        for(I i=0;i<n;++i) datos[i]=a=="filtrado" ? i%8+2 : i;
    }
    return datos;
}
void exigir(bool ok) { if(!ok) throw std::runtime_error("Validación fallida"); }
void validar(const std::string& a,I n,const Resultado& r) {
    if(a=="filtrado") {
        I cantidad=n/8*4+std::max<I>(0,n%8-4);
        exigir(r.usados==cantidad && r.valor==cantidad);
        for(I i=0;i<cantidad;++i) exigir(r.salida[i]==i%4+6);
    } else if(a=="cuadrados") {
        exigir(r.usados==n);
        for(I i=0;i<n;++i) exigir(r.salida[i]==static_cast<double>(i)*i);
    } else if(a=="suma") exigir(r.valor==static_cast<double>(n)*(n+1)/2);
    else if(a=="conteo") exigir(r.valor==n);
    else exigir(r.valor==n-1);
}
void pruebas() {
    for(auto a:{"filtrado","conteo","suma","busqueda","cuadrados"})
        for(I n:{0,1,8,10,257}) {
            auto datos=crear_datos(a,n);
            for(auto m:{"iterativo","recursivo"}) validar(a,n,ejecutar(a,m,n,datos));
        }
    std::vector<double> d{10,20,30};
    for(auto par:std::vector<std::pair<double,I>>{{10,0},{20,1},{30,2},{25,-1},{40,-1},{0,-1}}) {
        exigir(busqueda_iterativa(d,par.first)==par.second);
        exigir(busqueda_recursiva(d,par.first,0,2)==par.second);
    }
    exigir(suma_lineal(10)==55 && suma_cola(10)==55 && contar_lineal(10)==10);
    std::cout<<"PRUEBAS C++: correctas\n";
}
int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--test") { pruebas(); return 0; }
        if(argc!=5) throw std::runtime_error("Uso: algoritmos_cpp algoritmo metodo N repeticiones");
        std::string a=argv[1],m=argv[2]; I n=std::stoll(argv[3]); int rep=std::stoi(argv[4]);
        exigir(n>=0 && rep>0 && (m=="iterativo" || m=="recursivo"));
        exigir(a=="filtrado" || a=="conteo" || a=="suma" || a=="busqueda" || a=="cuadrados");
        auto datos=crear_datos(a,n);
        I pequeno=std::min<I>(10,n);
        validar(a,pequeno,ejecutar(a,m,pequeno,crear_datos(a,pequeno)));
        const int lote=a=="busqueda" ? 1000 : 1;
        volatile double testigo=0;
        std::cout<<std::setprecision(17);
        for(int k=0;k<rep;++k) {
            Resultado r;
            auto inicio=std::chrono::steady_clock::now();
            for(int j=0;j<lote;++j) { r=ejecutar(a,m,n,datos); testigo=r.valor; }
            double t=std::chrono::duration<double>(std::chrono::steady_clock::now()-inicio).count()/lote;
            validar(a,n,r);
            std::cout<<"{\"repeticion\":"<<k+1<<",\"segundos\":"<<t<<",\"valor\":"<<r.valor
                     <<",\"elementos_salida\":"<<r.usados<<",\"lote\":"<<lote<<"}\n";
        }
        (void)testigo;
    } catch(const std::exception& e) { std::cerr<<e.what()<<'\n'; return 1; }
}
