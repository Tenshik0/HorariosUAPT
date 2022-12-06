# Almacena datos sobre el aula
class Room:
    # Contador de ID utilizado para asignar ID automáticamente
    _next_room_id = 0

    # Inicializa los datos de la aula y asigna ID a la aula
    def __init__(self, name, lab, number_of_seats):
       # Devuelve el ID de la aula - asignado automáticamente
        self.Id = Room._next_room_id
        Room._next_room_id += 1
        # Devuelve el nombre     
        self.Name = name
        # Devuelve VERDADERO si la aula tiene computadoras, de lo contrario, devuelve FALSO
        self.Lab = lab
        # Devuelve el número de asientos en la aula
        self.NumberOfSeats = number_of_seats

    def __hash__(self):
        return hash(self.Id)

    # Compara ID de dos objetos que representan aulas
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        # No es estrictamente necesario, pero para evitar tener tanto x==y como x!=y
        # Verdadera al mismo tiempo
        return not (self == other)

    # Reinicia las asignaciones de ID
    @staticmethod
    def restartIDs() -> None:
        Room._next_room_id = 0
