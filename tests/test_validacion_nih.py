"""No necesita descargar imágenes reales para ejecutar estas pruebas."""
import importlib.util
from pathlib import Path

import pytest

script = Path(__file__).resolve().parents[1] / "scripts" / "validacion_nih.py"
spec = importlib.util.spec_from_file_location("validacion_nih", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fake_rows():
    rows = []
    for i, group in enumerate(mod.GROUPS):
        for n in range(1, 12):
            pid = str(i * 100 + n)
            rows.append({"Image Index": f"{i:08d}_{n:03d}.png", "Finding Labels": group,
                         "Patient ID": pid, "View Position": "PA"})
    return rows


def test_20_different_patients_four_groups():
    rows = fake_rows()
    selected = mod.select_samples(rows, {x["Image Index"] for x in rows}, 5)
    assert len(selected) == 20
    assert all(sum(x["group"] == group for x in selected) == 5 for group in mod.GROUPS)
    assert not any("Patient" in field for row in selected for field in row)
    assert all(x["source_split"] == "nih_official_test_list" for x in selected)
    assert not any(x["labels"] for x in selected if x["group"] == "No Finding")


def test_requires_official_test_list():
    rows = fake_rows()
    with pytest.raises(ValueError, match="No hay suficientes"):
        mod.select_samples(rows, {x["Image Index"] for x in rows[:6]}, 5)


def test_csv_must_have_ground_truth_columns():
    with pytest.raises(ValueError, match="sin columnas"):
        mod.read_label_table("image,label\ntest.png,Pneumothorax\n")


def test_multilabel_not_misrepresented_as_single_positive():
    rows = fake_rows()
    rows[0]["Finding Labels"] = "Pneumothorax|Effusion"
    selected = mod.select_samples(rows, {x["Image Index"] for x in rows}, 5)
    assert rows[0]["Image Index"] not in {x["image_id"] for x in selected}
