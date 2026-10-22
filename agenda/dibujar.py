"""Carillas A5. El día y el finde copian la geometría de design/."""

import re
from datetime import timedelta
from functools import lru_cache
from xml.sax.saxutils import escape

from .calendario import MESES, MESES_CORTOS, RAIZ
from .tipografia import LIGHT, REGULAR

ICONOS = RAIZ / "assets" / "images"
DESIGN = RAIZ / "design"

ANCHO = 148.5
ALTO = 210
MARGEN_ANILLADO = 16
MARGEN = 10
BORDE_DER = ANCHO - MARGEN  # 138.5

TINTA = "#1a1a1a"
GRIS = "#8a8a8a"
LINEA_SUAVE = "#7a7a7a"
FINDE = "#f3f3f3"

# Medidos sobre Lato Light a 20 mm: cada cifra ocupa 11.6 y el rótulo queda a 4.8.
ANCHO_CIFRA = 11.6
HUECO_NUMERO = 4.8
NUMERO_X = 16

# Desplazamientos desde la línea de base del número grande, como en los bocetos.
DY_DIA = 9.8
DY_MES = 4.4
DY_AVISO = 7.35
DY_SIGNO = 12.3
DY_LUNA = 14.8

SIGNO_X = 120.15
SIGNO_LADO = 7
LUNA_X = 125.5
LUNA_LADO = 12

ESTRELLA = 3.6
HUECO_ESTRELLA = 1.8
TAMANO_AVISO = 2.2
# Entre dos mensajes distintos, el interlineado no pasa el hueco número–día.
PASO_ENTRE = HUECO_NUMERO
# El corte de un mismo mensaje va más cerrado que ese interlineado.
PASO_MISMO = 2.8
TAMANO_PORTADA = 36
TAMANO_PORTADA_SECUNDARIO = 3.6
INTERLETRADO_PORTADA = 1.2

# Los renglones de las 8.00 a las 20.00. El paso es el mismo en todas las hojas.
Y_RENGLON = 48
PASO = 19 / 3

HORA_TEXTO_X = 23.16
HORA_LINEA_X = 26.16


def n(valor):
    redondo = round(float(valor), 3)
    if abs(redondo - round(redondo)) < 1e-9:
        return str(int(round(redondo)))
    return f"{redondo:.3f}".rstrip("0")


def y_renglon(indice):
    return Y_RENGLON + indice * PASO


def x_rotulo(numero):
    return NUMERO_X + len(str(numero)) * ANCHO_CIFRA + HUECO_NUMERO


def x_espejo(x):
    """Refleja x dentro del área de contenido, de 16 a 138.5."""
    return MARGEN_ANILLADO + BORDE_DER - x


def _attrs(pares):
    partes = []
    for clave, valor in pares:
        if isinstance(valor, float):
            valor = n(valor)
        partes.append(f'{clave}="{valor}"')
    return " ".join(partes)


def _documento(titulo, desc, cuerpo):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        f'width="{n(ANCHO)}mm" height="{n(ALTO)}mm" viewBox="0 0 {n(ANCHO)} {n(ALTO)}">\n'
        f"  <title>{escape(titulo)}</title>\n"
        f"  <desc>{escape(desc)}</desc>\n"
        f"{cuerpo}\n"
        "</svg>\n"
    )


def margen_del_libro(svg, pagina):
    """La impar es la derecha: el anillado queda a la izquierda, como está dibujado.

    La par es la izquierda del libro. El contenido se corre para que los 16 mm
    queden del lado del anillado y los 10 mm del lado de afuera.
    """
    if pagina % 2 == 1:
        return svg
    marca = "</desc>\n"
    cierre = "</svg>\n"
    if marca not in svg or not svg.endswith(cierre):
        raise ValueError("El SVG no tiene el cierre esperado.")
    cabeza, resto = svg.split(marca, 1)
    cuerpo = resto[: -len(cierre)]
    desplazamiento = MARGEN - MARGEN_ANILLADO
    grupo = (
        f'  <g id="lado-izquierdo" inkscape:label="anillado a la derecha" '
        f'transform="translate({n(desplazamiento)}, 0)">\n'
        f"{cuerpo}"
        f"  </g>\n"
    )
    return cabeza + marca + grupo + cierre


@lru_cache(maxsize=None)
def _interior(ruta):
    texto = ruta.read_text(encoding="utf-8")
    texto = re.sub(r"<title\b[^>]*>.*?</title>", "", texto, flags=re.S)
    texto = re.sub(r"<desc\b[^>]*>.*?</desc>", "", texto, flags=re.S)
    hallado = re.search(r"<svg\b[^>]*>(.*)</svg>", texto, flags=re.S)
    return hallado.group(1).strip()


def _con_relleno(fragmento):
    if "fill=" in fragmento:
        return fragmento
    return fragmento.replace("<path ", '<path fill="#1a1a1a" ', 1)


def _icono(ident, x, y, lado, viewbox, interior):
    identificador = f' id="{ident}"' if ident else ""
    return (
        f"<svg{identificador} x=\"{n(x)}\" y=\"{n(y)}\" "
        f'width="{n(lado)}" height="{n(lado)}" viewBox="{viewbox}">'
        f"{interior}</svg>"
    )


