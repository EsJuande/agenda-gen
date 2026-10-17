"""Genera las carillas de un mes y el PDF.

    python -m agenda junio
"""

import sys

from .calendario import ANIO, MESES, carillas_del_mes, comprobar
from .dibujar import comprobar_geometria, escribir_bocetos, svg_de_carilla
from .exportar import pdf_de_svgs
from .calendario import RAIZ


def _mes(texto):
    texto = texto.strip().lower()
    if texto.isdigit() and 1 <= int(texto) <= 12:
        return int(texto)
    if texto in MESES:
        return MESES.index(texto) + 1
    raise SystemExit(
        f"No reconozco el mes {texto!r}. Usá el nombre, por ejemplo junio, o un número del 1 al 12."
    )


def main(argv):
    if len(argv) != 2:
        raise SystemExit("Uso: python -m agenda junio")
    mes = _mes(argv[1])
    comprobar()
    comprobar_geometria()
    carillas = carillas_del_mes(ANIO, mes)
    carpeta = RAIZ / "output" / f"{ANIO}-{mes:02d}"
    carpeta.mkdir(parents=True, exist_ok=True)
    for viejo in carpeta.glob("*.svg"):
        viejo.unlink()
    rutas = []
    for indice, carilla in enumerate(carillas, start=1):
        ruta = carpeta / carilla.archivo(indice)
        ruta.write_text(svg_de_carilla(carilla, pagina=indice), encoding="utf-8")
        rutas.append(ruta)
        print(f"{indice:02d}  {carilla.descripcion()}")
    bocetos = escribir_bocetos(carillas)
    pdf = RAIZ / "output" / f"{MESES[mes - 1]}-{ANIO}.pdf"
    print("Armando el PDF…")
    pdf_de_svgs(rutas, pdf)
    print(f"{len(carillas)} carillas")
    print(f"PDF  {pdf.relative_to(RAIZ)}")
    print(f"SVG  {carpeta.relative_to(RAIZ)}/")
    for boceto in bocetos:
        print(f"Boceto  {boceto.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
