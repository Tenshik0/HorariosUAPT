from .Constantes import Constantes
from .CourseClass import CourseClass
from .Reservation import Reservation
from .Criteria import Criteria
from collections import deque
from random import randrange

import numpy as np

# Programar cromosoma
class Schedule:
   # Inicializa los cromosomas con el bloque de configuración (configuración del cromosoma)
    def __init__(self, datos):
        self._datos = datos
        # Valor de aptitud del cromosoma       
        self._fitness = 0

        # Ranuras de espacio-tiempo, una entrada representa una hora en un salón de clases
        slots_length = Constantes.DIAS_EN_LA_SEMANA * Constantes.HORAS_AL_DIA * self._datos.numberOfRooms
        self._slots = [[] for _ in range(slots_length)]

        # Tabla de clase para cromosoma
        # Se usa para determinar el primer intervalo de espacio-tiempo utilizado por la clase
        self._classes = {}

        # Indicadores de satisfacción de requisitos de clase
        self._criteria = np.zeros(self._datos.numberOfCourseClasses * Constantes.NUMERO_DE_CRITERIOS, dtype=bool)
        
        self._diversity = 0.0
        self._rank = 0

    def copy(self, c, setup_only):
        if not setup_only:
            self._datos = c.datos
            # copiar codigo
            self._slots, self._classes = [row[:] for row in c.slots], {key: value for key, value in c.classes.items()}

            # copiar banderas de requisitos de clase
            self._criteria = c.criteria[:]

            # copiar fitness
            self._fitness = c.fitness
            return self

        return Schedule(c.datos)

    # Crea un nuevo cromosoma con la misma configuración pero con un código elegido al azar
    def makeNewFromPrototype(self, positions = None):
        # crear un nuevo cromosoma, copiar la configuración del cromosoma
        new_chromosome = self.copy(self, True)
        new_chromosome_slots, new_chromosome_classes = new_chromosome._slots, new_chromosome._classes

        # colocar clases en posiciones aleatorias
        classes = self._datos.courseClasses
        nr = self._datos.numberOfRooms
        DIAS_EN_LA_SEMANA, HORAS_AL_DIA = Constantes.DIAS_EN_LA_SEMANA, Constantes.HORAS_AL_DIA
        for c in classes:
            # determinar la posición aleatoria de la clase
            dur = c.Duration

            day = randrange(DIAS_EN_LA_SEMANA)
            room = randrange(nr)
            time = randrange(HORAS_AL_DIA - dur)
            reservation = Reservation.getReservation(nr, day, time, room)

            if positions is not None:
                positions.append(day)
                positions.append(room)
                positions.append(time)
            reservation_index = hash(reservation)

            # llenar espacios de tiempo-espacio, por cada hora de clase
            for i in range(dur - 1, -1, -1):
                new_chromosome_slots[reservation_index + i].append(c)

            # insertar en la tabla de clase del cromosoma
            new_chromosome_classes[c] = reservation_index

        new_chromosome.calculateFitness()
        return new_chromosome

    # Realiza la operación de cruce utilizando dos cromosomas y devuelve el puntero a la descendencia
    def crossover(self, parent, numberOfCrossoverPoints, crossoverProbability):
        # comprobar la probabilidad de operación de cruce
        if randrange(100) > crossoverProbability:
            # Sin cruce, solo copia la primera padre
            return self.copy(self, False)

        # nuevo objeto de cromosoma, copiar configuración de cromosoma
        n = self.copy(self, True)
        n_classes, n_slots = n._classes, n._slots

        classes = self._classes
        course_classes = tuple(classes.keys())
        parent_classes = parent.classes
        parent_course_classes = tuple(parent.classes.keys())

        # número de clases
        size = len(classes)

        cp = size * [False]

        # determinar el punto de cruce (al azar)
        for i in range(numberOfCrossoverPoints, 0, -1):
            check_point = False
            while not check_point:
                p = randrange(size)
                if not cp[p]:
                    cp[p] = check_point = True

        # crear un nuevo código combinando códigos principales
        first = randrange(2) == 0
        
        for i in range(size):
            if first:
                course_class = course_classes[i]
                dur = course_class.Duration
                reservation_index = classes[course_class]
                # inserte la clase del primer padre en la tabla de clases del nuevo cromosoma
                n_classes[course_class] = reservation_index
                # todos los intervalos de tiempo-espacio de la clase se copian
                for j in range(dur - 1, -1, -1):
                    n_slots[reservation_index + j].append(course_class)
            else:
                course_class = parent_course_classes[i]
                dur = course_class.Duration
                reservation_index = parent_classes[course_class]
                # inserte la clase del segundo padre en la tabla de clases del nuevo cromosoma
                n_classes[course_class] = reservation_index
                # todos los intervalos de tiempo-espacio de la clase se copian
                for j in range(dur - 1, -1, -1):
                    n_slots[reservation_index + j].append(course_class)

            # punto de cruce
            if cp[i]:
                # cambiar el cromosoma de origen
                first = not first

        n.calculateFitness()

        # devolver el puntero inteligente a la descendencia
        return n
        
    # Realiza la operación de cruce utilizando dos cromosomas y devuelve el puntero a la descendencia
    def crossovers(self, parent, r1, r2, r3, etaCross, crossoverProbability):
        # número de clases
        size = len(self._classes)
        jrand = randrange(size)
        
        nr = self._datos.numberOfRooms
        HORAS_AL_DIA, DIAS_EN_LA_SEMANA = Constantes.HORAS_AL_DIA, Constantes.DIAS_EN_LA_SEMANA

        # crear un nuevo cromosoma, copiar la configuración del cromosoma
        new_chromosome = self.copy(self, True)
        new_chromosome_slots, new_chromosome_classes = new_chromosome._slots, new_chromosome._classes
        classes = self._classes
        course_classes = tuple(classes.keys())
        parent_classes = parent.classes
        parent_course_classes = tuple(parent.classes.keys())
        for i in range(size):
            if randrange(100) > crossoverProbability or i == jrand:
                course_class = course_classes[i]
                reservation1, reservation2 = Reservation.parse(r1.classes[course_class]), Reservation.parse(r2.classes[course_class])
                reservation3 = Reservation.parse(r3.classes[course_class])
                
                dur = course_class.Duration
                day = int(reservation3.Day + etaCross * (reservation1.Day - reservation2.Day))
                if day < 0:
                    day = 0
                elif day >= DIAS_EN_LA_SEMANA:
                    day = DIAS_EN_LA_SEMANA - 1

                room = int(reservation3.Room + etaCross * (reservation1.Room - reservation2.Room))
                if room < 0:
                    room = 0
                elif room >= nr:
                    room = nr - 1

                time = int(reservation3.Time + etaCross * (reservation1.Time - reservation2.Time))
                if time < 0:
                    time = 0
                elif time >= (HORAS_AL_DIA - dur):
                    time = HORAS_AL_DIA - 1 - dur

                reservation = Reservation.getReservation(nr, day, time, room)
                reservation_index = hash(reservation)

                # llenar espacios de tiempo-espacio, por cada hora de clase
                for j in range(dur - 1, -1, -1):
                    new_chromosome_slots[reservation_index + j].append(course_class)

                # insertar en la tabla de clase del cromosoma
                new_chromosome_classes[course_class] = reservation_index
            else:
                course_class = parent_course_classes[i]
                dur = course_class.Duration
                reservation = parent_classes[course_class]
                reservation_index = hash(reservation)
                
                # todos los intervalos de tiempo-espacio de la clase se copian
                for j in range(dur - 1, -1, -1):
                    new_chromosome_slots[reservation_index + j].append(course_class)
                
                # inserte la clase del segundo padre en la tabla de clases del nuevo cromosoma
                new_chromosome_classes[course_class] = reservation_index

        new_chromosome.calculateFitness()

        # devolver el puntero inteligente a la descendencia
        return new_chromosome

    def repair(self, cc1: CourseClass, reservation1_index: int, reservation2: Reservation):
        nr = self._datos.numberOfRooms
        HORAS_AL_DIA, DIAS_EN_LA_SEMANA = Constantes.HORAS_AL_DIA, Constantes.DIAS_EN_LA_SEMANA
        slots = self._slots
        dur = cc1.Duration

        for j in range(dur):
            # eliminar la hora de clase del espacio de tiempo actual
            cl = slots[reservation1_index + j]
            while cc1 in cl:
                cl.remove(cc1)

        # determinar la posición de la clase al azar
        if reservation2 is None:
            day = randrange(DIAS_EN_LA_SEMANA)
            room = randrange(nr)
            time = randrange(HORAS_AL_DIA - dur)
            reservation2 = Reservation.getReservation(nr, day, time, room)

        reservation2_index = hash(reservation2)
        for j in range(dur):
            # mover la hora de clase a un nuevo espacio de tiempo
            slots[reservation2_index + j].append(cc1)

        # cambiar la entrada de la tabla de clase para que apunte a nuevos espacios de tiempo y espacio
        self._classes[cc1] = reservation2_index

    # Realiza mutación en el cromosoma.
    def mutation(self, mutationSize, mutationProbability):
        # verificar la probabilidad de operación de mutación
        if randrange(100) > mutationProbability:
            return

        classes = self._classes
        # número de clases
        numberOfClasses = len(classes)
        course_classes = tuple(classes.keys())
        datos = self._datos
        nr = datos.numberOfRooms

        # mover el número seleccionado de clases en una posición aleatoria
        for i in range(mutationSize, 0, -1):
            # seleccionar cromosoma al azar para el movimiento
            mpos = randrange(numberOfClasses)

            # intervalo de tiempo-espacio actual utilizado por la clase
            cc1 = course_classes[mpos]
            reservation1_index = classes[cc1]

            self.repair(cc1, reservation1_index, None)

        self.calculateFitness()

    # Calcula el valor de aptitud del cromosoma
    def calculateFitness(self):
        # puntuación del cromosoma
        score = 0

        criteria, datos = self._criteria, self._datos
        items, slots = self._classes.items(), self._slots
        numberOfRooms = datos.numberOfRooms
        HORAS_AL_DIA, DIAS_EN_LA_SEMANA = Constantes.HORAS_AL_DIA, Constantes.DIAS_EN_LA_SEMANA
        daySize = HORAS_AL_DIA * numberOfRooms

        ci = 0
        getRoomById = datos.getRoomById

        # verifique los criterios y calcule los puntajes para cada clase en el horario
        for cc, reservation_index in items:
            reservation = Reservation.parse(reservation_index)

            # coordenada de la ranura espacio-temporal
            day, time, room = reservation.Day, reservation.Time, reservation.Room

            dur = cc.Duration

            ro = Criteria.isRoomOverlapped(slots, reservation, dur)

            # en la superposición de la habitación
            score = 0 if ro else score + 1

            criteria[ci + 0] = not ro

            r = getRoomById(room)
            # ¿La habitación actual tiene suficientes asientos?
            criteria[ci + 1] = Criteria.isSeatEnough(r, cc)
            score = score + 1 if criteria[ci + 1] else score / 2

            # ¿La habitación actual tiene ordenadores si son necesarios?
            criteria[ci + 2] = Criteria.isComputerEnough(r, cc)
            score = score + 1 if criteria[ci + 2] else score / 2

            # verificar la superposición de clases para profesores y grupos de estudiantes
            timeId = day * daySize + time
            po, go = Criteria.isOverlappedProfStudentGrp(slots, cc, numberOfRooms, timeId)

            # ¿Las profesoras no tienen clases superpuestas?
            score = 0 if po else score + 1

            criteria[ci + 3] = not po

            # ¿Los grupos de estudiantes no tienen clases superpuestas?
            score = 0 if go else score + 1

            criteria[ci + 4] = not go
            ci += Constantes.NUMERO_DE_CRITERIOS

        # calcular el valor de fitness basado en la puntuación
        self._fitness = score / len(criteria)

    def getDifference(self, other):
        return (self._criteria ^ other.criteria).sum()


    def extractPositions(self, positions):
        i = 0
        items = self._classes.items()
        for cc, reservation_index in items:
            reservation = Reservation.parse(reservation_index)

            positions[i] = reservation.Day
            i += 1
            positions[i] = reservation.Room
            i += 1
            positions[i] = reservation.Time
            i += 1


    def updatePositions(self, positions):
        DIAS_EN_LA_SEMANA, HORAS_AL_DIA = Constantes.DIAS_EN_LA_SEMANA, Constantes.HORAS_AL_DIA
        nr = self._datos.numberOfRooms
        i = 0
        items = self._classes.items()
        for cc, reservation1_index in items:
            dur = cc.Duration
            day = abs(int(positions[i]) % DIAS_EN_LA_SEMANA)
            room = abs(int(positions[i + 1]) % nr)
            time = abs(int(positions[i + 2]) % (HORAS_AL_DIA - dur))

            reservation2 = Reservation.getReservation(nr, day, time, room)
            self.repair(cc, reservation1_index, reservation2)

            positions[i] = reservation2.Day
            i += 1
            positions[i] = reservation2.Room
            i += 1
            positions[i] = reservation2.Time
            i += 1

        self.calculateFitness()


    # Devuelve el valor de aptitud del cromosoma
    @property
    def fitness(self):
        return self._fitness

    @property
    def datos(self):
        return self._datos

    @property
    # Devuelve la referencia a la tabla de clases.
    def classes(self):
        return self._classes

    @property
    # Devuelve una matriz de banderas de satisfacción de requisitos de clase
    def criteria(self):
        return self._criteria

    @property
    # Devuelve la referencia a la matriz de ranuras de tiempo-espacio
    def slots(self):
        return self._slots
        
    @property
    def diversity(self):
        return self._diversity

    @diversity.setter
    def diversity(self, new_diversity):
        self._diversity = new_diversity
        
    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, new_rank):
        self._rank = new_rank
