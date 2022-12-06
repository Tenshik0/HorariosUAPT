from model.Constantes import Constantes
from model.Reservation import Reservation
from collections import defaultdict


class TablaHorarios:
    ROOM_COLUMN_NUMBER = Constantes.DIAS_EN_LA_SEMANA + 1
    ROOM_ROW_NUMBER = Constantes.HORAS_AL_DIA + 1
    COLOR1 = "#319378"
    COLOR2 = "#CE0000"
    CRITERIAS = ('', '', '', '', '')
    #La sala actual tiene {alguna} superposición", 
    # "La sala actual tiene {cualquiera} asientos suficientes", X
    #"Habitación actual con {cualquiera} computadoras suficientes si se requieren",
    #"Los profesores tienen {cualquiera}clases superpuestas", 
    # "Los grupos de estudiantes tienen {cualquiera}clases superpuestas
    CRITERIAS_DESCR = ("Current room has {any}overlapping", 
                       "Current room has {any}enough seats",
                       "Current room with {any}enough computers if they are required",
                       "Profesor have {any}overlapping classes", 
                       "Student groups has {any}overlapping classes")
    HORAS = (
        "", "7 - 8", "8 - 9", "9 - 10", "10 - 11", "11 - 12", "12 - 13", "13 - 14", "14 - 15", "15 - 16", "16 - 17",
        "17 - 18", "18 - 19")
    DIAS_EN_LA_SEMANA = ("LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES")

    @staticmethod
    def getCourseClass(cc, criterias, ci):
        COLOR1 = TablaHorarios.COLOR1
        COLOR2 = TablaHorarios.COLOR2
        CRITERIAS = TablaHorarios.CRITERIAS
        length_CRITERIAS = len(CRITERIAS)
        CRITERIAS_DESCR = TablaHorarios.CRITERIAS_DESCR

        sb = [cc.Course.Name, "<br />", cc.Profesor.Name, "<br />", "/".join(map(lambda grp: grp.Name, cc.Groups)),
                  "<br />"]
        if cc.LabRequired:
            sb.append("Lab<br />")

        for i in range(length_CRITERIAS):
            sb.append("<span style='color:")
            if criterias[ci + i]:
                sb.append(COLOR1)
                sb.append("' title='")
                sb.append(CRITERIAS_DESCR[i].format(any="" if (i == 1 or i == 2) else "no "))
            else:
                sb.append(COLOR2)
                sb.append("' title='")
                sb.append(CRITERIAS_DESCR[i].format(any="not " if (i == 1 or i == 2) else ""))
            sb.append("'> ")
            sb.append(CRITERIAS[i])
            sb.append(" </span>")

        return sb

    @staticmethod
    def generateTimeTable(solution, slot_table):
        ci = 0

        time_table = defaultdict(list)
        items = solution.classes.items        
        ROOM_COLUMN_NUMBER = TablaHorarios.ROOM_COLUMN_NUMBER
        getCourseClass = TablaHorarios.getCourseClass

        for cc, reservation_index in items():
            reservation = Reservation.parse(reservation_index)

            # coordenada de la ranura espacio-temporal
            dayId = reservation.Day + 1
            horaId = reservation.Time + 1
            roomId = reservation.Room
            dur = cc.Duration

            key = (horaId, roomId)
            if key in slot_table:
                room_duration = slot_table[key]
            else:
                room_duration = ROOM_COLUMN_NUMBER * [0]
                slot_table[key] = room_duration
            room_duration[dayId] = dur

            for m in range(1, dur):
                next_key = (horaId + m, roomId)
                if next_key not in slot_table:
                    slot_table[next_key] = ROOM_COLUMN_NUMBER * [0]
                if slot_table[next_key][dayId] < 1:
                    slot_table[next_key][dayId] = -1

            if key in time_table:
                room_schedule = time_table[key]
            else:
                room_schedule = ROOM_COLUMN_NUMBER * [None]
                time_table[key] = room_schedule

            room_schedule[dayId] = "".join(getCourseClass(cc, solution.criteria, ci))
            ci += Constantes.NUMERO_DE_CRITERIOS

        return time_table

    @staticmethod
    def getHtmlCell(content, rowspan):
        if rowspan == 0:
            return "<td></td>"

        if content is None:
            return ""

        sb = []
        if rowspan > 1:
            sb.append("<td style='border: .1em solid black; padding: .25em' rowspan='")
            sb.append(rowspan)
            sb.append("'>")
        else:
            sb.append("<td style='border: .1em solid black; padding: .25em'>")

        sb.append(content)
        sb.append("</td>")
        return "".join(str(v) for v in sb)

    @staticmethod
    def getResult(solution):
        datos = solution.datos
        nr = datos.numberOfRooms
        getRoomById = datos.getRoomById

        slot_table = defaultdict(list)
        time_table = TablaHorarios.generateTimeTable(solution, slot_table)  # Tuple[0] = time, Tuple[1] = roomId
        if not slot_table or not time_table:
            return ""

        sb = []
        for roomId in range(nr):
            room = getRoomById(roomId)
            for horaId in range(TablaHorarios.ROOM_ROW_NUMBER):
                if horaId == 0:
                    sb.append("<div id='room_")
                    sb.append(room.Name)
                    sb.append("' style='padding: 0.5em'>\n")
                    sb.append("<table style='border-collapse: collapse; width: 95%'>\n")
                    sb.append(TablaHorarios.getTableHeader(room))
                else:
                    key = (horaId, roomId)
                    room_duration = slot_table[key] if key in slot_table.keys() else None
                    room_schedule = time_table[key] if key in time_table.keys() else None
                    sb.append("<tr>")
                    for dayId in range(TablaHorarios.ROOM_COLUMN_NUMBER):
                        if dayId == 0:
                            sb.append("<th style='border: .1em solid black; padding: .25em' scope='row' colspan='2'>")
                            sb.append(TablaHorarios.HORAS[horaId])
                            sb.append("</th>\n")
                            continue

                        if room_schedule is None and room_duration is None:
                            continue

                        content = room_schedule[dayId] if room_schedule is not None else None
                        sb.append(TablaHorarios.getHtmlCell(content, room_duration[dayId]))
                    sb.append("</tr>\n")

                if horaId == TablaHorarios.ROOM_ROW_NUMBER - 1:
                    sb.append("</table>\n</div>\n")

        return "".join(str(v) for v in sb)

    @staticmethod
    def getTableHeader(room):
        sb = ["<tr><th style='border: .1em solid black' scope='col' colspan='2'>Room: ", room.Name, "</th>\n"]
        for weekDay in TablaHorarios.DIAS_EN_LA_SEMANA:
            sb.append("<th style='border: .1em solid black; padding: .25em; width: 15%' scope='col' rowspan='2'>")
            sb.append(weekDay)
            sb.append("</th>\n")
        sb.append("</tr>\n")
        sb.append("<tr>\n")
        sb.append("<th style='border: .1em solid black; padding: .25em'>Lab: ")
        sb.append("Yes" if room.Lab else "No")
        sb.append("</th>\n")
        #sb.append("<th style='border: .1em solid black; padding: .25em'>Seats: ")
        #sb.append(room.NumberOfSeats)
        sb.append("</th>\n")
        sb.append("</tr>\n")
        return "".join(str(v) for v in sb)
