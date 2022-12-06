from model.Schedule import Schedule
import numpy as np
import matplotlib.pyplot as plt
import random
import sys
from time import time


# NSGA II - seleccion por elitismo 
class NsgaII:
        #Inicia el algoritmo decimos que el numero de cromosomas es 2
    def initAlgorithm(self, prototype, numberOfChromosomes=50):
        # Prototipo de cromosomas en la población.
        self._prototype = prototype

        # debe haber al menos 2 cromosomas en la población
        if numberOfChromosomes < 2:
            numberOfChromosomes = 2

        # Población de cromosomas
        self._chromosomes = []
        self._populationSize = numberOfChromosomes
        self._repeatRatio = .0

    # Inicializa el algoritmo genético
    def __init__(self, datos, numberOfCrossoverPoints=1, mutationSize=2, crossoverProbability=75,
                 mutationProbability=25):
        self.initAlgorithm(Schedule(datos))
        self._mutationSize = mutationSize
        self._numberOfCrossoverPoints = numberOfCrossoverPoints
        self._crossoverProbability = crossoverProbability
        self._mutationProbability = mutationProbability

    @property
    # Devuelve el puntero a los mejores cromosomas de la población.
    def result(self):
        return self._chromosomes[0]

    # función de clasificación no dominada
    def nonDominatedSorting(self, totalChromosome):
        doublePopulationSize = self._populationSize * 2
        s = doublePopulationSize * [ set() ]
        n = np.zeros(doublePopulationSize, dtype=int)
        front = [ set() ]

        for p in range(doublePopulationSize):
            for q in range(doublePopulationSize):
                if totalChromosome[p].fitness > totalChromosome[q].fitness:
                    s[p].add(q)
                elif totalChromosome[p].fitness < totalChromosome[q].fitness:
                    n[p] += 1

            if n[p] == 0:
                front[0].add(p)
    
        i = 0
        while front[i]:
            Q = set()
            for p in front[i]:
                for q in s[p]:
                    n[q] -= 1
                    if n[q] == 0:
                        Q.add(q)
            i += 1
            front.append(Q)

        front.pop()
        return front

    # calcular la función de distancia de hacinamiento
    def calculateCrowdingDistance(self, front, totalChromosome):
        distance, obj = {}, {}
        for key in front:
            distance[key] = 0
            fitness = totalChromosome[key].fitness
            if fitness not in obj.values():
                obj[key] = fitness

        sorted_keys = sorted(obj, key=obj.get)
        size = len(obj)
        distance[sorted_keys[0]] = distance[sorted_keys[-1]] = sys.float_info.max
        
        if size > 1:
            diff2 = totalChromosome[sorted_keys[-1]].getDifference(totalChromosome[sorted_keys[0]])
                
            for i in range(1, size - 1):
                diff = totalChromosome[sorted_keys[i + 1]].getDifference(totalChromosome[sorted_keys[i - 1]]) / diff2
                distance[sorted_keys[i]] += diff

        return distance

    def selection(self, front, totalChromosome):
        populationSize = self._populationSize
        calculateCrowdingDistance = self.calculateCrowdingDistance
        N = 0
        newPop = []
        while N < populationSize:
            for row in front:
                N += len(row)
                if N > populationSize:
                    distance = calculateCrowdingDistance(row, totalChromosome)
                    sortedCdf = sorted(distance, key=distance.get, reverse=True)
                    for j in sortedCdf:
                        if len(newPop) >= populationSize:
                            break
                        newPop.append(j)
                    break
                newPop.extend(row)
    
        return [totalChromosome[n] for n in newPop]

    def replacement(self, population):
        populationSize = self._populationSize
        numberOfCrossoverPoints = self._numberOfCrossoverPoints
        crossoverProbability = self._crossoverProbability
        offspring = []
        # generar una secuencia aleatoria para seleccionar el cromosoma padre para el cruce
        S = np.arange(populationSize)
        np.random.shuffle(S)

        halfPopulationSize = populationSize // 2
        for m in range(halfPopulationSize):
            parent0 = population[S[2 * m]]
            parent1 = population[S[2 * m + 1]]
            child0 = parent0.crossover(parent1, numberOfCrossoverPoints, crossoverProbability)
            child1 = parent1.crossover(parent0, numberOfCrossoverPoints, crossoverProbability)

            # agregar el cromosoma hijo a la lista de descendientes
            offspring.extend((child0, child1))
            
        return offspring
                
    # inicializar una nueva población con cromosomas construidos aleatoriamente usando un prototipo
    def initialize(self, population):
        prototype = self._prototype

        for i in range(len(population)):
            # agregar un nuevo cromosoma a la población
            population[i] = prototype.makeNewFromPrototype()

    def reform(self):
        random.seed(round(time() * 1000))
        np.random.seed(int(time()))
        if self._crossoverProbability < 95:
            self._crossoverProbability += 1.0
        elif self._mutationProbability < 30:
            self._mutationProbability += 1.0

    # Inicia y ejecuta el algoritmo.
    def run(self, maxRepeat=100, minFitness=0.9):
        x = []
        y = []
        mutationSize = self._mutationSize
        mutationProbability = self._mutationProbability
        nonDominatedSorting = self.nonDominatedSorting
        selection = self.selection
        populationSize = self._populationSize
        population = populationSize * [None]

        self.initialize(population)
        random.seed(round(time() * 1000))
        np.random.seed(int(time()))

        # La generación actual
        currentGeneration = 0

        repeat = 0
        lastBestFit = 0.0

        while 1:
            if currentGeneration > 0:
                best = self.result
                
                print("Funcion de aptitud:", "{:f}\t".format(best.fitness), "Generacion:", currentGeneration, end="\r")

                if len(y)==0:
                    y.append("{:f}\t".format(best.fitness))
                    x.append(currentGeneration)
                else:
                    if "{:f}\t".format(best.fitness) != y[len(y)-1]:
                        y.append("{:f}\t".format(best.fitness))
                        x.append(currentGeneration)
                        
                # algoritmo ha alcanzado los criterios?
                if best.fitness > minFitness:
                    break

                difference = abs(best.fitness - lastBestFit)
                if difference <= 0.001:
                    repeat += 1
                else:
                    repeat = 0

                self._repeatRatio = repeat * 100 / maxRepeat
                if repeat > (maxRepeat / 100):
                    self.reform()

            # Transversal
            offspring = self.replacement(population)

            # mutación
            for child in offspring:
                child.mutation(mutationSize, mutationProbability)

            totalChromosome = population + offspring

            # clasificación no dominada
            front = nonDominatedSorting(totalChromosome)
            if len(front) == 0:
                break

            # selección
            population = selection(front, totalChromosome)
            self._populationSize = populationSize = len(population)

            # comparación
            if currentGeneration == 0:
                self._chromosomes = population
            else:
                totalChromosome = population + self._chromosomes
                newBestFront = nonDominatedSorting(totalChromosome)
                if len(newBestFront) == 0:
                    break
                self._chromosomes = selection(newBestFront, totalChromosome)
                lastBestFit = best.fitness

            currentGeneration += 1
        #print("TERMINATOR!!!!!!!!!!!!!!!!!!!!!!!")
        plt.plot(x,y,'ro')
        plt.show()
        #for v1,v2 in zip(x,y):
            #print("X",v1, "Y",v2)
            
            
    def __str__(self):
        return "NSGA II"