def _signo(ident, x, y, nombre):
    interior = _con_relleno(_interior(ICONOS / "signos" / f"zodiac-{nombre}.svg"))
    return _icono(ident, x, y, SIGNO_LADO, "0 0 24 24", interior)


def _luna(ident, x, y, fase):
    interior = _interior(ICONOS / "fases-lunares" / f"{fase}.svg")
    return _icono(ident, x, y, LUNA_LADO, "-6 -6 12 12", interior)


def _estrella(x, y, lado=ESTRELLA):
    interior = _con_relleno(_interior(ICONOS / "star-four-points-circle-outline.svg"))
    return _icono("", x, y, lado, "2 2 20 20", interior)


def disponible_aviso(fecha_derecha):
    """Ancho de texto que, centrado, deja el hueco mínimo a cada lado."""
    return (
        SIGNO_X
        - fecha_derecha
        - 2 * HUECO_NUMERO
        - ESTRELLA
        - HUECO_ESTRELLA
    )


def x_aviso(fecha_derecha, ancho_bloque):
    """Borde izquierdo de la estrella. El bloque queda al medio del hueco."""
    return fecha_derecha + (SIGNO_X - fecha_derecha - ancho_bloque) / 2


def partir_mensaje(mensaje, disponible):
    """Parte en dos líneas si no entra. El cuerpo no cambia."""
    if REGULAR.ancho(mensaje, TAMANO_AVISO) <= disponible:
        return (mensaje,)
    palabras = mensaje.split(" ")
    mejor = None
    for corte in range(1, len(palabras)):
        arriba = " ".join(palabras[:corte])
        abajo = " ".join(palabras[corte:])
        ancho_arriba = REGULAR.ancho(arriba, TAMANO_AVISO)
        ancho_abajo = REGULAR.ancho(abajo, TAMANO_AVISO)
        if ancho_arriba <= disponible and ancho_abajo <= disponible:
            desvio = abs(ancho_arriba - ancho_abajo)
            if mejor is None or desvio < mejor[0]:
                mejor = (desvio, arriba, abajo)
    if mejor is not None:
        return (mejor[1], mejor[2])
    return (mensaje,)


def _cabecera(prefijo, dia, numero_y, espejo=False):
    """Encabezado de un día. En la carilla impar, fecha, signo y luna van en espejo.

    El orden de izquierda a derecha queda: fase, signo, aviso, día y mes, número.
    prefijo vacío en la carilla de semana.
    """
    ident = (lambda nombre: f"{prefijo}-{nombre}" if prefijo else nombre)
    x_texto = x_rotulo(dia.fecha.day)
    if espejo:
        x_numero = x_espejo(NUMERO_X)
        x_fecha = x_espejo(x_texto)
        ancla = ' text-anchor="end"'
        signo_x = x_espejo(SIGNO_X + SIGNO_LADO)
        luna_x = x_espejo(LUNA_X + LUNA_LADO)
    else:
        x_numero = NUMERO_X
        x_fecha = x_texto
        ancla = ""
        signo_x = SIGNO_X
        luna_x = LUNA_X
    grupo = (
        f'  <g id="{ident("cabecera") if not prefijo else prefijo}" '
        f'inkscape:label="{prefijo or "cabecera"}">'
    )
    numero = (
        f'    <text id="{ident("numero")}" x="{n(x_numero)}" y="{n(numero_y)}"{ancla} '
        f'fill="{TINTA}" font-family="Lato Light, Lato" font-size="20" font-weight="300">'
        f"{dia.fecha.day}</text>"
    )
    fecha = [
        f'    <text id="{ident("dia")}" x="{n(x_fecha)}" y="{n(numero_y - DY_DIA)}"{ancla} '
        f'fill="{TINTA}" font-family="Lato" font-size="3.4" letter-spacing="0.45">'
        f"{escape(dia.nombre_corto)}</text>",
        f'    <text id="{ident("mes")}" x="{n(x_fecha)}" y="{n(numero_y - DY_MES)}"{ancla} '
        f'fill="{GRIS}" font-family="Lato" font-size="3.4" letter-spacing="0.45">'
        f"{escape(dia.mes_corto)}</text>",
    ]
    aviso = _aviso(ident, dia, numero_y, x_texto, espejo) if dia.mensajes else []
    signo_y = numero_y - DY_SIGNO
    luna_y = numero_y - DY_LUNA
    signo = "    " + _signo(ident("signo"), signo_x, signo_y, dia.signo)
    luna = "    " + _luna(ident("fase-lunar"), luna_x, luna_y, dia.fase)
    if espejo:
        lineas = [grupo, luna, signo, *aviso, *fecha, numero, "  </g>"]
    else:
        lineas = [grupo, numero, *fecha, *aviso, signo, luna, "  </g>"]
    return lineas


