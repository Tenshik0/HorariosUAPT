from .NsgaII import NsgaII

import numpy as np

# Hybrid Genetic Algorithm and Sperm Swarm Optimization (HGASSO) mutacion y cruce
class Hgasso(NsgaII):
   # Inicializa el algoritmo genético híbrido y la optimización del enjambre de esperma
    def __init__(self, datos, numberOfCrossoverPoints=1, mutationSize=1, crossoverProbability=80,
                 mutationProbability=1):
        super().__init__(datos, numberOfCrossoverPoints, mutationSize, crossoverProbability,
                        mutationProbability)
        self._decline = .25
        self._sBestScore, self._sgBestScore = [], 0
        self._sBest, self._sgBest = [], []
        self._current_position, self._velocity = [], []
        self._motility = []

    def replacement(self, population):
        populationSize = len(population)
        climax, decline = 1 - self._decline, self._decline

        for i in range(populationSize):
            fitness = population[i].fitness
            if fitness < self._sBestScore[i]:
                population[i].updatePositions(self._current_position[i])
                fitness = population[i].fitness
                self._motility[i] = True

            if fitness > self._sBestScore[i]:
                self._sBestScore[i] = fitness
                population[i].extractPositions(self._current_position[i])
                self._sBest[i] = self._current_position[i][:]

            if fitness > self._sgBestScore:
                self._sgBestScore = fitness
                population[i].extractPositions(self._current_position[i])
                self._sgBest = self._current_position[i][:]

            if self._repeatRatio > self._sBestScore[i]:
                self._sBestScore[i] -= self._repeatRatio * decline
            if self._repeatRatio > climax and self._sgBestScore > climax:
                if i > (populationSize * self._sgBestScore):
                    population[i].updatePositions(self._current_position[i])
                    self._motility[i] = True

        self.updateVelocities(population)
        return super().replacement(population)

    def initialize(self, population):
        prototype = self._prototype
        size = 0
        populationSize = len(population)
        for i in range(populationSize):
            positions = []
            # agregar un nuevo cromosoma a la población
            population[i] = prototype.makeNewFromPrototype(positions)
            if i < 1:
                size = len(positions)
                self._current_position = np.zeros((populationSize, size), dtype=float)
                self._velocity = np.zeros((populationSize, size), dtype=float)

                self._sBest = np.zeros((populationSize, size), dtype=float)
                self._sgBest = np.zeros(populationSize, dtype=float)
                self._sBestScore = np.zeros(populationSize, dtype=float)
                self._motility = np.zeros(populationSize, dtype=bool)

            self._sBestScore[i] = population[i].fitness
            self._current_position[i] = positions
            self._velocity[i] = np.random.uniform(-.6464, .7157, size) / 3.0

    def updateVelocities(self, population):
        motility = self._motility
        if np.count_nonzero(motility) < 1:
            return

        populationSize = len(population)
        dim = self._velocity[motility].shape

        self._velocity[motility] = np.random.random(dim) * np.log10(np.random.uniform(7.0, 14.0, dim)) * self._velocity[motility] + \
        np.log10(np.random.uniform(7.0, 14.0, dim)) * np.log10(np.random.uniform(35.5, 38.5, dim)) * (self._sBest[motility] - self._current_position[motility]) + \
        np.log10(np.random.uniform(7.0, 14.0, dim)) * np.log10(np.random.uniform(35.5, 38.5, dim)) * (self._sgBest - self._current_position[motility])
        self._current_position[motility] += self._velocity[motility]

    def __str__(self):
        return ". Mutación aleatoria  ..."