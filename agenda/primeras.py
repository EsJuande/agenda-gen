"""Primeras páginas: datos, feriados, cumpleaños y planner anual."""

from calendar import monthrange
from datetime import date, timedelta

from .calendario import DIAS_CORTOS, FERIADOS, MESES, MESES_CORTOS, feriados_del_anio
from .dibujar import (
    BORDE_DER,
    GRIS,
    MARGEN_ANILLADO,
    TINTA,
    Y_PLANNER_0,
    Y_PLANNER_1,
    _documento,
    n,
)
from .tipografia import LIGHT, REGULAR

FINDE = "#f3f3f3"
TAMANO_TITULO = 14
TAMANO_SECCION = 3.8
TAMANO_FERIADO = 3.2
ICONO = 4.4
# Del texto de la sección al primer renglón. Igual en las cuatro secciones.
HUECO_LEYENDA = 13
# Entre renglones de la misma sección: dos pasos del pautado del resto de la agenda.
PASO_LINEAS = 38 / 3
# Del último renglón de una sección al título de la siguiente.
HUECO_SECCION = 32 / 3


def _titulo(ident, texto, anio=None):
    lineas = [
        f'  <g id="{ident}" inkscape:label="{ident}">',
        f'    <text id="titulo" x="{n(MARGEN_ANILLADO)}" y="22" fill="{TINTA}" '
        f'font-family="Lato Light, Lato" font-size="{n(TAMANO_TITULO)}" font-weight="300">'
        f"{texto}</text>",
    ]
    if anio is not None:
        x_anio = MARGEN_ANILLADO + LIGHT.ancho(texto, TAMANO_TITULO) + 3.5
        lineas.append(
            f'    <text id="detalle" x="{n(x_anio)}" y="22" fill="{GRIS}" font-family="Lato" '
            f'font-size="3.4" letter-spacing="0.35">{anio}</text>'
        )
    return lineas


def _seccion(ident, x, y, texto):
    return (
        f'    <text id="{ident}" x="{n(x)}" y="{n(y)}" fill="{TINTA}" font-family="Lato" '
        f'font-size="{n(TAMANO_SECCION)}">{texto}</text>'
    )


def _linea(ident, x1, x2, y):
    return (
        f'    <line id="{ident}" x1="{n(x1)}" y1="{n(y)}" x2="{n(x2)}" y2="{n(y)}" '
        f'stroke="{TINTA}" stroke-width="0.28"/>'
    )


def _icono(x, y, interior):
    return (
        f'<svg x="{n(x)}" y="{n(y)}" width="{n(ICONO)}" height="{n(ICONO)}" viewBox="0 0 24 24">'
        f'<g fill="none" stroke="{TINTA}" stroke-width="1.7" stroke-linejoin="round" '
        f'stroke-linecap="round">{interior}</g></svg>'
    )


def _persona():
    return (
        '<circle cx="12" cy="8" r="3.2"/>'
        '<path d="M6.2 19.6c.7-3.6 2.8-5.4 5.8-5.4s5.1 1.8 5.8 5.4"/>'
    )


def _celular():
    return (
        '<rect x="7" y="3" width="10" height="18" rx="2"/>'
        '<path d="M11 18.2h2"/>'
    )


def _sobre():
    return (
        '<rect x="3.5" y="6" width="17" height="12" rx="1.2"/>'
        '<path d="M4.2 7.2 12 13l7.8-5.8"/>'
    )


def _columnas():
    ancho = (BORDE_DER - MARGEN_ANILLADO - 8) / 2
    return (
        (MARGEN_ANILLADO, MARGEN_ANILLADO + ancho),
        (MARGEN_ANILLADO + ancho + 8, BORDE_DER),
    )


def _renglon_con_icono(ident, x1, x2, y, interior):
    return (
        "    " + _icono(x1, y - ICONO - 0.8, interior),
        _linea(ident, x1 + ICONO + 1.8, x2, y),
    )


def _renglones(y_leyenda, cantidad):
    return [y_leyenda + HUECO_LEYENDA + indice * PASO_LINEAS for indice in range(cantidad)]