def _aviso(ident, dia, numero_y, x_texto, espejo=False):
    anchos_fecha = (
        REGULAR.ancho(dia.nombre_corto, 3.4, 0.45),
        REGULAR.ancho(dia.mes_corto, 3.4, 0.45),
    )
    ancho_fecha = max(anchos_fecha)
    fecha_derecha = x_texto + ancho_fecha
    disponible = disponible_aviso(fecha_derecha)
    bloques = [partir_mensaje(mensaje, disponible) for mensaje in dia.mensajes]
    offsets = []
    textos = []
    cursor = 0.0
    for indice_bloque, bloque in enumerate(bloques):
        if indice_bloque:
            cursor += PASO_ENTRE
        for indice_linea, linea in enumerate(bloque):
            if indice_linea:
                cursor += PASO_MISMO
            offsets.append(cursor)
            textos.append(linea)
    ancho_texto = max(REGULAR.ancho(texto, TAMANO_AVISO) for texto in textos)
    ancho_bloque = ESTRELLA + HUECO_ESTRELLA + ancho_texto
    if espejo:
        # El bloque sigue estrella y texto hacia la derecha, centrado en el hueco reflejado.
        borde_signo = x_espejo(SIGNO_X)
        borde_fecha = x_espejo(x_texto) - ancho_fecha
        x_estrella = borde_signo + (borde_fecha - borde_signo - ancho_bloque) / 2
    else:
        x_estrella = x_aviso(fecha_derecha, ancho_bloque)
    x_mensaje = x_estrella + ESTRELLA + HUECO_ESTRELLA
    medio = (offsets[0] + offsets[-1]) / 2
    centro = numero_y - DY_AVISO
    y_estrella = centro - 0.6 - ESTRELLA / 2
    lineas = [
        f'    <g id="{ident("feriado")}" inkscape:label="aviso">',
        "      " + _estrella(x_estrella, y_estrella),
    ]
    for offset, texto in zip(offsets, textos):
        baseline = centro + (offset - medio)
        lineas.append(
            f'      <text x="{n(x_mensaje)}" y="{n(baseline)}" fill="{TINTA}" '
            f'font-family="Lato" font-size="{n(TAMANO_AVISO)}">{escape(texto)}</text>'
        )
    lineas.append("    </g>")
    return lineas


def _horario(prefijo, desde, hasta, con_numeros, x1):
    """desde y hasta son las horas en punto, inclusive. 8 y 20 cubren el día de semana."""
    ident = (lambda nombre: f"{prefijo}-{nombre}" if prefijo else nombre)
    lineas = [f'  <g id="{ident("horario")}" inkscape:label="horario" fill="none">']
    primera = (desde - 8) * 2
    ultima = (hasta - 8) * 2
    for indice in range(primera, ultima + 1):
        hora = 8 + indice // 2
        media = indice % 2 == 1
        etiqueta = f"{hora}.30" if media else f"{hora}.00"
        grupo = ident(f"hora-{hora:02d}-30" if media else f"hora-{hora:02d}")
        y = y_renglon(indice)
        lineas.append(f'    <g id="{grupo}" inkscape:label="{etiqueta}">')
        if media or not con_numeros:
            lineas.append(
                f'      <line x1="{n(x1)}" y1="{n(y)}" x2="{n(BORDE_DER)}" y2="{n(y)}" '
                f'stroke="{LINEA_SUAVE}" stroke-width="0.22" stroke-dasharray="0.35 0.85" '
                f'stroke-linecap="round"/>'
            )
        else:
            lineas.append(
                f'      <text x="{HORA_TEXTO_X}" y="{n(y)}" fill="{TINTA}" font-family="Lato" '
                f'font-size="2.8" text-anchor="end" dominant-baseline="central">{etiqueta}</text>'
            )
            lineas.append(
                f'      <line x1="{HORA_LINEA_X}" y1="{n(y)}" x2="{n(BORDE_DER)}" y2="{n(y)}" '
                f'stroke="{TINTA}" stroke-width="0.28"/>'
            )
        lineas.append("    </g>")
    lineas.append("  </g>")
    return lineas


def _renglones_domingo():
    """Del mismo paso que el horario, desde la altura de las 17.00 hasta las 20.00."""
    lineas = ['  <g id="domingo-renglones" inkscape:label="renglones" fill="none">']
    for orden, indice in enumerate(range(18, 25), start=1):
        y = y_renglon(indice)
        if indice % 2 == 0:
            trazo = (
                f'stroke="{TINTA}" stroke-width="0.28"'
            )
        else:
            trazo = (
                f'stroke="{LINEA_SUAVE}" stroke-width="0.22" '
                f'stroke-dasharray="0.35 0.85" stroke-linecap="round"'
            )
        lineas.append(
            f'    <line id="domingo-renglon-{orden:02d}" x1="{n(MARGEN_ANILLADO)}" '
            f'y1="{n(y)}" x2="{n(BORDE_DER)}" y2="{n(y)}" {trazo}/>'
        )
    lineas.append("  </g>")
    return lineas


def carilla_dia(dia, titulo, desc, espejo=False):
    cuerpo = _cabecera("", dia, 35, espejo)
    cuerpo.extend(_horario("", 8, 20, True, HORA_LINEA_X))
    return _documento(titulo, desc, "\n".join(cuerpo))


