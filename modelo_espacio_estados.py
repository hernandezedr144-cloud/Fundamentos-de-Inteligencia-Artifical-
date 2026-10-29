"""
Actividad 2.1 y 2.2 - Modelado de problemas reales como busqueda en espacios de estados.
Problema A: rompecabezas deslizante 3x3 (Puzzle8).
Problema B: jarros de agua de 4 y 3 litros, meta = 2 litros en el jarro A.

Cada problema se modela con la 5-tupla clasica:
  estado inicial, acciones, modelo de transicion (sucesores), prueba de objetivo, costo de ruta.
Se genera el grafo del espacio de estados con NetworkX y se reporta su analisis de complejidad.
"""
import os
import random
from collections import deque

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

random.seed(172)
AQUI = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------
# PROBLEMA A: Puzzle8
# --------------------------------------------------------------------------
class Puzzle8:
    """Estado = tupla de 9 enteros; 0 representa el hueco."""

    def __init__(self, inicio, meta=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        self.inicio = tuple(inicio)
        self.meta = tuple(meta)
        self._vecinos = {}
        for i in range(9):
            f, c = divmod(i, 3)
            ady = []
            for df, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nf, nc = f + df, c + dc
                if 0 <= nf < 3 and 0 <= nc < 3:
                    ady.append(nf * 3 + nc)
            self._vecinos[i] = ady

    def es_objetivo(self, estado):
        return estado == self.meta

    def sucesores(self, estado):
        hueco = estado.index(0)
        for destino in self._vecinos[hueco]:
            lista = list(estado)
            lista[hueco], lista[destino] = lista[destino], lista[hueco]
            accion = f"mover {estado[destino]} al hueco ({destino // 3},{destino % 3})"
            yield accion, 1, tuple(lista)

    def clave(self, estado):
        return estado

    def texto(self, estado):
        return "".join(str(x) for x in estado)


# --------------------------------------------------------------------------
# PROBLEMA B: Jarros de agua
# --------------------------------------------------------------------------
class Jarros:
    """Estado = (litros en jarro A, litros en jarro B). Capacidades (4, 3)."""

    def __init__(self, capacidades=(4, 3), meta=2):
        self.capacidades = capacidades
        self.meta = meta
        self.inicio = (0, 0)

    def es_objetivo(self, estado):
        return estado[0] == self.meta

    def sucesores(self, estado):
        a, b = estado
        ca, cb = self.capacidades
        if a < ca:
            yield "llenar A", 1, (ca, b)
        if b < cb:
            yield "llenar B", 1, (a, cb)
        if a > 0:
            yield "vaciar A", 1, (0, b)
        if b > 0:
            yield "vaciar B", 1, (a, 0)
        v = min(a, cb - b)
        if v > 0:
            yield "verter A->B", 1, (a - v, b + v)
        v = min(b, ca - a)
        if v > 0:
            yield "verter B->A", 1, (a + v, b - v)

    def clave(self, estado):
        return estado

    def texto(self, estado):
        return f"{estado[0]},{estado[1]}"


# --------------------------------------------------------------------------
# Generacion del grafo
# --------------------------------------------------------------------------
def construir_grafo(problema, profundidad_max, max_nodos=350):
    grafo = nx.DiGraph()
    capa = {problema.inicio: 0}
    grafo.add_node(problema.clave(problema.inicio), capa=0, rol="inicio")
    cola = deque([problema.inicio])
    suma_hijos, nodos_expandidos = 0, 0

    while cola:
        estado = cola.popleft()
        d = capa[estado]
        hijos = list(problema.sucesores(estado))
        if d < profundidad_max:
            suma_hijos += len(hijos)
            nodos_expandidos += 1
            for accion, costo, hijo in hijos:
                grafo.add_edge(problema.clave(estado), problema.clave(hijo),
                               accion=accion, costo=costo)
                if hijo not in capa:
                    capa[hijo] = d + 1
                    rol = "meta" if problema.es_objetivo(hijo) else "normal"
                    grafo.add_node(problema.clave(hijo), capa=d + 1, rol=rol)
                    cola.append(hijo)
                    if grafo.number_of_nodes() >= max_nodos:
                        cola.clear()
                        break

    factor = suma_hijos / nodos_expandidos if nodos_expandidos else 0.0
    return grafo, factor, capa


def dibujar(grafo, problema, titulo, archivo, por_capas):
    plt.figure(figsize=(13, 9) if not por_capas else (13, 15))
    if por_capas:
        pos = nx.multipartite_layout(grafo, subset_key="capa", align="vertical")
    else:
        pos = nx.spring_layout(grafo, seed=172, k=0.9)

    colores = []
    for nodo in grafo.nodes:
        rol = grafo.nodes[nodo].get("rol")
        if rol == "inicio":
            colores.append("#2e7d32")
        elif rol == "meta":
            colores.append("#c62828")
        else:
            colores.append("#5c6bc0")

    nx.draw_networkx_edges(grafo, pos, alpha=0.35, arrows=True,
                           arrowsize=8, width=0.7, node_size=90)
    nx.draw_networkx_nodes(grafo, pos, node_color=colores, node_size=110,
                           linewidths=0.4, edgecolors="black")
    etiquetas = {n: problema.texto(n) for n in grafo.nodes}
    nx.draw_networkx_labels(grafo, pos, etiquetas, font_size=5)
    plt.title(titulo)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(AQUI, archivo), dpi=170)
    plt.close()


def analizar(nombre, problema, grafo, factor, capa):
    metas = [n for n in grafo.nodes if problema.es_objetivo(n)]
    profundidad_meta = min((capa[m] for m in metas), default=None)
    lineas = [
        f"=== {nombre} ===",
        f"Estados distintos generados (|V|): {grafo.number_of_nodes()}",
        f"Transiciones (|E|): {grafo.number_of_edges()}",
        f"Factor de ramificacion promedio b: {factor:.2f}",
        f"Profundidad de la primera meta alcanzada d: {profundidad_meta}",
    ]
    if profundidad_meta:
        estimado = sum(factor ** i for i in range(profundidad_meta + 1))
        lineas.append(f"Estimacion de nodos b^d (orden de magnitud): {estimado:,.0f}")
    lineas += [
        "Complejidad temporal: O(b^d) para busqueda no informada.",
        "Complejidad espacial: O(b^d) si se guarda la frontera completa.",
        "Observacion: el espacio es finito y con estados repetidos, por lo que",
        "requiere deteccion de ciclos (conjunto de visitados) en cualquier algoritmo.",
        "",
    ]
    texto = "\n".join(lineas)
    print(texto)
    return texto


def main():
    # Puzzle: se desordena desde la meta con 6 movimientos legales.
    meta = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    puzzle = Puzzle8(meta)
    estado = meta
    for _ in range(6):
        estado = random.choice(list(puzzle.sucesores(estado)))[2]
    puzzle.inicio = estado
    print("Estado inicial del puzzle:", puzzle.texto(estado), "\n")

    jarros = Jarros()

    salida = []
    for nombre, problema, prof, archivo, capas in (
        ("Puzzle8", puzzle, 4, "grafo_puzzle8.png", False),
        ("Jarros", jarros, 7, "grafo_jarros.png", True),
    ):
        grafo, factor, capa = construir_grafo(problema, prof)
        dibujar(grafo, problema,
                f"Espacio de estados - {nombre} (profundidad <= {prof})",
                archivo, capas)
        salida.append(analizar(nombre, problema, grafo, factor, capa))

    ruta = os.path.join(AQUI, "analisis_complejidad.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(salida))
    print("Diagramas y analisis guardados en:", AQUI)


if __name__ == "__main__":
    main()