"""Carga defensiva de imágenes de DEMOSTRACIÓN, sin identidad clínica."""
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import hashlib

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PIXELS = 16_000_000
MIN_SIDE = 32


class ImageRejected(ValueError):
    """Entrada fuera del contrato público de la aplicación."""


@dataclass(frozen=True)
class ValidatedImage:
    png: bytes
    sha256: str
    width: int
    height: int
    source_format: str
    warnings: tuple[str, ...]


def _as_gray(data: bytes) -> tuple[Image.Image, str]:
    if len(data) >= 132 and data[128:132] == b'DICM':
        try:
            import pydicom
        except ImportError as exc:
            raise ImageRejected('DICOM no disponible: instalar pydicom') from exc
        try:
            ds = pydicom.dcmread(BytesIO(data))
            for tag in ('PatientName', 'PatientID', 'PatientBirthDate', 'AccessionNumber', 'InstitutionName'):
                if str(getattr(ds, tag, '')).strip():
                    raise ImageRejected('DICOM con metadatos identificativos: utilizar archivo de prueba desidentificado')
            if str(getattr(ds, 'Modality', '')).upper() not in ('CR', 'DX'):
                raise ImageRejected('Solo se admiten radiografías DICOM de modalidad CR/DX')
            if int(getattr(ds, 'NumberOfFrames', 1)) != 1:
                raise ImageRejected('DICOM multiframe no admitido')
            pixels = np.asarray(ds.pixel_array)
            if pixels.ndim != 2:
                raise ImageRejected('DICOM no monocromático: formato no admitido')
            if pixels.size > MAX_PIXELS:
                raise ImageRejected('Dimensiones de imagen excesivas')
            pixels = pixels.astype('float32')
            low, high = np.percentile(pixels, [1, 99])
            if high <= low:
                raise ImageRejected('DICOM sin contraste útil')
            pixels = np.clip((pixels - low) / (high - low) * 255, 0, 255).astype('uint8')
            if getattr(ds, 'PhotometricInterpretation', '') == 'MONOCHROME1':
                pixels = 255 - pixels
            return Image.fromarray(pixels, 'L'), 'DICOM'
        except ImageRejected:
            raise
        except Exception as exc:
            raise ImageRejected('DICOM corrupto o codificación de píxeles no disponible') from exc
    try:
        with Image.open(BytesIO(data)) as img:
            if img.format not in ('PNG', 'JPEG'):
                raise ImageRejected('Formato no admitido; use PNG, JPG o DICOM')
            if img.width * img.height > MAX_PIXELS:
                raise ImageRejected('Dimensiones de imagen excesivas')
            return ImageOps.exif_transpose(img).convert('L'), img.format
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ImageRejected('Archivo corrupto o formato no admitido') from exc


def validate_image(data: bytes, max_bytes: int) -> ValidatedImage:
    if not data or len(data) > max_bytes:
        raise ImageRejected('Archivo vacío o superior al límite permitido')
    image, source_format = _as_gray(data)
    if min(image.size) < MIN_SIDE:
        raise ImageRejected('Resolución insuficiente (mínimo 32 px por lado)')
    output = BytesIO()
    image.save(output, format='PNG')
    return ValidatedImage(
        png=output.getvalue(), sha256=hashlib.sha256(data).hexdigest(),
        width=image.width, height=image.height, source_format=source_format,
        warnings=('No usar datos de pacientes ni material asistencial.',
                  'El sistema no detecta datos identificativos incrustados en píxeles.'),
    )