def carilla_finde(dias, titulo, desc, espejo=False):
    sabado = next((dia for dia in dias if dia.fecha.weekday() == 5), None)
    domingo = next((dia for dia in dias if dia.fecha.weekday() == 6), None)
    cuerpo = []
    if sabado:
        cuerpo.extend(_cabecera("sabado", sabado, 35, espejo))
        # El horario queda dentro del grupo sábado, como en el boceto.
        cuerpo = cuerpo[:-1]
        cuerpo.extend("  " + linea if linea.startswith("  ") else linea for linea in _horario("sabado", 8, 14, True, HORA_LINEA_X))
        cuerpo.append("  </g>")
    if domingo:
        cuerpo.extend(_cabecera("domingo", domingo, 149, espejo))
        cuerpo = cuerpo[:-1]
        cuerpo.extend(_renglones_domingo())
        cuerpo.append("  </g>")
    return _documento(titulo, desc, "\n".join(cuerpo))


def carilla_portada(anio, mes, titulo, desc):
    """El cuerpo grande es el mes en tres letras. Debajo, el nombre completo y el año, en una línea."""
    corto = MESES_CORTOS[mes - 1]
    nombre = MESES[mes - 1]
    baseline = 102
    regla = baseline + TAMANO_PORTADA * 0.30
    linea = regla + 8
    hueco = TAMANO_PORTADA_SECUNDARIO
    ancho_anio = REGULAR.ancho(str(anio), TAMANO_PORTADA_SECUNDARIO, INTERLETRADO_PORTADA)
    ancho_nombre = REGULAR.ancho(nombre, TAMANO_PORTADA_SECUNDARIO, INTERLETRADO_PORTADA)
    x_mes = BORDE_DER - ancho_anio - hueco
    ancho = BORDE_DER - MARGEN_ANILLADO
    if LIGHT.ancho(corto, TAMANO_PORTADA) > ancho:
        raise ValueError(f"{corto!r} no entra en la portada a {TAMANO_PORTADA} mm.")
    if ancho_nombre + hueco + ancho_anio > ancho:
        raise ValueError(f"{nombre} {anio} no entra debajo del mes corto.")
    cuerpo = "\n".join(
        [
            '  <g id="portada" inkscape:label="portada">',
            f'    <text id="mes-corto" x="{n(BORDE_DER)}" y="{n(baseline)}" fill="{TINTA}" '
            f'text-anchor="end" font-family="Lato Light, Lato" font-size="{n(TAMANO_PORTADA)}" '
            f'font-weight="300">{escape(corto)}</text>',
            f'    <line id="regla" x1="{n(BORDE_DER - 22)}" y1="{n(regla)}" '
            f'x2="{n(BORDE_DER)}" y2="{n(regla)}" stroke="{TINTA}" stroke-width="0.28"/>',
            f'    <text id="mes" x="{n(x_mes)}" y="{n(linea)}" fill="{GRIS}" '
            f'text-anchor="end" font-family="Lato" font-size="{n(TAMANO_PORTADA_SECUNDARIO)}" '
            f'letter-spacing="{n(INTERLETRADO_PORTADA)}">{escape(nombre)}</text>',
            f'    <text id="anio" x="{n(BORDE_DER)}" y="{n(linea)}" fill="{GRIS}" '
            f'text-anchor="end" font-family="Lato" font-size="{n(TAMANO_PORTADA_SECUNDARIO)}" '
            f'letter-spacing="{n(INTERLETRADO_PORTADA)}">{anio}</text>',
            "  </g>",
        ]
    )
    return _documento(titulo, desc, cuerpo)


Y_PLANNER_TITULO = 22
Y_PLANNER_ROTULO = 32
Y_PLANNER_0 = 38
Y_PLANNER_1 = 200
TAMANO_CELDA = 5.5
FILAS_PLANNER = 5
PAD_CELDA = 2.4
# La línea de base del número queda a 8 del borde superior.
Y_CIFRA = 8
# Cap height de Lato Light, 1415/2000. El día posterior deja el mismo aire.
PAD_CIFRA = Y_CIFRA - (1415 / 2000) * TAMANO_CELDA
HUECO_ESTRELLA_CELDA = 1.3
DY_ESTRELLA_CELDA = 5.1
LADO_ESTRELLA_CELDA = 3.2

COLUMNAS_IZQ = (
    ("lun", (0,)),
    ("mar", (1,)),
    ("mié", (2,)),
)
COLUMNAS_DER = (
    ("jue", (3,)),
    ("vie", (4,)),
    ("sáb / dom", (5, 6)),
)


def _semanas(anio, mes, dias):
    """Semanas de lunes a domingo. None es un día de otro mes."""
    por_fecha = {dia.fecha: dia for dia in dias}
    primero = dias[0].fecha
    ultimo = dias[-1].fecha
    inicio = primero - timedelta(days=primero.weekday())
    fin = ultimo + timedelta(days=(6 - ultimo.weekday()))
    semanas = []
    cursor = inicio
    while cursor <= fin:
        semana = []
        for i in range(7):
            fecha = cursor + timedelta(days=i)
            if fecha.month == mes and fecha.year == anio:
                semana.append(por_fecha[fecha])
            else:
                semana.append(None)
        semanas.append(semana)
        cursor += timedelta(days=7)
    return semanas


