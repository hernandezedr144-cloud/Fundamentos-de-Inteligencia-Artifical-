"""
Actividad 2.6 - Algoritmo genetico (DEAP) para TSP de 10 paradas.
Poblacion, cromosoma (permutacion), fitness (distancia), seleccion por torneo,
cruce OX, mutacion por intercambio, 40 generaciones y grafica de convergencia.
"""
import math
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from deap_compat import base, creator, tools, DEAP_REAL

AQUI = os.path.dirname(os.path.abspath(__file__))
random.seed(172)

N = 10
PUNTOS = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(N)]
D = [[math.dist(a, b) for b in PUNTOS] for a in PUNTOS]

TAM_POB = 60
GENERACIONES = 40
P_CRUCE = 0.85
P_MUTACION = 0.30
TORNEO = 3


def aptitud(ind):
    return (sum(D[ind[i]][ind[(i + 1) % N]] for i in range(N)),)


def main():
    print(f"Motor: {'DEAP real' if DEAP_REAL else 'compatibilidad en Python puro'}")
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individuo", list, fitness=creator.FitnessMin)

    caja = base.Toolbox()
    caja.register("permutacion", random.sample, range(N), N)
    caja.register("individuo", tools.initIterate, creator.Individuo, caja.permutacion)

    poblacion = [caja.individuo() for _ in range(TAM_POB)]
    for ind in poblacion:
        ind.fitness.values = aptitud(ind)

    historial = []
    for gen in range(GENERACIONES):
        elite = min(poblacion, key=lambda i: i.fitness.values)
        hijos = [creator.Individuo(h) for h in
                 tools.selTournament(poblacion, TAM_POB, TORNEO)]

        for i in range(0, len(hijos) - 1, 2):
            if random.random() < P_CRUCE:
                tools.cxOrdered(hijos[i], hijos[i + 1])
        for h in hijos:
            if random.random() < P_MUTACION:
                tools.mutShuffleIndexes(h, 0.15)
        for h in hijos:
            h.fitness.values = aptitud(h)

        poblacion = sorted(hijos + [elite], key=lambda i: i.fitness.values)[:TAM_POB]
        mejor = poblacion[0]
        historial.append(mejor.fitness.values[0])
        print(f"Gen {gen + 1:02d} | mejor = {mejor.fitness.values[0]:.2f} | "
              f"promedio = {sum(i.fitness.values[0] for i in poblacion) / TAM_POB:.2f}")

    mejor = poblacion[0]
    fig, ejes = plt.subplots(1, 2, figsize=(14, 5))
    ejes[0].plot(range(1, GENERACIONES + 1), historial, color="#1565c0")
    ejes[0].set_title("Convergencia del fitness (menor es mejor)")
    ejes[0].set_xlabel("Generacion")
    ejes[0].set_ylabel("Distancia total")
    ejes[0].grid(alpha=0.3)

    xs = [PUNTOS[i][0] for i in mejor] + [PUNTOS[mejor[0]][0]]
    ys = [PUNTOS[i][1] for i in mejor] + [PUNTOS[mejor[0]][1]]
    ejes[1].plot(xs, ys, "-o", color="#2e7d32")
    for k, (x, y) in enumerate(PUNTOS):
        ejes[1].annotate(str(k), (x, y), fontsize=8)
    ejes[1].set_title(f"Mejor ruta (costo {mejor.fitness.values[0]:.2f})")
    ejes[1].set_aspect("equal")

    plt.tight_layout()
    plt.savefig(os.path.join(AQUI, "convergencia_ga.png"), dpi=170)
    plt.close()

    with open(os.path.join(AQUI, "mejor_individuo.txt"), "w", encoding="utf-8") as f:
        f.write(f"Motor: {'DEAP real' if DEAP_REAL else 'compatibilidad'}\n")
        f.write(f"Cromosoma: {' '.join(map(str, mejor))}\n")
        f.write(f"Fitness: {mejor.fitness.values[0]:.4f}\n")
        f.write("Fitness de la generacion 1: %.4f\n" % historial[0])
        f.write("Fitness de la generacion final: %.4f\n" % historial[-1])

    print(f"\nMejor costo: {mejor.fitness.values[0]:.2f}")
    print(f"Reproduccion (gen 1 -> gen {GENERACIONES}): "
          f"{historial[0]:.2f} -> {historial[-1]:.2f}")


if __name__ == "__main__":
    main()