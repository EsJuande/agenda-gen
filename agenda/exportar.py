"""Junta las carillas SVG en un PDF A5, una página por carilla."""

import subprocess
from pathlib import Path


def pdf_de_svgs(svgs, destino):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.parent / f".{destino.stem}-paginas"
    temporal.mkdir(parents=True, exist_ok=True)
    pdfs = []
    acciones = []
    for svg in svgs:
        pdf = temporal / f"{svg.stem}.pdf"
        pdfs.append(pdf)
        acciones.append(
            f"file-open:{svg}; export-filename:{pdf}; export-do; file-close"
        )
    acciones.append("quit")
    proceso = subprocess.run(
        ["inkscape", "--shell"],
        input="\n".join(acciones) + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    faltan = [pdf for pdf in pdfs if not pdf.exists() or pdf.stat().st_size == 0]
    if faltan:
        detalle = (proceso.stderr or proceso.stdout or "").strip()
        raise RuntimeError(
            "Inkscape no pudo armar el PDF.\n"
            + "\n".join(pdf.name for pdf in faltan[:8])
            + (f"\n{detalle[-2000:]}" if detalle else "")
        )
    unido = temporal / "unido.pdf"
    subprocess.run(["pdfunite", *[str(pdf) for pdf in pdfs], str(unido)], check=True)
    # pdfunite deja el índice del archivo mal formado. Ghostscript lo reescribe.
    subprocess.run(
        [
            "gs",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.5",
            f"-sOutputFile={destino}",
            str(unido),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    for pdf in pdfs:
        pdf.unlink()
    unido.unlink()
    temporal.rmdir()
    return destino
