"""Descarga una muestra NIH ChestX-ray14 y evalúa TrIA (solo investigación).

NO válida diagnóstico, sensibilidad clínica ni generalización externa.
Fuentes: NIH Clinical Center, etiquetas NLP de Data_Entry_2017_v2020.csv.
No incorpora imágenes, datos personales ni artefactos de terceros al repositorio.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests
from PIL import Image

DATASET = "NIH ChestX-ray14"
METADATA_URLS = (
    "https://huggingface.co/datasets/alkzar90/NIH-Chest-X-ray-dataset/resolve/main/data/Data_Entry_2017_v2020.csv",
    "https://raw.githubusercontent.com/gregwchase/nih-chest-xray/master/data/Data_Entry_2017.csv",
)
TEST_LIST_URL = "https://huggingface.co/datasets/alkzar90/NIH-Chest-X-ray-dataset/resolve/main/data/test_list.txt"
# Copia pública descrita en un trabajo de investigación. No es el servidor NIH.
IMAGE_MIRROR_URLS = (
    "https://nih-chest-x-rays.s3.us-east-2.amazonaws.com/images_1024x1024/",
    "https://nih-chest-x-rays.s3.us-east-2.amazonaws.com/images_224x224/",
)
GROUPS = ("Pneumothorax", "Effusion", "Consolidation", "No Finding")
TARGETS = GROUPS[:-1]
ATTRIBUTION = {
    "dataset": DATASET,
    "owner": "NIH Clinical Center",
    "original": "https://nihcc.app.box.com/v/ChestXray-NIHCC",
    "reference": "Wang et al., ChestX-ray8, CVPR 2017, doi:10.1109/CVPR.2017.369",
    "mirror": "Public NIH image copy maintained by third-party researchers (unverified original hashes)",
    "label_limitations": "Etiquetas extraídas por NLP de informes; no adjudicadas por radiólogos para esta muestra.",
    "model_limitations": "El modelo NIH fue entrenado en el dominio NIH; NO es validación independiente ni clínica.",
}


def get_bytes(url: str, *, max_bytes: int = 20_000_000) -> bytes:
    with requests.get(url, timeout=(12, 80), stream=True, headers={"User-Agent": "TrIA-NF3-educational/1.0"}) as r:
        r.raise_for_status()
        data = bytearray()
        for block in r.iter_content(256 * 1024):
            data.extend(block)
            if len(data) > max_bytes:
                raise ValueError(f"Archivo remoto demasiado grande: {url}")
        return bytes(data)


def read_label_table(text: str):
    rows = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    needed = {"Image Index", "Finding Labels", "Patient ID"}
    if not needed.issubset(set(rows.fieldnames or [])):
        raise ValueError(f"CSV NIH sin columnas {needed}, encontrado {rows.fieldnames}")
    return [r for r in rows if r.get("Image Index", "").endswith(".png")]


def select_samples(rows, test_names, per_group: int = 5):
    """Una imagen por paciente, únicamente positivos de etiqueta única.

    No representativa: selecciona por nombre de archivo y equilibra clases adrede.
    """
    if per_group < 1 or per_group > 20:
        raise ValueError("per_group debe estar entre 1 y 20")
    selected, used = [], set()
    for group in GROUPS:
        candidates = sorted(
            (r for r in rows if r["Image Index"] in test_names
             and r["Finding Labels"].strip() == group
             and r.get("Patient ID", "").strip()),
            key=lambda r: r["Image Index"],
        )
        count = 0
        for r in candidates:
            pid = r["Patient ID"].strip()
            if pid in used:
                continue
            used.add(pid)
            selected.append({
                "image_id": r["Image Index"],
                "group": group,
                "labels": [] if group == "No Finding" else [group],
                "view": r.get("View Position", ""),
                "source_split": "nih_official_test_list",
                # No publicar IDs de pacientes; solo verificar unicidad durante selección.
            })
            count += 1
            if count == per_group:
                break
        if count != per_group:
            raise ValueError(f"No hay suficientes pacientes únicos para {group}: {count}/{per_group}")
    return selected


def download_samples(out: Path, per_group: int = 5):
    out.mkdir(parents=True, exist_ok=True)
    (out / "images").mkdir(exist_ok=True)
    metadata_path = out / "Data_Entry_2017_v2020.csv"
    test_path = out / "test_list.txt"
    if metadata_path.is_file():
        content = metadata_path.read_bytes()
        metadata_url = "caché local (original indicado en ATTRIBUTION)"
    else:
        problems = []
        for src in METADATA_URLS:
            try:
                content = get_bytes(src, max_bytes=15_000_000)
                read_label_table(content.decode("utf-8-sig"))
                metadata_path.write_bytes(content)
                metadata_url = src
                break
            except (requests.RequestException, UnicodeDecodeError, ValueError) as exc:
                problems.append(f"{src}: {exc}")
        else:
            raise RuntimeError("No se pudo obtener metadatos NIH: " + "; ".join(problems))
    if test_path.is_file():
        test_data = test_path.read_bytes()
    else:
        test_data = get_bytes(TEST_LIST_URL, max_bytes=1_000_000)
        test_path.write_bytes(test_data)
    test_names = {x.strip() for x in test_data.decode("utf-8-sig").splitlines() if x.strip()}
    rows = read_label_table(content.decode("utf-8-sig"))
    samples = select_samples(rows, test_names, per_group)
    for n, record in enumerate(samples, start=1):
        name = record["image_id"]
        if not name.replace("_", "").replace(".", "").isalnum():
            raise ValueError(f"Nombre de imagen inválido {name!r}")
        dest = out / "images" / name
        if dest.is_file():
            raw = dest.read_bytes()
            source = "caché local (URL indicada en el manifiesto anterior)"
        else:
            errs = []
            for base in IMAGE_MIRROR_URLS:
                source = base + quote(name)
                try:
                    raw = get_bytes(source, max_bytes=7_000_000)
                    with Image.open(io.BytesIO(raw)) as image:
                        image.verify()
                    with Image.open(io.BytesIO(raw)) as image:
                        if image.format != "PNG" or min(image.size) < 224:
                            raise ValueError("Formato PNG o dimensiones inválidos")
                    dest.write_bytes(raw)
                    break
                except (requests.RequestException, OSError, ValueError) as exc:
                    errs.append(f"{source}: {exc}")
            else:
                raise RuntimeError(f"Imagen {name}: no descargada. " + "; ".join(errs))
        with Image.open(dest) as img:
            if img.format != "PNG" or min(img.size) < 224:
                raise ValueError(f"Imagen inválida/corrupta: {dest}")
            dims = list(img.size)
        record.update({"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                       "dimensions": dims, "path": f"images/{name}", "mirror_url": source})
        print(f"[{n:02d}/{len(samples)}] {name} [{record['group']}] {len(raw)} bytes", flush=True)
    manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_metadata_url": metadata_url,
        "metadata_sha256": hashlib.sha256(content).hexdigest(),
        "test_list_sha256": hashlib.sha256(test_data).hexdigest(),
        "per_group": per_group,
        "count": len(samples),
        "attribution": ATTRIBUTION,
        "selection": "solo etiquetas únicas, 1 imagen/paciente, de test_list.txt oficial; primer nombre ordenado por clase",
        "sampling_warning": "Muestra equilibrada y sesgada para smoke; no sirve para reclamar rendimiento clínico.",
        "samples": samples,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"LISTO: {len(samples)} radiografías y manifiesto en {out}", flush=True)
    return manifest


def evaluate_samples(out: Path, *, mode: str = "xrv", limit: int | None = None):
    from fastapi.testclient import TestClient
    from tria.api import create_app
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    samples = manifest["samples"][:limit] if limit else manifest["samples"]
    if not samples:
        raise ValueError("No hay imágenes que evaluar")
    rows = []
    with TestClient(create_app(out / ".tria-local", model_backend=mode)) as client:
        for n, sample in enumerate(samples, 1):
            p = out / sample["path"]
            raw = p.read_bytes()
            if hashlib.sha256(raw).hexdigest() != sample["sha256"]:
                raise RuntimeError(f"SHA256 no coincide: {p}")
            uploaded = client.post("/api/v1/studies", files={"file": (p.name, raw, "image/png")})
            uploaded.raise_for_status()
            study_id = uploaded.json()["id"]
            res = client.post(f"/api/v1/studies/{study_id}/analyses")
            res.raise_for_status()
            prediction = res.json()
            report = client.get(f"/api/v1/analyses/{prediction['id']}/report")
            if report.status_code != 200 or not report.content.startswith(b"%PDF-"):
                raise RuntimeError("Informe PDF inválido")
            heatmap = client.get(f"/api/v1/analyses/{prediction['id']}/heatmap")
            scores = prediction.get("scores", {})
            if mode == "xrv" and (prediction["status"] != "EXPLORATORIO" or set(scores) != set(TARGETS)):
                raise RuntimeError(f"Sin inferencia xrv real: {prediction}")
            row = {"image_id": sample["image_id"], "reference_label": sample["group"],
                   "sha256": sample["sha256"], "model_version": prediction["model_version"],
                   "status": prediction["status"], "indicator": prediction["indicator"],
                   "gradcam_png": heatmap.status_code == 200 and heatmap.content.startswith(b"\x89PNG"),
                   "pdf": True,
                   **{name: scores.get(name, "") for name in TARGETS}}
            rows.append(row)
            print(f"[{n:02d}/{len(samples)}] {sample['group']}: " + ", ".join(f"{k}={scores.get(k, 'N/A')}" for k in TARGETS), flush=True)
    with (out / "resultados_nih.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    stats = {}
    for target in TARGETS:
        pos = [float(r[target]) for r in rows if r["reference_label"] == target and isinstance(r[target], (float, int))]
        other = [float(r[target]) for r in rows if r["reference_label"] != target and isinstance(r[target], (float, int))]
        stats[target] = {"n_pos": len(pos), "n_other": len(other),
                         "mean_pos": round(statistics.mean(pos), 6) if pos else None,
                         "mean_other": round(statistics.mean(other), 6) if other else None}
    summary = {"status": "technical_smoke_only", "n": len(rows), "mode": mode,
               "all_pdf": all(r["pdf"] for r in rows),
               "gradcam_generated": sum(bool(r["gradcam_png"]) for r in rows),
               "stats_descriptive_only": stats,
               "warning": "NIH was used to train the pretrained model; NOT independent, clinical or representative validation. 'No Finding' is not clinical normality. Scores are not calibrated probabilities.",
               "sources": ATTRIBUTION}
    (out / "resumen_nih.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main():
    ap = argparse.ArgumentParser(description="RadioTriaje-AI: prueba NIH no clínica, trazable")
    ap.add_argument("action", choices=["download", "evaluate", "all"])
    ap.add_argument("--output", type=Path, default=Path("data/validacion_nih"))
    ap.add_argument("--per-group", type=int, default=5)
    ap.add_argument("--mode", choices=["demo", "xrv"], default="xrv")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    if args.action in ("download", "all"):
        download_samples(args.output, args.per_group)
    if args.action in ("evaluate", "all"):
        evaluate_samples(args.output, mode=args.mode, limit=args.limit)


if __name__ == "__main__":
    main()
