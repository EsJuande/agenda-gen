"""Genera las carillas de un mes, o las primeras páginas, y el PDF.

    python -m agenda junio
    python -m agenda primeras
"""

import sys

from .calendario import ANIO, MESES, RAIZ, carillas_del_mes, carillas_iniciales, comprobar
from .dibujar import comprobar_geometria, escribir_bocetos, svg_de_carilla
from .exportar import pdf_de_svgs


def _mes(texto):
    texto = texto.strip().lower()
    if texto in ("primeras", "inicio"):
        return texto
    if texto.isdigit() and 1 <= int(texto) <= 12:
        return int(texto)
    if texto in MESES:
        return MESES.index(texto) + 1
    raise SystemExit(
        "No reconozco el argumento. Usá un mes, por ejemplo junio, o primeras."
    )


def _escribir(carillas, carpeta, pdf):
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
    print("Armando el PDF…")
    pdf_de_svgs(rutas, pdf)
    print(f"{len(carillas)} carillas")
    print(f"PDF  {pdf.relative_to(RAIZ)}")
    print(f"SVG  {carpeta.relative_to(RAIZ)}/")
    for boceto in bocetos:
        print(f"Boceto  {boceto.relative_to(RAIZ)}")


def main(argv):
    if len(argv) != 2:
        raise SystemExit("Uso: python -m agenda junio   o   python -m agenda primeras")
    mes = _mes(argv[1])
    if mes in ("primeras", "inicio"):
        comprobar()
        comprobar_geometria()
        carillas = carillas_iniciales(ANIO)
        _escribir(carillas, RAIZ / "output" / f"{ANIO}-primeras", RAIZ / "output" / f"primeras-{ANIO}.pdf")
        return 0
    comprobar()
    comprobar_geometria()
    carillas = carillas_del_mes(ANIO, mes)
    _escribir(
        carillas,
        RAIZ / "output" / f"{ANIO}-{mes:02d}",
        RAIZ / "output" / f"{MESES[mes - 1]}-{ANIO}.pdf",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
