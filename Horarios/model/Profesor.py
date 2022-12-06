# Almacena datos sobre el profesor
class Profesor:
    # Inicializas los datos del profesor
    def __init__(self, id, name):
        self.Id = id
        self.Name = name
        self.CourseClasses = []

    #  Vincular al profesor al curso
    def addCourseClass(self, courseClass):
        self.CourseClasses.append(courseClass)

    def __hash__(self):
        return hash(self.Id)

    # Compara ID's de dos objetos que representan profesores
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        # No es estrictamente necesario, pero para evitar tener tanto x==y como x!=y
        # Cierto al mismo tiempo
        return not (self == other)
