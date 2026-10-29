"""
Actividad 2.4 - Comparacion BFS vs DFS en un laberinto con ciclos generado con semilla.
Documenta representacion, complejidad, camino solucion, nodos expandidos y tiempo.
"""
import os
import random
import time
from collections import deque

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
FILAS, COLUMNAS = 15, 15
CICLOS = 45


def generar_laberinto(semilla=172):
    random.seed(semilla)
    m = [["#"] * COLUMNAS for _ in range(FILAS)]

    def excavar(f, c):
        m[f][c] = "."
        direcciones = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(direcciones)
        for df, dc in direcciones:
            nf, nc = f + df, c + dc
            if 0 < nf < FILAS - 1 and 0 < nc < COLUMNAS - 1 and m[nf][nc] == "#":
                m[f + df // 2][c + dc // 2] = "."
                excavar(nf, nc)

    excavar(1, 1)
    return m


def abrir_ciclos(m, cantidad, semilla=99):
    """Tira paredes internas para crear rutas alternativas."""
    random.seed(semilla)
    candidatos = []
    for f in range(1, FILAS - 1):
        for c in range(1, COLUMNAS - 1):
            if m[f][c] != "#":
                continue
            horizontal = m[f][c - 1] == "." and m[f][c + 1] == "."
            vertical = m[f - 1][c] == "." and m[f + 1][c] == "."
            if horizontal or vertical:
                candidatos.append((f, c))
    random.shuffle(candidatos)
    for f, c in candidatos[:cantidad]:
        m[f][c] = "."
    return m


def buscar(m, inicio, meta, es_bfs):
    frontera = deque([inicio]) if es_bfs else [inicio]
    padre = {inicio: None}
    expandidos = []
    while frontera:
        actual = frontera.popleft() if es_bfs else frontera.pop()
        if actual in expandidos:
            continue
        expandidos.append(actual)
        if actual == meta:
            camino, nodo = [], actual
            while nodo is not None:
                camino.append(nodo)
                nodo = padre[nodo]
            return camino[::-1], expandidos
        f, c = actual
        for df, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nf, nc = f + df, c + dc
            if 0 <= nf < FILAS and 0 <= nc < COLUMNAS and m[nf][nc] != "#":
                if (nf, nc) not in padre:
                    padre[(nf, nc)] = actual
                    frontera.append((nf, nc))
    return None, expandidos


def graficar(m, inicio, meta, resultados):
    fig, ejes = plt.subplots(1, 2, figsize=(14, 7))
    for eje, (nombre, camino, expandidos, _) in zip(ejes, resultados):
        eje.imshow([[1 if celda == "#" else 0 for celda in fila] for fila in m],
                   cmap="Greys", origin="upper")
        if expandidos:
            eje.scatter([c for _, c in expandidos], [f for f, _ in expandidos],
                        s=16, c="#90caf9", label="expandidos")
        if camino:
            eje.plot([c for _, c in camino], [f for f, _ in camino],
                     "-", color="#c62828", linewidth=2, label="camino")
        eje.scatter([inicio[1]], [inicio[0]], c="#2e7d32", s=70, marker="s")
        eje.scatter([meta[1]], [meta[0]], c="#6a1b9a", s=70, marker="*")
        eje.set_title(f"{nombre}: {len(expandidos)} expandidos, "
                      f"camino {len(camino) if camino else 0}")
        eje.legend(loc="upper right", fontsize=8)
        eje.set_xticks([]); eje.set_yticks([])
    plt.tight_layout()
    plt.savefig(os.path.join(AQUI, "comparacion_bfs_dfs.png"), dpi=170)
    plt.close()


def main():
    m = generar_laberinto()
    abrir_ciclos(m, CICLOS)
    inicio, meta = (1, 1), (FILAS - 2, COLUMNAS - 2)
    print(f"Representacion: matriz 15x15 con {CICLOS} ciclos abiertos; "
          "'#' muro, '.' libre. Costo uniforme = 1.\n")

    resultados = []
    for nombre, es_bfs in (("BFS", True), ("DFS", False)):
        t0 = time.perf_counter()
        camino, expandidos = buscar(m, inicio, meta, es_bfs)
        t = time.perf_counter() - t0
        resultados.append((nombre, camino, expandidos, t))
        print(f"{nombre}: nodos expandidos = {len(expandidos)}, "
              f"longitud del camino = {len(camino) if camino else 'sin solucion'}, "
              f"tiempo = {t * 1000:.2f} ms")

    graficar(m, inicio, meta, resultados)

    with open(os.path.join(AQUI, "comparacion.csv"), "w", encoding="utf-8") as f:
        f.write("algoritmo,nodos_expandidos,longitud_camino,tiempo_ms,optimo\n")
        for nombre, camino, expandidos, t in resultados:
            f.write(f"{nombre},{len(expandidos)},{len(camino) if camino else 0},"
                    f"{t * 1000:.3f},{'si' if nombre == 'BFS' else 'no garantizado'}\n")

    print("\nComplejidad temporal: O(b^d) ambos. Espacial: BFS O(b^d), DFS O(b*m).")
    print("BFS garantiza el camino mas corto con costo uniforme; DFS no.")
    print("Archivos generados en:", AQUI)


if __name__ == "__main__":
    main()