def _grupos_de_filas(semanas):
    """Cinco filas. La sexta semana, si existe, comparte la última."""
    if len(semanas) > 6:
        raise ValueError(f"El mes no entra en la grilla de cinco filas: {len(semanas)} semanas.")
    grupos = []
    for fila in range(FILAS_PLANNER):
        if fila < 4:
            grupos.append([semanas[fila]] if fila < len(semanas) else [[None] * 7])
            continue
        grupo = [semanas[i] for i in (4, 5) if i < len(semanas)]
        grupos.append(grupo or [[None] * 7])
    return grupos


def _dias_celda(grupo, indices):
    dias = []
    for semana in grupo:
        for indice in indices:
            dia = semana[indice]
            if dia is not None:
                dias.append(dia)
    return dias


def _numero_celda(x, y, dia, derecha=False):
    """x es el borde izquierdo, o el derecho si el día va al extremo inferior."""
    cifras = LIGHT.ancho(str(dia.fecha.day), TAMANO_CELDA)
    ancla = ' text-anchor="end"' if derecha else ""
    lineas = [
        f'    <text x="{n(x)}" y="{n(y)}"{ancla} fill="{TINTA}" font-family="Lato Light, Lato" '
        f'font-size="{n(TAMANO_CELDA)}" font-weight="300">{dia.fecha.day}</text>'
    ]
    if dia.mensajes:
        if derecha:
            x_estrella = x - cifras - HUECO_ESTRELLA_CELDA - LADO_ESTRELLA_CELDA
        else:
            x_estrella = x + cifras + HUECO_ESTRELLA_CELDA
        lineas.append("    " + _estrella(x_estrella, y - DY_ESTRELLA_CELDA, LADO_ESTRELLA_CELDA))
    return lineas


def carilla_planner(anio, mes, dias, lado, titulo, desc):
    """Izquierda: lun, mar, mié. Derecha: jue, vie y el finde en una columna.

    La grilla es siempre de cinco filas. Sábado y domingo comparten casillero,
    y una sexta semana se pliega en la última fila del mismo modo.
    """
    nombre = MESES[mes - 1]
    columnas = COLUMNAS_IZQ if lado == "izq" else COLUMNAS_DER
    grupos = _grupos_de_filas(_semanas(anio, mes, dias))
    ancho = (BORDE_DER - MARGEN_ANILLADO) / len(columnas)
    alto = (Y_PLANNER_1 - Y_PLANNER_0) / FILAS_PLANNER
    lineas = ['  <g id="planner" inkscape:label="calendario">']
    if lado == "izq":
        tamano = 14
        x_anio = MARGEN_ANILLADO + LIGHT.ancho(nombre, tamano) + 3.5
        lineas.append(
            f'    <text id="mes" x="{n(MARGEN_ANILLADO)}" y="{n(Y_PLANNER_TITULO)}" fill="{TINTA}" '
            f'font-family="Lato Light, Lato" font-size="{n(tamano)}" font-weight="300">'
            f"{escape(nombre)}</text>"
        )
        lineas.append(
            f'    <text id="anio" x="{n(x_anio)}" y="{n(Y_PLANNER_TITULO)}" fill="{GRIS}" '
            f'font-family="Lato" font-size="3.4" letter-spacing="0.35">{anio}</text>'
        )
    else:
        x_finde = MARGEN_ANILLADO + 2 * ancho
        lineas.append(
            f'    <rect x="{n(x_finde)}" y="{n(Y_PLANNER_0)}" width="{n(ancho)}" '
            f'height="{n(Y_PLANNER_1 - Y_PLANNER_0)}" fill="{FINDE}"/>'
        )
    for indice, (rotulo, _) in enumerate(columnas):
        cx = MARGEN_ANILLADO + (indice + 0.5) * ancho
        lineas.append(
            f'    <text x="{n(cx)}" y="{n(Y_PLANNER_ROTULO)}" fill="{GRIS}" font-family="Lato" '
            f'font-size="2.6" text-anchor="middle" letter-spacing="0.2">{rotulo}</text>'
        )
    lineas.append(
        f'    <rect id="marco" x="{n(MARGEN_ANILLADO)}" y="{n(Y_PLANNER_0)}" '
        f'width="{n(BORDE_DER - MARGEN_ANILLADO)}" height="{n(Y_PLANNER_1 - Y_PLANNER_0)}" '
        f'fill="none" stroke="{TINTA}" stroke-width="0.28"/>'
    )
    for indice in range(1, len(columnas)):
        x = MARGEN_ANILLADO + indice * ancho
        lineas.append(
            f'    <line x1="{n(x)}" y1="{n(Y_PLANNER_0)}" x2="{n(x)}" y2="{n(Y_PLANNER_1)}" '
            f'stroke="{TINTA}" stroke-width="0.22"/>'
        )
    for fila in range(1, FILAS_PLANNER):
        y = Y_PLANNER_0 + fila * alto
        lineas.append(
            f'    <line x1="{n(MARGEN_ANILLADO)}" y1="{n(y)}" x2="{n(BORDE_DER)}" y2="{n(y)}" '
            f'stroke="{TINTA}" stroke-width="0.22"/>'
        )
    for fila, grupo in enumerate(grupos):
        y_superior = Y_PLANNER_0 + fila * alto + Y_CIFRA
        y_posterior = Y_PLANNER_0 + (fila + 1) * alto - PAD_CIFRA
        for indice, (_, dias_columna) in enumerate(columnas):
            x = MARGEN_ANILLADO + indice * ancho
            x_der = BORDE_DER if indice == len(columnas) - 1 else x + ancho
            dias_en_celda = _dias_celda(grupo, dias_columna)
            if len(dias_en_celda) > 2:
                raise ValueError("Un casillero no puede compartir más de dos días.")
            if not dias_en_celda:
                continue
            lineas.extend(_numero_celda(x + PAD_CELDA, y_superior, dias_en_celda[0]))
            if len(dias_en_celda) > 1:
                lineas.extend(
                    _numero_celda(x_der - PAD_CELDA, y_posterior, dias_en_celda[-1], derecha=True)
                )
    lineas.append("  </g>")
    return _documento(titulo, desc, "\n".join(lineas))


