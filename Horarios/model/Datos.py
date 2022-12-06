import codecs
import json

from .Profesor import Profesor
from .StudentsGroup import StudentsGroup
from .Course import Course
from .Room import Room
from .CourseClass import CourseClass


# Lee el archivo de configuración y almacena los objetos analizados
class Datos:

    # Inicializar datos
    def __init__(self):
        # Indica que la configuración aún no se ha analizado
        self._isEmpty = True
        # Profesoras analizadas
        self._profesors = {}
        # grupos de estudiantes analizados
        self._studentGroups = {}
        # cursos analizados
        self._courses = {}
        # aulas analizadas
        self._rooms = {}
        # clases analizadas
        self._courseClasses = []

    # Devuelve profesora con identificación especificada
    #Si no hay ningún profesor con dicho método de ID devuelve NULL
    def getProfesorById(self, id) -> Profesor:
        if id in self._profesors:
            return self._profesors[id]
        return None

    @property
    # Devuelve el número de profesoras analizadas.
    def numberOfProfesors(self) -> int:
        return len(self._profesors)

    # Devuelve el grupo de estudiantes con ID especificado
    # Si no hay ningún grupo de estudiantes con dicho método de identificación, devuelve NULL
    def getStudentsGroupById(self, id) -> StudentsGroup:
        if id in self._studentGroups:
            return self._studentGroups[id]
        return None

    @property
    # Devuelve el número de grupos de estudiantes analizados
    def numberOfStudentGroups(self) -> int:
        return len(self._studentGroups)

    # Devuelve el curso con el ID especificado
    # Si no hay un curso con dicho método de identificación, devuelve NULL
    def getCourseById(self, id) -> Course:
        if id in self._courses:
            return self._courses[id]
        return None

    @property
    def numberOfCourses(self) -> int:
        return len(self._courses)

    # Devuelve la aula con el ID especificado
    # Si no hay aula con dicho método de identificación, devuelve NULL   
    def getRoomById(self, id) -> Room:
        if id in self._rooms:
            return self._rooms[id]
        return None

    @property
    # Devuelve el número de aulas analizadas
    def numberOfRooms(self) -> int:
        return len(self._rooms)

    @property
    # Devuelve la referencia a la lista de clases analizadas
    def courseClasses(self) -> []:
        return self._courseClasses

    @property
    # Devuelve el número de clases analizadas
    def numberOfCourseClasses(self) -> int:
        return len(self._courseClasses)

    @property
    # Devuelve VERDADERO si la configuración aún no se ha analizado
    def isEmpty(self) -> bool:
        return self._isEmpty

    # Lee los datos del profesor del archivo de configuración, crea un objeto y regresa
    # Devuelve NULL si el método no puede analizar los datos de configuración
    @staticmethod
    def __parseProfesor(dictConfig):
        id = 0
        name = ''

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]

        if id == 0 or name == '':
            return None
        return Profesor(id, name)

    # Lee los datos de StudentsGroup del archivo de configuración, crea un objeto y regresa
    # Devuelve Ninguno si el método no puede analizar los datos de configuración
    @staticmethod
    def __parseStudentsGroup(dictConfig):
        id = 0
        name = ''
        size = 0

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]
            elif key == 'size':
                size = dictConfig[key]

        if id == 0:
            return None
        return StudentsGroup(id, name, size)

    # Lee los datos del curso del archivo de configuración, crea un objeto y regresa
    # Devuelve Ninguno si el método dictConfig analiza los datos de configuración
    @staticmethod
    def __parseCourse(dictConfig):
        id = 0
        name = ''

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]

        if id == 0:
            return None
        return Course(id, name)

    #Lee los datos de las aulas del archivo de configuración, crea un objeto y regresa
    # Devuelve Ninguno si el método no puede analizar los datos de configuración
    @staticmethod
    def __parseRoom(dictConfig):
        lab = False
        name = ''
        size = 0

        for key in dictConfig:
            if key == 'lab':
                lab = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]
            elif key == 'size':
                size = dictConfig[key]

        if size == 0 or name == '':
            return None
        return Room(name, lab, size)

    # Lee los datos de la clase del archivo de configuración, crea el objeto y devuelve el puntero
    # Devuelve Ninguno si el método no puede analizar los datos de configuración
    def __parseCourseClass(self, dictConfig):
        pid = 0
        cid = 0
        dur = 1
        lab = False
        group_list = []

        for key in dictConfig:
            if key == 'profesor':
                pid = dictConfig[key]
            elif key == 'course':
                cid = dictConfig[key]
            elif key == 'lab':
                lab = dictConfig[key]
            elif key == 'duration':
                dur = dictConfig[key]
            elif key == 'group' or key == 'groups':
                groups = dictConfig[key]
                if isinstance(groups, list):
                    for grp in groups:
                        g = self.getStudentsGroupById(grp)
                        if g:
                            group_list.append(g)
                else:
                    g = self.getStudentsGroupById(groups)
                    if g:
                        group_list.append(g)

        # obtener el profesor que imparte la clase y el curso al que pertenece esta clase
        p = self.getProfesorById(pid)
        c = self.getCourseById(cid)

        # ¿Existe la profesora y la clase?
        if not c or not p:
            return None

        # hacer objeto y devolver
        return CourseClass(p, c, lab, dur, group_list)

    # analizar archivo y almacenar objeto analizado
    def parseFile(self, fileName):
        # borrar objetos analizados previamente
        self._profesors = {}
        self._studentGroups = {}
        self._courses = {}
        self._rooms = {}
        self._courseClasses = []

        Room.restartIDs()
        CourseClass.restartIDs()

        with codecs.open(fileName, "r", "utf-8") as f:
            # lea el archivo en una cadena y deserialice JSON a un tipo
            data = json.load(f)

        for dictConfig in data:
            for key in dictConfig:
                if key == 'prof':
                    prof = self.__parseProfesor(dictConfig[key])
                    self._profesors[prof.Id] = prof
                elif key == 'course':
                    course = self.__parseCourse(dictConfig[key])
                    self._courses[course.Id] = course
                elif key == 'room':
                    room = self.__parseRoom(dictConfig[key])
                    self._rooms[room.Id] = room
                elif key == 'group':
                    group = self.__parseStudentsGroup(dictConfig[key])
                    self._studentGroups[group.Id] = group
                elif key == 'class':
                    courseClass = self.__parseCourseClass(dictConfig[key])
                    self._courseClasses.append(courseClass)

        self._isEmpty = False
