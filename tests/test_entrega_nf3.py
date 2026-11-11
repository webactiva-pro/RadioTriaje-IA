"""Comprobaciones de integridad de la muestra y de la guía académica NF3.

No accede a Internet, no prueba exactitud clínica y no necesita PyTorch.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "NF3_NIH_20_MANIFEST.json"
CSV = ROOT / "docs" / "NF3_NIH_20_RESULTADOS.csv"
PUBLIC_IMAGES = ROOT / "examples" / "nih" / "radiografias"


def test_public_nih_png_count_and_sha256_match_manifest():
    samples = json.loads(MANIFEST.read_text(encoding="utf-8"))["samples"]
    assert len(samples) == 20
    ids = [row["image_id"] for row in samples]
    assert len(ids) == len(set(ids))
    assert Counter(row["group"] for row in samples) == {
        "Pneumothorax": 5, "Effusion": 5,
        "Consolidation": 5, "No Finding": 5,
    }
    assert {p.name for p in PUBLIC_IMAGES.glob("*.png")} == set(ids)
    for row in samples:
        image = PUBLIC_IMAGES / row["image_id"]
        payload = image.read_bytes()
        assert len(payload) == row["bytes"], row["image_id"]
        assert hashlib.sha256(payload).hexdigest() == row["sha256"], row["image_id"]


def test_public_nih_csv_consistent_with_manifest_and_exploratory_scope():
    samples = json.loads(MANIFEST.read_text(encoding="utf-8"))["samples"]
    lookup = {row["image_id"]: row for row in samples}
    with CSV.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 20
    assert {row["image_id"] for row in rows} == set(lookup)
    for row in rows:
        manifest = lookup[row["image_id"]]
        assert row["sha256"] == manifest["sha256"]
        assert row["reference_label"] == manifest["group"]
        assert row["indicator"] == "SIN_RESULTADO"
        assert row["status"] == "EXPLORATORIO"
        assert row["gradcam_png"] == "True"
        assert row["pdf"] == "True"
        for target in ("Pneumothorax", "Effusion", "Consolidation"):
            assert 0.0 <= float(row[target]) <= 1.0


def test_delivery_guide_links_and_checksum_command_are_legible():
    guide = (ROOT / "docs" / "05_EJECUCION_Y_VERIFICACION.md").read_text(encoding="utf-8")
    status = (ROOT / "docs" / "NF3_ESTADO_IMPLEMENTACION.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "\x00" not in guide
    assert r".\examples\nih\radiografias\00000193_000.png" in guide
    assert "92664c9056ba1e4f3ca1cbcfc7be99c312fa597e27875d3fbdef83d53d2606fe" in guide
    assert "fase2_grupo8.pdf" in guide and "fase2_grupo8.pdf" in readme
    assert "NF3_EVIDENCIAS_Y_REPRODUCIBILIDAD.md" not in status
    assert "20 radiografías NIH desidentificadas" in status
