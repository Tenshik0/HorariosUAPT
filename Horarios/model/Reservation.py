from .Constantes import Constantes


class Reservation:
    NR = -1
    _reservationPool = {}


    def __init__(self, day: int, time: int, room: int):
        self.Day = day
        self.Time = time
        self.Room = room

    @staticmethod
    def parse(hashCode):
        reservation = Reservation._reservationPool.get(hashCode)
        if reservation is None:
            day = hashCode // (Constantes.HORAS_AL_DIA * Reservation.NR)
            hashCode2 = hashCode - (day * Constantes.HORAS_AL_DIA * Reservation.NR)
            room = hashCode2 // Constantes.HORAS_AL_DIA
            time = hashCode2 % Constantes.HORAS_AL_DIA
            reservation = Reservation(day, time, room)
            Reservation._reservationPool[hashCode] = reservation
        return reservation

    @staticmethod
    def getHashCode(day: int, time: int, room: int) -> int:
            return day * Reservation.NR * Constantes.HORAS_AL_DIA + room * Constantes.HORAS_AL_DIA + time

    @staticmethod
    def getReservation(nr: int, day: int, time: int, room: int):
        if nr != Reservation.NR and nr > 0:
            Reservation.NR = nr
            Reservation._reservationPool.clear()

        hashCode = Reservation.getHashCode(day, time, room)
        reservation = Reservation.parse(hashCode)

        if reservation is None:
            reservation = Reservation(day, time, room)
            Reservation._reservationPool[hashCode] = reservation
        return reservation

    def __hash__(self) -> int:
        return Reservation.getHashCode(self.Day, self.Time, self.Room)


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)
            
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __str__(self):
        return "Day: " + str(self.Day) + ", " + "Room: " + str(self.Room) + ", Time: " + str(self.Time)
