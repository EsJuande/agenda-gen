"""Calendario 2027: signos, fases lunares y orden de las carillas."""

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "data" / "dias-especiales.txt"
ANIO = 2027

ART = ZoneInfo("America/Argentina/Buenos_Aires")
UTC = ZoneInfo("UTC")

MESES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)
MESES_CORTOS = (
    "ene",
    "feb",
    "mar",
    "abr",
    "may",
    "jun",
    "jul",
    "ago",
    "sep",
    "oct",
    "nov",
    "dic",
)
DIAS_CORTOS = ("lun", "mar", "mié", "jue", "vie", "sáb", "dom")

# El signo cambia en estas fechas, inclusive. Antes del 20 de enero sigue Capricornio.
_INICIOS_SIGNO = (
    (1, 20, "aquarius"),
    (2, 19, "pisces"),
    (3, 21, "aries"),
    (4, 20, "taurus"),
    (5, 21, "gemini"),
    (6, 21, "cancer"),
    (7, 23, "leo"),
    (8, 23, "virgo"),
    (9, 23, "libra"),
    (10, 23, "scorpio"),
    (11, 22, "sagittarius"),
    (12, 22, "capricorn"),
)

SIGNO_ES = {
    "aries": "Aries",
    "taurus": "Tauro",
    "gemini": "Géminis",
    "cancer": "Cáncer",
    "leo": "Leo",
    "virgo": "Virgo",
    "libra": "Libra",
    "scorpio": "Escorpio",
    "sagittarius": "Sagitario",
    "capricorn": "Capricornio",
    "aquarius": "Acuario",
    "pisces": "Piscis",
}

# Fases principales en UTC, del Observatorio Naval de Estados Unidos para 2027.
# En la carilla se usa el día civil de Argentina (UTC−3).
_FASES_UTC = (
    ("2027-01-07T20:24:00", "nueva"),
    ("2027-01-15T20:34:00", "cuarto-creciente"),
    ("2027-01-22T12:17:00", "llena"),
    ("2027-01-29T10:55:00", "cuarto-menguante"),
    ("2027-02-06T15:56:00", "nueva"),
    ("2027-02-14T07:58:00", "cuarto-creciente"),
    ("2027-02-20T23:23:00", "llena"),
    ("2027-02-28T05:16:00", "cuarto-menguante"),
    ("2027-03-08T09:29:00", "nueva"),
    ("2027-03-15T16:25:00", "cuarto-creciente"),
    ("2027-03-22T10:44:00", "llena"),
    ("2027-03-30T00:54:00", "cuarto-menguante"),
    ("2027-04-06T23:51:00", "nueva"),
    ("2027-04-13T22:56:00", "cuarto-creciente"),
    ("2027-04-20T22:27:00", "llena"),
    ("2027-04-28T20:18:00", "cuarto-menguante"),
    ("2027-05-06T10:58:00", "nueva"),
    ("2027-05-13T04:44:00", "cuarto-creciente"),
    ("2027-05-20T10:59:00", "llena"),
    ("2027-05-28T13:58:00", "cuarto-menguante"),
    ("2027-06-04T19:40:00", "nueva"),
    ("2027-06-11T10:56:00", "cuarto-creciente"),
    ("2027-06-19T00:44:00", "llena"),
    ("2027-06-27T04:54:00", "cuarto-menguante"),
    ("2027-07-04T03:02:00", "nueva"),
    ("2027-07-10T18:39:00", "cuarto-creciente"),
    ("2027-07-18T15:45:00", "llena"),
    ("2027-07-26T16:55:00", "cuarto-menguante"),
    ("2027-08-02T10:05:00", "nueva"),
    ("2027-08-09T04:54:00", "cuarto-creciente"),
    ("2027-08-17T07:29:00", "llena"),
    ("2027-08-25T02:27:00", "cuarto-menguante"),
    ("2027-08-31T17:41:00", "nueva"),
    ("2027-09-07T18:31:00", "cuarto-creciente"),
    ("2027-09-15T23:03:00", "llena"),
    ("2027-09-23T10:20:00", "cuarto-menguante"),
    ("2027-09-30T02:36:00", "nueva"),
    ("2027-10-07T11:47:00", "cuarto-creciente"),
    ("2027-10-15T13:47:00", "llena"),
    ("2027-10-22T17:29:00", "cuarto-menguante"),
    ("2027-10-29T13:36:00", "nueva"),
    ("2027-11-06T08:00:00", "cuarto-creciente"),
    ("2027-11-14T03:26:00", "llena"),
    ("2027-11-21T00:48:00", "cuarto-menguante"),
    ("2027-11-28T03:24:00", "nueva"),
    ("2027-12-06T05:22:00", "cuarto-creciente"),
    ("2027-12-13T16:09:00", "llena"),
    ("2027-12-20T09:11:00", "cuarto-menguante"),
    ("2027-12-27T20:12:00", "nueva"),
)