def carilla_datos(anio, titulo, desc):
    columnas = _columnas()
    y = 40
    lineas = [
        *_titulo("datos", "datos personales"),
        _seccion("pertenece", MARGEN_ANILLADO, y, "Esta Agenda pertenece a"),
    ]
    for orden, y_linea in enumerate(_renglones(y, 2), start=1):
        lineas.append(_linea(f"nombre-{orden}", MARGEN_ANILLADO, BORDE_DER, y_linea))
    y = _renglones(y, 2)[-1] + HUECO_SECCION
    lineas.append(_seccion("contacto", MARGEN_ANILLADO, y, "Contactos de emergencia"))
    iconos = (_persona(), _celular(), _sobre())
    for fila, (y_linea, interior) in enumerate(zip(_renglones(y, 3), iconos), start=1):
        for columna, (x1, x2) in enumerate(columnas, start=1):
            lineas.extend(
                _renglon_con_icono(f"contacto-{columna}-{fila}", x1, x2, y_linea, interior)
            )
    y = _renglones(y, 3)[-1] + HUECO_SECCION
    lineas.append(_seccion("alergias", columnas[0][0], y, "Alergias"))
    lineas.append(_seccion("medicamentos", columnas[1][0], y, "Medicamentos"))
    for orden, y_linea in enumerate(_renglones(y, 2), start=1):
        lineas.append(_linea(f"alergias-{orden}", *columnas[0], y_linea))
        lineas.append(_linea(f"medicamentos-{orden}", *columnas[1], y_linea))
    y = _renglones(y, 2)[-1] + HUECO_SECCION
    lineas.append(_seccion("consideraciones", MARGEN_ANILLADO, y, "Consideraciones especiales"))
    for orden, y_linea in enumerate(_renglones(y, 3), start=1):
        lineas.append(_linea(f"consideraciones-{orden}", MARGEN_ANILLADO, BORDE_DER, y_linea))
    lineas.append("  </g>")
    return _documento(titulo, desc, "\n".join(lineas))


def carilla_feriados(anio, titulo, desc):
    lineas = [*_titulo("feriados", "feriados", anio)]
    x_dia = 30
    x_mes = 33
    x_nombre = 46
    y = 46
    nota_y = 198
    paso = (nota_y - 16 - y) / (len(FERIADOS) - 1)
    for mes, dia, nombre, trasladable in FERIADOS:
        fecha = date(anio, mes, dia)
        lineas.append(
            f'    <text x="{n(MARGEN_ANILLADO)}" y="{n(y)}" fill="{GRIS}" font-family="Lato" '
            f'font-size="{n(TAMANO_FERIADO)}">{DIAS_CORTOS[fecha.weekday()]}</text>'
        )
        lineas.append(
            f'    <text x="{n(x_dia)}" y="{n(y)}" fill="{GRIS}" font-family="Lato" '
            f'font-size="{n(TAMANO_FERIADO)}" text-anchor="end">{dia}</text>'
        )
        lineas.append(
            f'    <text x="{n(x_mes)}" y="{n(y)}" fill="{GRIS}" font-family="Lato" '
            f'font-size="{n(TAMANO_FERIADO)}">{MESES_CORTOS[mes - 1]}</text>'
        )
        lineas.append(
            f'    <text x="{n(x_nombre)}" y="{n(y)}" fill="{TINTA}" font-family="Lato" '
            f'font-size="{n(TAMANO_FERIADO)}">{nombre}</text>'
        )
        if trasladable:
            x_asterisco = x_nombre + REGULAR.ancho(nombre, TAMANO_FERIADO) + 0.8
            lineas.append(
                f'    <text x="{n(x_asterisco)}" y="{n(y - 1.6)}" fill="{TINTA}" font-family="Lato" '
                f'font-size="2.2">*</text>'
            )
        y += paso
    lineas.append(
        f'    <text id="nota" x="{n(MARGEN_ANILLADO)}" y="{n(nota_y)}" fill="{GRIS}" '
        f'font-family="Lato" font-size="2.8">* Feriados trasladables</text>'
    )
    lineas.append("  </g>")
    return _documento(titulo, desc, "\n".join(lineas))


