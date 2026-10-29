"""
Actividad 2.3 - Busqueda local aplicada a un TSP de 12 ciudades.
Compara Hill Climbing con reinicios aleatorios contra Simulated Annealing.
Reporta funcion objetivo, vecindad, parametros, grafica de convergencia y comparacion.
"""
import math
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

random.seed(172)
AQUI = os.path.dirname(os.path.abspath(__file__))
N = 12
CIUDADES = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(N)]
D = [[math.dist(a, b) for b in CIUDADES] for a in CIUDADES]

ITERACIONES = 3000
REINICIOS = 10
T0 = 800.0
ALFA = 0.995
ITER_SA = 6000


def costo(ruta):
    return sum(D[ruta[i]][ruta[(i + 1) % N]] for i in range(N))


def vecino(ruta):
    """Vecindad 2-opt: invierte un segmento."""
    i, j = sorted(random.sample(range(N), 2))
    nueva = ruta[:i] + ruta[i:j + 1][::-1] + ruta[j + 1:]
    return nueva


def hill_climbing():
    mejor_global, mejor_costo = None, float("inf")
    historia = []
    for _ in range(REINICIOS):
        actual = random.sample(range(N), N)
        c = costo(actual)
        for _ in range(ITERACIONES):
            cand = vecino(actual)
            cc = costo(cand)
            if cc < c:
                actual, c = cand, cc
            else:
                break
            historia.append(min(mejor_costo, c))
        if c < mejor_costo:
            mejor_global, mejor_costo = actual, c
        historia.extend([mejor_costo] * 50)
    return mejor_global, mejor_costo, historia


def simulated_annealing():
    actual = random.sample(range(N), N)
    c = costo(actual)
    mejor, mejor_costo = actual[:], c
    historia = []
    T = T0
    for _ in range(ITER_SA):
        cand = vecino(actual)
        cc = costo(cand)
        delta = cc - c
        if delta < 0 or random.random() < math.exp(-delta / max(T, 1e-9)):
            actual, c = cand, cc
            if cc < mejor_costo:
                mejor, mejor_costo = cand[:], cc
        historia.append(mejor_costo)
        T *= ALFA
    return mejor, mejor_costo, historia


def graficar(hc, sa, ruta_hc, ruta_sa, costo_hc, costo_sa):
    fig, ejes = plt.subplots(1, 3, figsize=(17, 5))

    ejes[0].plot(hc, label="Hill Climbing", color="#c62828")
    ejes[0].plot(sa, label="Simulated Annealing", color="#1565c0")
    ejes[0].set_yscale("log")
    ejes[0].set_title("Convergencia (mejor costo acumulado)")
    ejes[0].set_xlabel("Iteracion")
    ejes[0].set_ylabel("Costo (escala log)")
    ejes[0].legend()

    for eje, ruta, c, titulo, color in (
        (ejes[1], ruta_hc, costo_hc, "Mejor ruta - Hill Climbing", "#c62828"),
        (ejes[2], ruta_sa, costo_sa, "Mejor ruta - Simulated Annealing", "#1565c0"),
    ):
        xs = [CIUDADES[i][0] for i in ruta] + [CIUDADES[ruta[0]][0]]
        ys = [CIUDADES[i][1] for i in ruta] + [CIUDADES[ruta[0]][1]]
        eje.plot(xs, ys, "-o", color=color, markersize=6)
        for k, (x, y) in enumerate(CIUDADES):
            eje.annotate(str(k), (x, y), fontsize=8)
        eje.set_title(f"{titulo}\nCosto = {c:.2f}")
        eje.set_aspect("equal")

    plt.tight_layout()
    plt.savefig(os.path.join(AQUI, "convergencia_y_rutas.png"), dpi=170)
    plt.close()


def main():
    print(f"Funcion objetivo: longitud total del recorrido TSP de {N} ciudades (minimizar)")
    print(f"Vecindad: 2-opt | HC: {REINICIOS} reinicios x {ITERACIONES} iter | "
          f"SA: T0={T0}, alfa={ALFA}, {ITER_SA} iter\n")

    t0 = time.perf_counter()
    ruta_hc, costo_hc, hist_hc = hill_climbing()
    t_hc = time.perf_counter() - t0

    t0 = time.perf_counter()
    ruta_sa, costo_sa, hist_sa = simulated_annealing()
    t_sa = time.perf_counter() - t0

    graficar(hist_hc, hist_sa, ruta_hc, ruta_sa, costo_hc, costo_sa)

    with open(os.path.join(AQUI, "resultados.csv"), "w", encoding="utf-8") as f:
        f.write("algoritmo,costo_final,tiempo_s,ruta\n")
        f.write(f"hill_climbing,{costo_hc:.4f},{t_hc:.4f},{' '.join(map(str, ruta_hc))}\n")
        f.write(f"simulated_annealing,{costo_sa:.4f},{t_sa:.4f},{' '.join(map(str, ruta_sa))}\n")

    print(f"HC  -> costo {costo_hc:.2f} en {t_hc:.3f} s")
    print(f"SA  -> costo {costo_sa:.2f} en {t_sa:.3f} s")
    print("Mejora de SA sobre HC: "
          f"{(costo_hc - costo_sa) / costo_hc * 100:.1f} %")
    print("Archivos generados en:", AQUI)


if __name__ == "__main__":
    main()