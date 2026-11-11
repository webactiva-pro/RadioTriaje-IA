"""Produce un patrón geométrico artificial sin imágenes de personas."""
from pathlib import Path
from PIL import Image, ImageDraw

path = Path(__file__).resolve().parents[1] / 'data' / 'demo_geometrico.png'
path.parent.mkdir(parents=True, exist_ok=True)
image = Image.new('L', (448, 448), 28)
draw = ImageDraw.Draw(image)
draw.ellipse((70, 50, 240, 390), fill=130)
draw.ellipse((210, 50, 380, 390), fill=155)
draw.rectangle((209, 60, 236, 360), fill=210)
draw.ellipse((110, 210, 155, 250), fill=235)
image.save(path)
print('Imagen sintética de prueba, no radiografía:', path)
