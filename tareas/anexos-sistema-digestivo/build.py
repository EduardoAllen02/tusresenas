#!/usr/bin/env python3
"""Arma los anexos: inserta estilos e ilustraciones SVG en cada plantilla de
`fuente/` (los HTML quedan autocontenidos) y, con --pdf, los imprime a PDF
con Chrome/Chromium.

    python3 build.py          # solo HTML
    python3 build.py --pdf    # HTML + PDF (usa CHROME=/ruta/a/chrome si no está en el PATH)
"""
import os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FUENTE, SVG = ROOT / "fuente", ROOT / "svg"
ANEXOS = ["anexo-relaciona-partes", "anexo-17", "anexo-26"]


def svg_inline(nombre, clase=""):
    s = (SVG / f"{nombre}.svg").read_text(encoding="utf-8")
    s = re.sub(r"^<\?xml.*?\?>\s*", "", s).strip()
    if clase:
        s = s.replace("<svg ", f'<svg class="{clase}" ', 1)
    return s


def armar(nombre):
    html = (FUENTE / f"{nombre}.html").read_text(encoding="utf-8")
    html = html.replace("{{css}}", (FUENTE / "estilos.css").read_text(encoding="utf-8"))
    html = html.replace("{{logo}}", (FUENTE / "logo.svg").read_text(encoding="utf-8").strip())
    html = re.sub(r"\{\{svg:([\w-]+)(?:\|([\w -]+))?\}\}", lambda m: svg_inline(m[1], m[2] or ""), html)
    destino = ROOT / f"{nombre}.html"
    destino.write_text(html, encoding="utf-8")
    return destino


def chrome():
    for c in (os.environ.get("CHROME"), shutil.which("chromium"), shutil.which("google-chrome"),
              shutil.which("chrome"), "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"):
        if c and Path(c).exists():
            return c
    sys.exit("No encontré Chrome/Chromium: define CHROME=/ruta/a/chrome")


def a_pdf(html):
    pdf = html.with_suffix(".pdf")
    subprocess.run([chrome(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", f"file://{html}"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return pdf


if __name__ == "__main__":
    pdfs = []
    for n in ANEXOS:
        h = armar(n)
        print("HTML", h.name)
        if "--pdf" in sys.argv:
            pdfs.append(a_pdf(h))
            print("PDF ", pdfs[-1].name)
    if pdfs:
        from pypdf import PdfWriter
        w = PdfWriter()
        for p in pdfs:
            w.append(str(p))
        w.write(str(ROOT / "todos-los-anexos.pdf"))
        print("PDF  todos-los-anexos.pdf")