_ENTRE_FASES = {
    "nueva": "creciente",
    "cuarto-creciente": "gibosa-creciente",
    "llena": "gibosa-menguante",
    "cuarto-menguante": "menguante",
}


def cargar_mensajes(ruta=DATOS):
    mensajes = {}
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        fecha, texto = linea.split(";", 1)
        dia = date.fromisoformat(fecha.strip())
        mensajes.setdefault(dia, []).append(texto.strip())
    return mensajes


def signo_de(dia):
    actual = "capricorn"
    for mes, numero, nombre in _INICIOS_SIGNO:
        if (dia.month, dia.day) >= (mes, numero):
            actual = nombre
    return actual


def _fases_locales():
    fases = []
    for iso, nombre in _FASES_UTC:
        momento = datetime.fromisoformat(iso).replace(tzinfo=UTC).astimezone(ART)
        fases.append((momento.date(), nombre))
    return fases


_FASES_LOCALES = _fases_locales()


def fase_de(dia):
    """Fase del día. Si la tabla todavía no llega, usa la del día siguiente."""
    consulta = dia
    while True:
        previa = None
        hay_posterior = False
        for fecha, nombre in _FASES_LOCALES:
            if fecha <= consulta:
                previa = (fecha, nombre)
            else:
                hay_posterior = True
                break
        if previa is not None:
            fecha, nombre = previa
            if fecha == consulta:
                return nombre
            return _ENTRE_FASES[nombre]
        if not hay_posterior:
            raise ValueError(f"No hay fase lunar conocida para el {dia.isoformat()}.")
        consulta += timedelta(days=1)


@dataclass(frozen=True)
class Dia:
    fecha: date
    mensajes: tuple[str, ...]
    signo: str
    fase: str

    @property
    def nombre_corto(self):
        return DIAS_CORTOS[self.fecha.weekday()]

    @property
    def mes_corto(self):
        return MESES_CORTOS[self.fecha.month - 1]


@dataclass(frozen=True)
class Carilla:
    tipo: str
    anio: int
    mes: int
    dias: tuple[Dia, ...] = ()

    def archivo(self, indice):
        if self.tipo == "portada":
            base = "portada"
        elif self.tipo == "planner-izq":
            base = "planner-izquierda"
        elif self.tipo == "planner-der":
            base = "planner-derecha"
        elif self.tipo == "notas":
            base = "notas"
        elif self.tipo == "dia":
            base = f"dia-{self.dias[0].fecha.isoformat()}"
        elif self.tipo == "finde":
            fechas = "-".join(dia.fecha.isoformat() for dia in self.dias)
            base = f"finde-{fechas}"
        else:
            base = self.tipo
        return f"{indice:03d}-{base}.svg"

    def descripcion(self):
        nombre = MESES[self.mes - 1]
        if self.tipo == "portada":
            return f"Portada de {nombre}"
        if self.tipo == "planner-izq":
            return f"Planner de {nombre}, lunes a miércoles"
        if self.tipo == "planner-der":
            return f"Planner de {nombre}, jueves a domingo"
        if self.tipo == "notas":
            return f"Notas de {nombre}"
        partes = []
        for dia in self.dias:
            texto = f"{dia.nombre_corto} {dia.fecha.day}"
            if dia.mensajes:
                texto += " — " + " / ".join(dia.mensajes)
            partes.append(texto)
        return "  ·  ".join(partes)


