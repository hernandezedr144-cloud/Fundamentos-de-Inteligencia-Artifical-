"""Capa de compatibilidad: usa DEAP real o un equivalente en Python puro."""
import random

try:
    from deap import base, creator, tools
    DEAP_REAL = True
except Exception:
    DEAP_REAL = False

    class _Fitness:
        weights = (-1.0,)

        def __init__(self, values=()):
            self.values = tuple(values)

        def setValues(self, *v):
            self.values = tuple(v)

        def getValues(self):
            return self.values

        def __lt__(self, otro):
            return self.values < otro.values

        def __le__(self, otro):
            return self.values <= otro.values

        def __repr__(self):
            return f"Fitness({self.values})"

    class _Creator:
        def create(self, nombre, clase_base, **atributos):
            fit_cls = atributos.pop("fitness", None)
            cls = type(nombre, (clase_base,), atributos)
            if fit_cls is not None:
                def __init__(self, *a, **k):
                    clase_base.__init__(self, *a, **k)
                    self.fitness = fit_cls()
                cls.__init__ = __init__
            setattr(self, nombre, cls)
            return cls

    class _Toolbox:
        def register(self, alias, func, *args, **kwargs):
            if args or kwargs:
                setattr(self, alias, lambda *a, **k: func(*(a + args), **{**kwargs, **k}))
            else:
                setattr(self, alias, func)

    class _Tools:
        @staticmethod
        def initIterate(container, func):
            return lambda: container(func())

        @staticmethod
        def selTournament(individuos, k, tournsize):
            elegidos = []
            for _ in range(k):
                muestra = random.sample(individuos, min(tournsize, len(individuos)))
                elegidos.append(min(muestra, key=lambda i: i.fitness.values))
            return elegidos

        @staticmethod
        def cxOrdered(ind1, ind2):
            tam = len(ind1)
            a, b = sorted(random.sample(range(tam), 2))

            def ox(p1, p2):
                hijo = [None] * tam
                hijo[a:b + 1] = p1[a:b + 1]
                resto = [g for g in p2 if g not in hijo]
                k = 0
                for i in range(tam):
                    if hijo[i] is None:
                        hijo[i] = resto[k]
                        k += 1
                return hijo

            h1, h2 = ox(ind1, ind2), ox(ind2, ind1)
            ind1[:] = h1
            ind2[:] = h2
            return ind1, ind2

        @staticmethod
        def mutShuffleIndexes(ind, indpb):
            for i in range(len(ind)):
                if random.random() < indpb:
                    j = random.randrange(len(ind))
                    ind[i], ind[j] = ind[j], ind[i]
            return (ind,)

    base = type("base", (), {"Fitness": _Fitness, "Toolbox": _Toolbox})
    creator = _Creator()
    tools = _Tools