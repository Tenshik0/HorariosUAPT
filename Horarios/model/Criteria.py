from .Constantes import Constantes


# Lee el archivo de configuración y almacena los objetos analizados
class Criteria:

    # verificar si hay superposición de clases en la habitación
    @staticmethod
    def isRoomOverlapped(slots, reservation, dur):
        reservation_index = hash(reservation)
        cls = slots[reservation_index: reservation_index + dur]
        return any(True for slot in cls if len(slot) > 1)

    # ¿La habitación actual tiene suficientes asientos?
    @staticmethod
    def isSeatEnough(r, cc):
        return r.NumberOfSeats >= cc.NumberOfSeats

    # ¿La habitación actual tiene computadoras si son necesarias?
    @staticmethod
    def isComputerEnough(r, cc):
        return (not cc.LabRequired) or (cc.LabRequired and r.Lab)

    # verificar la superposición de clases para profesores y grupos de estudiantes
    @staticmethod
    def isOverlappedProfStudentGrp(slots, cc, numberOfRooms, timeId):
        po = go = False

        dur = cc.Duration
        for i in range(numberOfRooms, 0, -1):
            # por cada hora de clase
            for j in range(timeId, timeId + dur):
                cl = slots[j]
                for cc1 in cl:
                    if cc != cc1:
                        # Profesora se superpone?
                        if not po and cc.profesorOverlaps(cc1):
                            po = True
                        # grupos de estudiantes se superponen?
                        if not go and cc.groupsOverlap(cc1):
                            go = True
                        # ambos tipos de superposición? no hay necesidad de comprobar más
                        if po and go:
                            return po, go

            timeId += Constantes.HORAS_AL_DIA
        return po, go
