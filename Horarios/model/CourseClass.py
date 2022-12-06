class CourseClass:
    #Contador de ID utilizado para asignar ID automáticamente
    _next_class_id = 0

    # Inicializa el objeto de clase
    def __init__(self, profesor, course, requires_lab, duration, groups):
        self.Id = CourseClass._next_class_id
        CourseClass._next_class_id += 1
        # Devolver puntero al profesor que enseña
        self.Profesor = profesor
        # Devuelve el puntero al curso al que pertenece la clase
        self.Course = course
        # Devuelve el número de asientos (estudiantes) necesarios en la aula
        self.NumberOfSeats = 0
        # Devuelve VERDADERO si la clase requiere computadoras en el salón.
        self.LabRequired = requires_lab
        # Devuelve la duración de la clase en horas
        self.Duration = duration
        # Devuelve la referencia a la lista de grupos de estudiantes que asisten a clase
        self.Groups = set(groups)

        #unir grupos de profesores a la clase
        self.Profesor.addCourseClass(self)

        # unir grupos de estudiantes a la clase
        for grp in self.Groups:  # self.groups:
            grp.addClass(self)
            self.NumberOfSeats += grp.NumberOfStudents

    # Devuelve VERDADERO si otra clase tiene uno o grupos de estudiantes superpuestos.
    def groupsOverlap(self, c):
        return len(self.Groups & c.Groups) > 0

    # Devuelve VERDADERO si otra clase tiene el mismo profesor.
    def profesorOverlaps(self, c):
        return self.Profesor == c.Profesor

    def __hash__(self):
        return hash(self.Id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        # No es estrictamente necesario, pero para evitar tener tanto x==y como x!=y
        # Cierto al mismo tiempo
        return not (self == other)

    # Reinicia las asignaciones de ID
    @staticmethod
    def restartIDs() -> None:
        CourseClass._next_class_id = 0