def carilla_cumpleanos(anio, titulo, desc):
    columnas = 3
    filas = 4
    ancho = (BORDE_DER - MARGEN_ANILLADO) / columnas
    alto = (Y_PLANNER_1 - Y_PLANNER_0) / filas
    lineas = [
        *_titulo("cumpleanos", "cumpleaños", anio),
        f'    <rect id="marco" x="{n(MARGEN_ANILLADO)}" y="{n(Y_PLANNER_0)}" '
        f'width="{n(BORDE_DER - MARGEN_ANILLADO)}" height="{n(Y_PLANNER_1 - Y_PLANNER_0)}" '
        f'fill="none" stroke="{TINTA}" stroke-width="0.28"/>',
    ]
    for indice in range(1, columnas):
        x = MARGEN_ANILLADO + indice * ancho
        lineas.append(
            f'    <line x1="{n(x)}" y1="{n(Y_PLANNER_0)}" x2="{n(x)}" y2="{n(Y_PLANNER_1)}" '
            f'stroke="{TINTA}" stroke-width="0.22"/>'
        )
    for fila in range(1, filas):
        y = Y_PLANNER_0 + fila * alto
        lineas.append(
            f'    <line x1="{n(MARGEN_ANILLADO)}" y1="{n(y)}" x2="{n(BORDE_DER)}" y2="{n(y)}" '
            f'stroke="{TINTA}" stroke-width="0.22"/>'
        )
    for mes in range(1, 13):
        fila, columna = divmod(mes - 1, columnas)
        x = MARGEN_ANILLADO + columna * ancho + 2.4
        y = Y_PLANNER_0 + fila * alto + 8
        lineas.append(
            f'    <text x="{n(x)}" y="{n(y)}" fill="{TINTA}" font-family="Lato Light, Lato" '
            f'font-size="8" font-weight="300">{MESES_CORTOS[mes - 1]}</text>'
        )
    lineas.append("  </g>")
    return _documento(titulo, desc, "\n".join(lineas))


def _semanas_numeros(anio, mes):
    ultimo = monthrange(anio, mes)[1]
    primero = date(anio, mes, 1)
    inicio = primero - timedelta(days=primero.weekday())
    semanas = []
    cursor = inicio
    while len(semanas) < 6:
        semana = []
        for i in range(7):
            fecha = cursor + timedelta(days=i)
            if fecha.month == mes and fecha.year == anio and fecha.day <= ultimo:
                semana.append(fecha.day)
            else:
                semana.append(None)
        semanas.append(semana)
        cursor += timedelta(days=7)
    return semanas


def _mini_mes(x, y, ancho, alto, anio, mes):
    nombre = MESES[mes - 1]
    pad = 2.2
    letras = ("l", "m", "x", "j", "v", "s", "d")
    col = (ancho - 2 * pad) / 7
    y_nombre = y + 6
    y_letras = y + 11.4
    y_grilla = y + 13.6
    alto_fila = (y + alto - 1.4 - y_grilla) / 6
    lineas = [
        f'    <rect x="{n(x + pad + 5 * col)}" y="{n(y_letras - 2.6)}" width="{n(2 * col)}" '
        f'height="{n(y + alto - 1.2 - (y_letras - 2.6))}" fill="{FINDE}"/>',
        f'    <text x="{n(x + 2.4)}" y="{n(y_nombre)}" fill="{TINTA}" '
        f'font-family="Lato Light, Lato" font-size="4.6" font-weight="300">{nombre}</text>',
    ]
    for indice, letra in enumerate(letras):
        cx = x + pad + (indice + 0.5) * col
        lineas.append(
            f'    <text x="{n(cx)}" y="{n(y_letras)}" fill="{GRIS}" font-family="Lato" '
            f'font-size="1.8" text-anchor="middle">{letra}</text>'
        )
    for fila, semana in enumerate(_semanas_numeros(anio, mes)):
        baseline = y_grilla + (fila + 0.72) * alto_fila
        for indice, numero in enumerate(semana):
            if numero is None:
                continue
            cx = x + pad + (indice + 0.5) * col
            lineas.append(
                f'    <text x="{n(cx)}" y="{n(baseline)}" fill="{TINTA}" '
                f'font-family="Lato Light, Lato" font-size="2.4" font-weight="300" '
                f'text-anchor="middle">{numero}</text>'
            )
    return lineas