def carilla_planner_izq(anio, mes, dias, titulo, desc):
    return carilla_planner(anio, mes, dias, "izq", titulo, desc)


def carilla_planner_der(anio, mes, dias, titulo, desc):
    return carilla_planner(anio, mes, dias, "der", titulo, desc)


def carilla_notas(anio, mes, titulo, desc):
    nombre = MESES[mes - 1]
    tamano = 14
    x_mes = MARGEN_ANILLADO + LIGHT.ancho("notas", tamano) + 3.5
    lineas = [
        '  <g id="notas" inkscape:label="notas">',
        f'    <text id="titulo" x="{n(MARGEN_ANILLADO)}" y="22" fill="{TINTA}" '
        f'font-family="Lato Light, Lato" font-size="{n(tamano)}" font-weight="300">notas</text>',
        f'    <text id="mes" x="{n(x_mes)}" y="22" fill="{GRIS}" font-family="Lato" '
        f'font-size="3.4" letter-spacing="0.35">{escape(nombre)} {anio}</text>',
        '    <g id="renglones" inkscape:label="renglones" fill="none">',
    ]
    # Dos renglones por encima de las 8.00, en el mismo paso, para acercarlos al título.
    for orden, indice in enumerate(range(-2, 25)):
        y = y_renglon(indice)
        if indice % 2 == 0:
            trazo = f'stroke="{TINTA}" stroke-width="0.28"'
        else:
            trazo = (
                f'stroke="{LINEA_SUAVE}" stroke-width="0.22" '
                f'stroke-dasharray="0.35 0.85" stroke-linecap="round"'
            )
        lineas.append(
            f'      <line id="renglon-{orden:02d}" x1="{n(MARGEN_ANILLADO)}" y1="{n(y)}" '
            f'x2="{n(BORDE_DER)}" y2="{n(y)}" {trazo}/>'
        )
    lineas.append("    </g>")
    lineas.append("  </g>")
    return _documento(titulo, desc, "\n".join(lineas))


def svg_de_carilla(carilla, boceto=False, pagina=1):
    nombre = MESES[carilla.mes - 1]
    if carilla.tipo == "portada":
        titulo = "Portada de mes — boceto" if boceto else f"Portada de {nombre} {carilla.anio}"
        desc = (
            f"Boceto de portada de mes, A5, alineada a la derecha. El cuerpo grande es el mes en tres letras. Debajo, el nombre completo y el año en la misma línea. Ejemplo: {nombre} {carilla.anio}."
            if boceto
            else f"Portada de {nombre} de {carilla.anio}."
        )
        return margen_del_libro(carilla_portada(carilla.anio, carilla.mes, titulo, desc), pagina)
    if carilla.tipo == "planner-izq":
        titulo = "Planner mensual, izquierda — boceto" if boceto else f"Calendario de {nombre} {carilla.anio}"
        desc = (
            f"Boceto del planner mensual, carilla izquierda. El anillado queda a la derecha. Ejemplo: {nombre} {carilla.anio}."
            if boceto
            else f"Calendario de {nombre} de {carilla.anio}. La estrella marca un día con aviso."
        )
        return margen_del_libro(
            carilla_planner_izq(carilla.anio, carilla.mes, carilla.dias, titulo, desc), pagina
        )
    if carilla.tipo == "planner-der":
        titulo = "Planner mensual, derecha — boceto" if boceto else f"Calendario de {nombre} {carilla.anio}"
        desc = (
            f"Boceto del planner mensual, carilla derecha. Jueves, viernes y finde. En un casillero compartido, el día posterior va abajo a la derecha. Ejemplo: {nombre} {carilla.anio}."
            if boceto
            else f"Jueves, viernes y finde de {nombre} de {carilla.anio}."
        )
        return margen_del_libro(
            carilla_planner_der(carilla.anio, carilla.mes, carilla.dias, titulo, desc), pagina
        )
    if carilla.tipo == "notas":
        titulo = "Notas — boceto" if boceto else f"Notas de {nombre} {carilla.anio}"
        desc = (
            f"Boceto de carilla de notas. Va al final del mes. Ejemplo: {nombre} {carilla.anio}."
            if boceto
            else f"Notas de {nombre} de {carilla.anio}."
        )
        return margen_del_libro(carilla_notas(carilla.anio, carilla.mes, titulo, desc), pagina)
    if carilla.tipo == "dia":
        dia = carilla.dias[0]
        return margen_del_libro(
            carilla_dia(
                dia,
                f"{dia.fecha.isoformat()}",
                f"{dia.nombre_corto} {dia.fecha.day} de {nombre} de {carilla.anio}.",
                espejo=pagina % 2 == 1,
            ),
            pagina,
        )
    if carilla.tipo == "finde":
        fechas = " y ".join(str(dia.fecha.day) for dia in carilla.dias)
        return margen_del_libro(
            carilla_finde(
                carilla.dias,
                "finde " + "-".join(dia.fecha.isoformat() for dia in carilla.dias),
                f"Sábado y domingo, {fechas} de {nombre} de {carilla.anio}.",
                espejo=pagina % 2 == 1,
            ),
            pagina,
        )
    raise ValueError(f"No sé dibujar una carilla {carilla.tipo!r}.")


