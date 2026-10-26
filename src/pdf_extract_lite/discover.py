"""Find PDF URLs. Returns URLs only — never page or PDF text."""

from __future__ import annotations

import calendar
import re
from pathlib import Path
from urllib.parse import urljoin

import requests

from pdf_extract_lite.download import session_from_config

PDF_HREF = re.compile(r'href=["\']([^"\']+\.pdf)["\']', re.IGNORECASE)
PDF_ABS = re.compile(r"https?://[^\"'\s>]+\.pdf", re.IGNORECASE)


def discover(config: dict, session: requests.Session | None = None) -> list[str]:
    kind = config["source"]["type"]
    if kind == "html_archive":
        return _from_html(config, session or session_from_config(config))
    if kind == "url_template":
        return _from_template(config)
    if kind == "link_list":
        return _from_list(config)
    raise ValueError(f"unknown source.type {kind}")


def _from_html(config: dict, session: requests.Session) -> list[str]:
    source = config["source"]
    page_url = source["page_url"]
    response = session.get(page_url, timeout=config["download"]["timeout_seconds"])
    response.raise_for_status()
    html = response.text
    found = PDF_ABS.findall(html)
    for href in PDF_HREF.findall(html):
        found.append(href if href.startswith("http") else urljoin(page_url, href))
    must = [s.lower() for s in source.get("link_must_contain") or []]
    skip = [s.lower() for s in source.get("link_must_not_contain") or []]
    year_min = int(source.get("year_min") or 0)
    year_max = int(source.get("year_max") or 9999)
    year_re = re.compile(source.get("year_regex") or r"(20\d{2})")
    keep: list[str] = []
    seen: set[str] = set()
    for url in found:
        low = url.lower()
        if any(token not in low for token in must):
            continue
        if any(token in low for token in skip):
            continue
        years = [int(y) for y in year_re.findall(url)]
        if years and not any(year_min <= y <= year_max for y in years):
            continue
        if url not in seen:
            seen.add(url)
            keep.append(url)
    return keep


def _from_template(config: dict) -> list[str]:
    source = config["source"]
    template = source["url_template"]
    months = source.get("months") or list(range(1, 13))
    names = source.get("month_names") or {
        i: calendar.month_name[i].lower() for i in range(1, 13)
    }
    urls = []
    for year in range(int(source["year_min"]), int(source["year_max"]) + 1):
        for month in months:
            urls.append(
                template.format(
                    year=year,
                    month=int(month),
                    month_name=names.get(int(month), names.get(str(month), "")),
                )
            )
    return urls


def _from_list(config: dict) -> list[str]:
    path = Path(config["source"]["list_path"])
    if not path.is_absolute():
        path = project_root_from(config) / path
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def project_root_from(config: dict) -> Path:
    return Path(config["_config_path"]).resolve().parents[1]
