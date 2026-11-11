"""Informe académico visual, trazable y explícitamente NO CLÍNICO.

La imagen de la página 1 es una VISTA NORMALIZADA (no el fichero original);
el SHA-256 de la página 2 corresponde a los bytes originales aportados.
Se evita afirmar procedencia, validación médica o versión del código desconocidas.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

NAVY = colors.HexColor('#152B43')
INK = colors.HexColor('#20364E')
MUTED = colors.HexColor('#50667B')
TEAL = colors.HexColor('#067D86')
BORDER = colors.HexColor('#DFE6ED')
PALE = colors.HexColor('#F3F7FA')
ORANGE = colors.HexColor('#B86425')
WARNING = colors.HexColor('#FFF3E7')
WHITE = colors.white
MARGIN = 36


def _fonts() -> tuple[str, str, str]:
    """Utilizar fuentes locales del SO sin empaquetar archivos de fuentes."""
    candidates = (
        (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
         Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
         Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')),
        (Path('C:/Windows/Fonts/arial.ttf'),
         Path('C:/Windows/Fonts/arialbd.ttf'),
         Path('C:/Windows/Fonts/consola.ttf')),
    )
    for normal, bold, mono in candidates:
        if all(p.is_file() for p in (normal, bold, mono)):
            for name, path in (('TrIA-Regular', normal), ('TrIA-Bold', bold), ('TrIA-Mono', mono)):
                if name not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont(name, str(path)))
            return 'TrIA-Regular', 'TrIA-Bold', 'TrIA-Mono'
    return 'Helvetica', 'Helvetica-Bold', 'Courier'


def _text(c: canvas.Canvas, x: float, y: float, s: str, font: str, size: float,
          color=INK) -> None:
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, str(s))


def _wrap(c: canvas.Canvas, x: float, y: float, value: str, width: float, font: str,
          size: float = 9.0, leading: float = 13.0, color=INK, max_lines: int | None = None) -> float:
    c.setFont(font, size)
    c.setFillColor(color)
    lines = simpleSplit(str(value), font, size, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def _header(c: canvas.Canvas, fonts, number: int) -> None:
    w, h = A4
    regular, bold, _ = fonts
    c.setFillColor(NAVY)
    c.rect(0, h-85, w, 85, stroke=0, fill=1)
    _text(c, MARGIN, h-39, 'TrIA', bold, 26, WHITE)
    _text(c, MARGIN+83, h-37, 'RadioTriaje-AI | Grupo 8', regular, 10, WHITE)
    _text(c, MARGIN+83, h-55, 'INFORME DE ANÁLISIS', bold, 9, colors.HexColor('#8BDBDE'))
    c.setFillColor(WARNING)
    c.roundRect(MARGIN, h-119, w-2*MARGIN, 24, 5, stroke=0, fill=1)
    _text(c, MARGIN+11, h-111, 'Proyecto académico · No apto para diagnóstico', bold, 8.7, ORANGE)
    c.setStrokeColor(BORDER)
    c.line(MARGIN, 42, w-MARGIN, 42)
    _text(c, MARGIN, 28, 'TrIA · Informe de análisis · Grupo 8', regular, 8, MUTED)
    _text(c, w-MARGIN-47, 28, f'Página {number} / 2', regular, 8, MUTED)


def _image_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, image_bytes: bytes | None,
                title: str, desc: str, fonts) -> None:
    normal, bold, _ = fonts
    c.setFillColor(PALE)
    c.setStrokeColor(BORDER)
    c.roundRect(x, y, w, h, 8, stroke=1, fill=1)
    _text(c, x+12, y+h-22, title, bold, 10.5)
    _wrap(c, x+12, y+h-37, desc, w-24, normal, 7.5, 10, MUTED, max_lines=2)
    image_y, image_h = y+12, h-72
    c.setFillColor(colors.HexColor('#0D1721'))
    c.roundRect(x+12, image_y, w-24, image_h, 4, stroke=0, fill=1)
    if image_bytes:
        try:
            rdr = ImageReader(BytesIO(image_bytes))
            c.drawImage(rdr, x+14, image_y+2, width=w-28, height=image_h-4,
                        preserveAspectRatio=True, anchor='c', mask='auto')
        except Exception:
            _text(c, x+23, image_y + image_h/2, 'Imagen no disponible', normal, 8, WHITE)
    else:
        _text(c, x+23, image_y + image_h/2, 'Visualización no disponible', normal, 8, WHITE)


def _section_title(c, x, y, s, fonts):
    _, bold, _ = fonts
    _text(c, x, y, s, bold, 12.5, NAVY)


def _metadata_line(c, x, y, label, value, fonts, mono=False, long=False):
    normal, bold, fixed = fonts
    _text(c, x, y, label.upper(), bold, 8.2, MUTED)
    if long:
        return _wrap(c, x, y-18, str(value), 514, fixed if mono else normal,
                     9 if mono else 9.5, 13, INK)-9
    _text(c, x, y-18, value or 'No registrado', fixed if mono else normal, 9.5, INK)
    return y-43


def make_pdf(study: dict, analysis: dict, preview_png: bytes | None = None,
             heatmap_png: bytes | None = None, *,
             model_weights_sha256: str | None = None,
             software_commit: str | None = None,
             source_note: str | None = None) -> bytes:
    """Crear un informe A4 de dos páginas sin inventar metadatos ni hallazgos.

    Compatibilidad: los argumentos posicionales study y analysis existentes se mantienen.
    Las imágenes ausentes se señalan explícitamente, nunca se sustituyen por otra.
    """
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=A4, pageCompression=1)
    c.setTitle('TrIA - Informe de análisis')
    c.setAuthor('RadioTriaje-AI / Grupo 8')
    c.setSubject('Informe de análisis y trazabilidad')
    fonts = _fonts()
    normal, bold, mono = fonts
    w, h = A4

    # PÁGINA 1: hallazgos computacionales y figuras de la misma ejecución.
    _header(c, fonts, 1)
    _section_title(c, MARGIN, 690, 'Análisis de imagen', fonts)
    _text(c, MARGIN, 674, f"Estudio: {study.get('id', 'No registrado')}", normal, 8.6, MUTED)
    _text(c, MARGIN, 658, f"Estado: {analysis.get('status', 'No registrado')}", bold, 9, TEAL)

    gap = 14
    card_w = (w - 2*MARGIN - gap)/2
    scores = analysis.get('scores') or {}
    strongest = max(scores, key=scores.get) if scores else None
    _image_card(c, MARGIN, 385, card_w, 254, preview_png,
                'IMAGEN PROCESADA', 'Imagen preparada para el análisis.', fonts)
    _image_card(c, MARGIN+card_w+gap, 385, card_w, 254, heatmap_png,
                'MAPA GRAD-CAM', ('Clase: ' + strongest if strongest and heatmap_png else
                                         'No disponible para esta ejecución.'), fonts)

    _section_title(c, MARGIN, 358, 'Resultados del modelo', fonts)
    _text(c, MARGIN, 340, 'Valores orientativos del modelo; no son probabilidades clínicas calibradas.', normal, 8.1, MUTED)
    if scores:
        display = [('Neumotórax', 'Pneumothorax'), ('Derrame pleural', 'Effusion'),
                   ('Consolidación', 'Consolidation')]
        for idx, (label, key) in enumerate(display):
            y = 311 - idx*34
            value = scores.get(key)
            if value is None:
                _text(c, MARGIN+6, y, label, normal, 9.5)
                _text(c, w-MARGIN-54, y, 'Sin dato', normal, 9, MUTED)
                continue
            value = max(0.0, min(1.0, float(value)))
            _text(c, MARGIN+6, y, label, normal, 9.4, INK)
            c.setFillColor(BORDER)
            c.roundRect(210, y-3, 218, 9, 4, fill=1, stroke=0)
            if value > 0:
                c.setFillColor(TEAL)
                c.roundRect(210, y-3, 218*value, 9, min(4, 218*value/2), fill=1, stroke=0)
            _text(c, 443, y, f'{value:.4f}', bold, 9.3, NAVY)
    else:
        _text(c, MARGIN+6, 305, 'Modo de pruebas: estadísticas de imagen, sin inferencia de IA.', normal, 9, MUTED)
        for i, (k, value) in enumerate((analysis.get('features') or {}).items()):
            _text(c, MARGIN+6, 284-i*18, f'{k}: {value}', normal, 9, INK)

    c.setFillColor(PALE)
    c.roundRect(MARGIN, 104, w-2*MARGIN, 82, 7, fill=1, stroke=0)
    _text(c, MARGIN+13, 167, 'Nota de interpretación', bold, 9.5, NAVY)
    note = (analysis.get('message') or 'No hay información adicional.') if analysis.get('status') != 'EXPLORATORIO' else 'El modelo ha generado puntuaciones y, si está disponible, un mapa de activación. No establece prioridad médica.'
    _wrap(c, MARGIN+13, 149, note, w-2*MARGIN-26, normal, 8, 11.5, INK, max_lines=4)
    # Las limitaciones completas se explican en la segunda página.
    _text(c, MARGIN, 72, 'Identificadores, hashes y procedencia en la página siguiente.', normal, 8.3, MUTED)
    c.showPage()

    # PÁGINA 2: trazabilidad, evidencias y limitaciones.
    _header(c, fonts, 2)
    _section_title(c, MARGIN, 690, 'Trazabilidad de la ejecución', fonts)
    y = 660
    fields = [
        ('Estudio / ID técnico', study.get('id', 'No registrado'), True, False),
        ('Análisis / ID técnico', analysis.get('id', 'No registrado'), True, False),
        ('SHA-256 del archivo de entrada ORIGINAL (64 caracteres)', study.get('sha256', 'No registrado'), True, True),
        ('Formato y resolución', f"{study.get('source_format', '?')} · {study.get('width', '?')} × {study.get('height', '?')} px", False, False),
        ('Fecha de ejecución (UTC)', analysis.get('created_at', 'No registrado'), False, False),
        ('Modo y versión del modelo', f"{analysis.get('mode', '?')} · {analysis.get('model_version', '?')}", False, True),
        ('SHA-256 de los pesos del modelo', model_weights_sha256 or 'No registrado para esta ejecución', True, True),
        ('Commit del software', software_commit or 'No registrado para esta ejecución', True, False),
        ('Origen declarado de la imagen', source_note or 'No vinculado a un dataset en este informe', False, True),
    ]
    for label, value, usemono, long in fields:
        y = _metadata_line(c, MARGIN+3, y, label, str(value), fonts, usemono, long)
    y = min(y, 229)
    c.setFillColor(WARNING)
    c.roundRect(MARGIN, 101, w-2*MARGIN, 153, 8, stroke=0, fill=1)
    _text(c, MARGIN+13, 232, 'Límites del análisis', bold, 9.2, ORANGE)
    limitations = [
        'El modelo no está validado para diagnóstico ni para establecer urgencia médica.',
        'Grad-CAM muestra activaciones de la red, no lesiones confirmadas.',
        'El hash corresponde al archivo original; se conserva una versión normalizada.',
        'No se verifica toda posible información identificativa incrustada en la imagen.',
    ]
    cy = 210
    for line in limitations:
        cy = _wrap(c, MARGIN+13, cy, '- ' + line, w-2*MARGIN-26, normal, 7.7, 11.5, INK)
        cy -= 4
    _text(c, MARGIN, 76, 'Modelo: TorchXRayVision (Cohen y cols.) · Código: RadioTriaje-AI', normal, 8, MUTED)
    _text(c, MARGIN, 63, 'La integridad puede comprobarse comparando el SHA-256 del archivo de origen.', normal, 7.7, MUTED)
    c.save()
    return output.getvalue()