def escribir_bocetos(carillas):
    """Portada, planner y notas, para retocar en Inkscape. No pisa un boceto que ya exista."""
    destinos = {
        "portada": DESIGN / "carilla-portada-mes.svg",
        "planner-izq": DESIGN / "carilla-planner-izq.svg",
        "planner-der": DESIGN / "carilla-planner-der.svg",
        "notas": DESIGN / "carilla-notas.svg",
    }
    # El boceto del planner izquierdo es la carilla par: el anillado va a la derecha.
    pagina_boceto = {"planner-izq": 2}
    escritos = []
    for carilla in carillas:
        destino = destinos.get(carilla.tipo)
        if destino is None or destino.exists():
            continue
        destino.write_text(
            svg_de_carilla(carilla, boceto=True, pagina=pagina_boceto.get(carilla.tipo, 1)),
            encoding="utf-8",
        )
        escritos.append(destino)
    return escritos


def comprobar_geometria():
    """El aviso respeta el hueco del número y no achica la letra."""
    assert abs(x_rotulo(1) - 32.4) < 1e-6
    assert abs(x_rotulo(24) - 44) < 1e-6
    assert n(y_renglon(1)) == "54.333"
    assert n(y_renglon(24)) == "200"
    ancho_fecha = max(
        REGULAR.ancho("sáb", 3.4, 0.45),
        REGULAR.ancho("may", 3.4, 0.45),
    )
    derecha = 32.4 + ancho_fecha
    trabajador = "Día del Trabajador"
    assert partir_mensaje(trabajador, disponible_aviso(derecha)) == (trabajador,)
    ancho = ESTRELLA + HUECO_ESTRELLA + REGULAR.ancho(trabajador, TAMANO_AVISO)
    x = x_aviso(derecha, ancho)
    assert abs((x - derecha) - (SIGNO_X - (x + ancho))) < 1e-6
    assert x - derecha > HUECO_NUMERO
    guemes = "Paso a la Inmortalidad del Gral. Don Martín Miguel de Güemes"
    ancho_jun = max(REGULAR.ancho("lun", 3.4, 0.45), REGULAR.ancho("jun", 3.4, 0.45))
    derecha = x_rotulo(21) + ancho_jun
    disponible = disponible_aviso(derecha)
    lineas = partir_mensaje(guemes, disponible)
    assert len(lineas) == 2
    assert all(REGULAR.ancho(linea, TAMANO_AVISO) <= disponible for linea in lineas)
    ancho = ESTRELLA + HUECO_ESTRELLA + max(
        REGULAR.ancho(linea, TAMANO_AVISO) for linea in lineas
    )
    x = x_aviso(derecha, ancho)
    assert abs((x - derecha) - (SIGNO_X - (x + ancho))) < 1e-6
    assert x - derecha + 1e-9 >= HUECO_NUMERO
    from .calendario import DIAS_CORTOS, MESES_CORTOS, cargar_mensajes

    for fecha, lista in cargar_mensajes().items():
        der = x_rotulo(fecha.day) + max(
            REGULAR.ancho(DIAS_CORTOS[fecha.weekday()], 3.4, 0.45),
            REGULAR.ancho(MESES_CORTOS[fecha.month - 1], 3.4, 0.45),
        )
        cupo = disponible_aviso(der)
        lineas_dia = []
        for mensaje in lista:
            lineas_dia.extend(partir_mensaje(mensaje, cupo))
        ancho_dia = ESTRELLA + HUECO_ESTRELLA + max(
            REGULAR.ancho(linea, TAMANO_AVISO) for linea in lineas_dia
        )
        origen = x_aviso(der, ancho_dia)
        assert abs((origen - der) - (SIGNO_X - (origen + ancho_dia))) < 1e-6
        assert origen - der + 1e-6 >= HUECO_NUMERO
    assert PASO_ENTRE == HUECO_NUMERO
    assert PASO_MISMO < PASO_ENTRE
    for mes, corto, nombre in zip(
        range(1, 13),
        ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"),
        (
            "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
            "agosto", "septiembre", "octubre", "noviembre", "diciembre",
        ),
    ):
        portada = carilla_portada(2027, mes, nombre, nombre)
        assert f'font-size="{n(TAMANO_PORTADA)}" font-weight="300">{corto}</text>' in portada
        linea = 102 + TAMANO_PORTADA * 0.30 + 8
        assert f'y="{n(linea)}" fill="{GRIS}" text-anchor="end" font-family="Lato" font-size="{n(TAMANO_PORTADA_SECUNDARIO)}" letter-spacing="{n(INTERLETRADO_PORTADA)}">{nombre}</text>' in portada
        assert f'y="{n(102 + TAMANO_PORTADA * 0.30 + 8)}" fill="{GRIS}" text-anchor="end" font-family="Lato" font-size="{n(TAMANO_PORTADA_SECUNDARIO)}" letter-spacing="{n(INTERLETRADO_PORTADA)}">2027</text>' in portada
        assert portada.index(f">{nombre}</text>") < portada.index(">2027</text>")
        assert portada.count('font-size="36"') == 1
    from .calendario import carillas_del_mes

    carillas = carillas_del_mes(2027, 6)
    desplazamiento = n(MARGEN - MARGEN_ANILLADO)
    for indice, carilla in enumerate(carillas, start=1):
        svg = svg_de_carilla(carilla, pagina=indice)
        if indice % 2 == 0:
            assert f'transform="translate({desplazamiento}, 0)"' in svg
        else:
            assert "lado-izquierdo" not in svg
        if carilla.tipo in ("dia", "finde"):
            numeros = re.findall(r'id="[^"]*numero" ([^>]*)>', svg)
            lunas = re.findall(r'id="[^"]*fase-lunar" x="([^"]+)"', svg)
            signos = re.findall(r'id="[^"]*signo" x="([^"]+)"', svg)
            assert numeros and lunas and signos
            assert 'x1="26.16"' in svg
            if indice % 2 == 1:
                assert all('x="138.5"' in attrs and 'text-anchor="end"' in attrs for attrs in numeros)
                assert set(lunas) == {n(x_espejo(LUNA_X + LUNA_LADO))}
                assert set(signos) == {n(x_espejo(SIGNO_X + SIGNO_LADO))}
            else:
                assert all('x="16"' in attrs and "text-anchor" not in attrs for attrs in numeros)
                assert set(lunas) == {n(LUNA_X)}
                assert set(signos) == {n(SIGNO_X)}
    from datetime import date

    from .calendario import carillas_del_mes as _carillas

    def _planner(anio, mes, lado):
        carilla = next(c for c in _carillas(anio, mes) if c.tipo == lado)
        return svg_de_carilla(carilla, pagina=2 if lado == "planner-izq" else 3)

    ancho_col = (BORDE_DER - MARGEN_ANILLADO) / 3
    alto_fila = (Y_PLANNER_1 - Y_PLANNER_0) / FILAS_PLANNER
    junio_der = _planner(2027, 6, "planner-der")
    x_sab = MARGEN_ANILLADO + 2 * ancho_col + PAD_CELDA
    assert f'x="{n(x_sab)}" y="{n(Y_PLANNER_0 + Y_CIFRA)}"' in junio_der
    y_dom = Y_PLANNER_0 + alto_fila - PAD_CIFRA
    assert f'x="{n(BORDE_DER - PAD_CELDA)}" y="{n(y_dom)}" text-anchor="end"' in junio_der
    assert ">6</text>" in junio_der
    y_20 = Y_PLANNER_0 + 3 * alto_fila - PAD_CIFRA
    assert f'x="{n(BORDE_DER - PAD_CELDA)}" y="{n(y_20)}" text-anchor="end"' in junio_der
    assert ">20</text>" in junio_der
    cifras = LIGHT.ancho("20", TAMANO_CELDA)
    x_estrella = BORDE_DER - PAD_CELDA - cifras - HUECO_ESTRELLA_CELDA - LADO_ESTRELLA_CELDA
    assert f'x="{n(x_estrella)}" y="{n(y_20 - DY_ESTRELLA_CELDA)}"' in junio_der
    assert date(2027, 5, 1).weekday() == 5
    mayo_izq = _planner(2027, 5, "planner-izq")
    y_24 = Y_PLANNER_0 + 4 * alto_fila + Y_CIFRA
    assert f'x="{n(MARGEN_ANILLADO + PAD_CELDA)}" y="{n(y_24)}"' in mayo_izq
    x_31 = MARGEN_ANILLADO + ancho_col - PAD_CELDA
    y_31 = Y_PLANNER_0 + 5 * alto_fila - PAD_CIFRA
    assert f'x="{n(x_31)}" y="{n(y_31)}" text-anchor="end"' in mayo_izq
    assert ">31</text>" in mayo_izq
