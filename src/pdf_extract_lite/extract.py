"""Section extract via pdftotext. Probe returns counts, not page text."""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

NUM = r"[-+]?\d{1,3}(?:[’'`´‘]\d{3})*(?:[.,]\d+)?|[-+]?\d+(?:[.,]\d+)?"
MONTHS = {
    "jan": 1, "januar": 1, "january": 1, "feb": 2, "februar": 2, "february": 2,
    "mar": 3, "maerz": 3, "marz": 3, "march": 3, "apr": 4, "april": 4,
    "mai": 5, "may": 5, "jun": 6, "juni": 6, "june": 6, "jul": 7, "juli": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "okt": 10, "oct": 10, "oktober": 10, "october": 10,
    "nov": 11, "november": 11, "dez": 12, "dec": 12, "dezember": 12, "december": 12,
}


def pdftotext_pages(path: Path) -> list[str]:
    proc = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return [page for page in proc.stdout.split("\f") if page.strip()]


def section_pages(pages: list[str], config: dict) -> list[int]:
    markers = [m.lower() for m in config["extract"].get("section_markers") or []]
    ends = [m.lower() for m in config["extract"].get("section_end_markers") or []]
    hits = []
    for index, page in enumerate(pages):
        low = page.lower()
        if markers and not any(marker in low for marker in markers):
            continue
        if ends and any(marker in low for marker in ends) and not any(marker in low for marker in markers):
            continue
        hits.append(index)
    return hits


def probe_file(path: Path, config: dict) -> dict:
    pages = pdftotext_pages(path)
    hits = section_pages(pages, config)
    blob = "\n".join(pages[i] for i in hits)
    present = []
    missing = []
    for series in config["extract"].get("series") or []:
        if re.search(series["label"], blob, re.IGNORECASE):
            present.append(series["id"])
        else:
            missing.append(series["id"])
    return {
        "file": path.name,
        "n_pages": len(pages),
        "section_pages": ",".join(str(i + 1) for i in hits) or "-",
        "n_labels_present": len(present),
        "n_labels_missing": len(missing),
        "missing_ids": ";".join(missing),
    }


def parse_num(raw: str) -> float | None:
    text = raw.strip().replace("−", "-").replace("–", "-")
    if text in {"", "-", "--", "*"}:
        return None
    text = text.replace("+", "")
    for char in ("'", "’", "‘", "`", "´"):
        text = text.replace(char, "")
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def extract_file(path: Path, config: dict, report_year: int | None, report_month: int | None) -> list[dict]:
    pages = pdftotext_pages(path)
    hits = section_pages(pages, config)
    blob = "\n".join(pages[i] for i in hits)
    rows = []
    for series in config["extract"].get("series") or []:
        match = re.search(rf"^.*{series['label']}.*$", blob, re.IGNORECASE | re.MULTILINE)
        if not match:
            continue
        numbers = [parse_num(token) for token in re.findall(NUM, match.group(0))]
        numbers = [value for value in numbers if value is not None]
        # Drop a year token that is part of the label, keep the value run.
        values = [value for value in numbers if not (1900 <= value <= 2100 and value == int(value))]
        for position, value in enumerate(values, start=1):
            rows.append({
                "report_year": report_year,
                "report_month": report_month,
                "source_file": path.name,
                "series": series["id"],
                "unit": series.get("unit") or "",
                "position": position,
                "value": value,
                "is_projection": int(position > 12 and series.get("tail_is_projection", True)),
            })
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "report_year", "report_month", "source_file", "series",
        "unit", "position", "value", "is_projection",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