def _dia(fecha, mensajes):
    return Dia(
        fecha=fecha,
        mensajes=tuple(mensajes.get(fecha, ())),
        signo=signo_de(fecha),
        fase=fase_de(fecha),
    )


def carillas_del_mes(anio, mes, mensajes=None):
    if mensajes is None:
        mensajes = cargar_mensajes()
    primero = date(anio, mes, 1)
    ultimo = date(anio, mes, monthrange(anio, mes)[1])
    dias = tuple(_dia(primero + timedelta(days=i), mensajes) for i in range(ultimo.day))
    carillas = [
        Carilla("portada", anio, mes),
        Carilla("planner-izq", anio, mes, dias),
        Carilla("planner-der", anio, mes, dias),
    ]
    cursor = primero
    while cursor <= ultimo:
        if cursor.weekday() == 5:
            grupo = [_dia(cursor, mensajes)]
            siguiente = cursor + timedelta(days=1)
            if siguiente <= ultimo and siguiente.weekday() == 6:
                grupo.append(_dia(siguiente, mensajes))
            carillas.append(Carilla("finde", anio, mes, tuple(grupo)))
            cursor = grupo[-1].fecha + timedelta(days=1)
        elif cursor.weekday() == 6:
            carillas.append(Carilla("finde", anio, mes, (_dia(cursor, mensajes),)))
            cursor += timedelta(days=1)
        else:
            carillas.append(Carilla("dia", anio, mes, (_dia(cursor, mensajes),)))
            cursor += timedelta(days=1)
    # Notas al final. Como mínimo una hoja (las dos carillas). Si con eso
    # la portada del mes siguiente no cae en página impar, se suma una carilla.
    carillas.append(Carilla("notas", anio, mes))
    carillas.append(Carilla("notas", anio, mes))
    if (len(carillas) + 1) % 2 == 0:
        carillas.append(Carilla("notas", anio, mes))
    return carillas


def comprobar():
    """Fechas que ya están fijas en los bocetos y en las efemérides de junio."""
    assert date(2027, 6, 1).weekday() == 1
    assert signo_de(date(2027, 3, 24)) == "aries"
    assert signo_de(date(2027, 5, 1)) == "taurus"
    assert signo_de(date(2027, 6, 20)) == "gemini"
    assert signo_de(date(2027, 6, 21)) == "cancer"
    assert fase_de(date(2027, 1, 1)) == "nueva"
    assert fase_de(date(2027, 1, 6)) == "nueva"
    assert fase_de(date(2027, 1, 7)) == "nueva"
    assert fase_de(date(2027, 1, 8)) == "creciente"
    assert fase_de(date(2027, 5, 1)) == "menguante"
    assert fase_de(date(2027, 6, 1)) == "menguante"
    assert fase_de(date(2027, 6, 4)) == "nueva"
    assert fase_de(date(2027, 6, 11)) == "cuarto-creciente"
    assert fase_de(date(2027, 6, 18)) == "llena"
    assert fase_de(date(2027, 6, 19)) == "gibosa-menguante"
    assert fase_de(date(2027, 6, 27)) == "cuarto-menguante"
    assert fase_de(date(2027, 6, 30)) == "menguante"
    junio = carillas_del_mes(2027, 6)
    assert [carilla.tipo for carilla in junio[:3]] == ["portada", "planner-izq", "planner-der"]
    assert len(junio) == 32
    assert [carilla.tipo for carilla in junio[-3:]] == ["notas", "notas", "notas"]
    assert sum(1 for carilla in junio if carilla.tipo == "dia") == 22
    assert sum(1 for carilla in junio if carilla.tipo == "finde") == 4
    for mes in range(1, 13):
        carillas = carillas_del_mes(2027, mes)
        cantidad = 0
        for carilla in reversed(carillas):
            if carilla.tipo != "notas":
                break
            cantidad += 1
        assert cantidad in (2, 3)
        assert cantidad == sum(1 for carilla in carillas if carilla.tipo == "notas")
        assert (len(carillas) + 1) % 2 == 1
