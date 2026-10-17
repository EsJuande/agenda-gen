"""Anchos de Lato, para colocar el número, el aviso y el signo."""

import struct
from pathlib import Path

LATO_LIGHT = Path("/usr/share/fonts/truetype/lato/Lato-Light.ttf")
LATO_REGULAR = Path("/usr/share/fonts/truetype/lato/Lato-Regular.ttf")


class Fuente:
    def __init__(self, ruta):
        datos = Path(ruta).read_bytes()
        tablas = _tablas(datos)
        self.upem = struct.unpack_from(">H", tablas["head"], 18)[0]
        metricas = struct.unpack_from(">H", tablas["hhea"], 34)[0]
        hmtx = tablas["hmtx"]
        self.avances = [
            struct.unpack_from(">H", hmtx, i * 4)[0] for i in range(metricas)
        ]
        self.glifos = _cmap(tablas["cmap"])

    def ancho(self, texto, tamano, interletrado=0):
        total = 0
        ultimo = self.avances[-1]
        for caracter in texto:
            glifo = self.glifos.get(ord(caracter), 0)
            avance = self.avances[glifo] if glifo < len(self.avances) else ultimo
            total += avance
        extra = interletrado * max(0, len(texto) - 1)
        return total / self.upem * tamano + extra


def _tablas(datos):
    cantidad = struct.unpack_from(">H", datos, 4)[0]
    tablas = {}
    for i in range(cantidad):
        etiqueta, _, inicio, largo = struct.unpack_from(">4sIII", datos, 12 + i * 16)
        tablas[etiqueta.decode()] = datos[inicio : inicio + largo]
    return tablas


def _cmap(cmap):
    subtablas = struct.unpack_from(">H", cmap, 2)[0]
    inicio = None
    for i in range(subtablas):
        plataforma, codificacion, desplazamiento = struct.unpack_from(
            ">HHI", cmap, 4 + i * 8
        )
        formato = struct.unpack_from(">H", cmap, desplazamiento)[0]
        if plataforma == 3 and codificacion == 1 and formato == 4:
            inicio = desplazamiento
            break
    if inicio is None:
        raise RuntimeError("La fuente no tiene cmap Unicode de formato 4.")

    segmentos = struct.unpack_from(">H", cmap, inicio + 6)[0] // 2
    fin = list(struct.unpack_from(f">{segmentos}H", cmap, inicio + 14))
    empieza = list(
        struct.unpack_from(f">{segmentos}H", cmap, inicio + 16 + segmentos * 2)
    )
    delta = list(
        struct.unpack_from(f">{segmentos}h", cmap, inicio + 16 + segmentos * 4)
    )
    rango_pos = inicio + 16 + segmentos * 6
    rango = list(struct.unpack_from(f">{segmentos}H", cmap, rango_pos))
    glifos = {}
    for i in range(segmentos):
        if empieza[i] == 0xFFFF:
            continue
        for codigo in range(empieza[i], fin[i] + 1):
            if rango[i] == 0:
                glifo = (codigo + delta[i]) & 0xFFFF
            else:
                pos = rango_pos + i * 2 + rango[i] + (codigo - empieza[i]) * 2
                glifo = struct.unpack_from(">H", cmap, pos)[0]
                glifo = (glifo + delta[i]) & 0xFFFF if glifo else 0
            glifos[codigo] = glifo
    return glifos


LIGHT = Fuente(LATO_LIGHT)
REGULAR = Fuente(LATO_REGULAR)