def _meses_del_lado(lado):
    """Filas de cuatro meses: dos en la carilla izquierda y dos en la derecha."""
    if lado == "izq":
        return (1, 2, 5, 6, 9, 10)
    return (3, 4, 7, 8, 11, 12)


def carilla_anual(anio, lado, titulo, desc):
    meses = _meses_del_lado(lado)
    lineas = [f'  <g id="anual" inkscape:label="planner anual">']
    if lado == "izq":
        lineas.extend(_titulo("anual", str(anio))[1:])
    columnas = 2
    filas = 3
    ancho = (BORDE_DER - MARGEN_ANILLADO) / columnas
    alto = (Y_PLANNER_1 - Y_PLANNER_0) / filas
    lineas.append(
        f'    <rect id="marco" x="{n(MARGEN_ANILLADO)}" y="{n(Y_PLANNER_0)}" '
        f'width="{n(BORDE_DER - MARGEN_ANILLADO)}" height="{n(Y_PLANNER_1 - Y_PLANNER_0)}" '
        f'fill="none" stroke="{TINTA}" stroke-width="0.28"/>'
    )
    x_medio = MARGEN_ANILLADO + ancho
    lineas.append(
        f'    <line x1="{n(x_medio)}" y1="{n(Y_PLANNER_0)}" x2="{n(x_medio)}" y2="{n(Y_PLANNER_1)}" '
        f'stroke="{TINTA}" stroke-width="0.22"/>'
    )
    for fila in range(1, filas):
        y = Y_PLANNER_0 + fila * alto
        lineas.append(
            f'    <line x1="{n(MARGEN_ANILLADO)}" y1="{n(y)}" x2="{n(BORDE_DER)}" y2="{n(y)}" '
            f'stroke="{TINTA}" stroke-width="0.22"/>'
        )
    for orden, mes in enumerate(meses):
        fila, columna = divmod(orden, columnas)
        x = MARGEN_ANILLADO + columna * ancho
        y = Y_PLANNER_0 + fila * alto
        lineas.extend(_mini_mes(x, y, ancho, alto, anio, mes))
    lineas.append("  </g>")
    return _documento(titulo, desc, "\n".join(lineas))


def svg_primeras(carilla, boceto=False):
    anio = carilla.anio
    if carilla.tipo == "datos":
        return carilla_datos(
            anio,
            "Datos personales — boceto" if boceto else f"Datos personales {anio}",
            "Carilla de datos personales. Nombre, dos contactos y notas de salud.",
        )
    if carilla.tipo == "feriados":
        return carilla_feriados(
            anio,
            "Feriados nacionales — boceto" if boceto else f"Feriados nacionales {anio}",
            "Feriados nacionales de Argentina, en el día en que se observan.",
        )
    if carilla.tipo == "cumpleanos":
        return carilla_cumpleanos(
            anio,
            "Cumpleaños — boceto" if boceto else f"Cumpleaños {anio}",
            "Doce meses, tres por fila, para anotar cumpleaños.",
        )
    if carilla.tipo == "anual-izq":
        return carilla_anual(
            anio,
            "izq",
            "Planner anual, izquierda — boceto" if boceto else f"Planner anual {anio}",
            "Enero, febrero, mayo, junio, septiembre y octubre. El finde va en gris.",
        )
    if carilla.tipo == "anual-der":
        return carilla_anual(
            anio,
            "der",
            "Planner anual, derecha — boceto" if boceto else f"Planner anual {anio}",
            "Marzo, abril, julio, agosto, noviembre y diciembre.",
        )
    raise ValueError(f"No sé dibujar una carilla {carilla.tipo!r}.")


def nombres_entran():
    """Los feriados entran en una línea, a la derecha de la fecha."""
    for _, _, nombre, trasladable in FERIADOS:
        extra = 2.4 if trasladable else 0
        if REGULAR.ancho(nombre, TAMANO_FERIADO) + extra > BORDE_DER - 46:
            return False
    return len(feriados_del_anio(2027)) == 17
