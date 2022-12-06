# Almacena datos sobre el grupo de estudiantes.
class StudentsGroup:
    # Inicializa los datos del grupo de estudiantes
    def __init__(self, id, name, numberOfStudents):
        self.Id = id
        self.Name = name
        self.NumberOfStudents = numberOfStudents
        self.CourseClasses = []

    # Vincular grupo a clase
    def addClass(self, course_class):
        self.CourseClasses.append(course_class)

    def __hash__(self):
        return hash(self.Id)

    # Compara las identificaciones de dos objetos que representan grupos de estudiantes
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        # No es estrictamente necesario, pero para evitar tener tanto x==y como x!=y
        # Cierto al mismo tiempo
        return not (self == other)
