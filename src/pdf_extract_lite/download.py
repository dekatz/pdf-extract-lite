"""Download PDFs with retries, rate limit, and optional env-based auth.

Does not read PDF contents.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path

import requests

MONTHS = {
    "january": 1, "januar": 1, "february": 2, "februar": 2,
    "march": 3, "maerz": 3, "marz": 3, "april": 4,
    "may": 5, "mai": 5, "june": 6, "juni": 6, "july": 7, "juli": 7,
    "august": 8, "september": 9, "october": 10, "oktober": 10,
    "november": 11, "december": 12, "dezember": 12,
}


def session_from_config(config: dict) -> requests.Session:
    session = requests.Session()
    headers = {"User-Agent": config.get("user_agent") or "pdf-extract-lite/0.1"}
    headers.update(config.get("download", {}).get("headers") or {})
    auth = config.get("auth") or {"type": "none"}
    if auth["type"] == "bearer_env":
        token = os.environ.get(auth["env_var"], "")
        if not token:
            raise RuntimeError(f"auth.env_var {auth['env_var']} is empty")
        headers["Authorization"] = f"Bearer {token}"
    elif auth["type"] == "cookie_env":
        cookie = os.environ.get(auth["env_var"], "")
        if not cookie:
            raise RuntimeError(f"auth.env_var {auth['env_var']} is empty")
        headers["Cookie"] = cookie
    session.headers.update(headers)
    return session


def local_name(url: str, config: dict) -> str:
    raw = url.rsplit("/", 1)[-1].split("?")[0]
    pattern = config["source"].get("stamp_regex")
    if pattern:
        match = re.search(pattern, raw, re.IGNORECASE)
        if match:
            year = match.groupdict().get("year")
            month = match.groupdict().get("month")
            if year and month:
                month_num = MONTHS.get(month.lower().replace("ä", "a"), None)
                if month_num is None and month.isdigit():
                    month_num = int(month)
                if month_num:
                    return f"{int(year):04d}-{month_num:02d}_{raw}"
    return raw


def download_all(config: dict, urls: list[str], out_dir: Path) -> dict[str, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    session = session_from_config(config)
    delay = float(config["download"]["rate_limit_seconds"])
    retries = int(config["download"]["retries"])
    timeout = int(config["download"]["timeout_seconds"])
    min_bytes = int(config["download"]["min_bytes"])
    counts = {"ok": 0, "skip": 0, "fail": 0}
    failures: list[str] = []
    for url in urls:
        dest = out_dir / local_name(url, config)
        if dest.exists() and dest.stat().st_size >= min_bytes:
            counts["skip"] += 1
            continue
        status = _one(session, url, dest, retries, timeout, min_bytes)
        counts[status] += 1
        if status == "fail":
            failures.append(url)
        time.sleep(delay)
    if failures:
        fail_path = out_dir.parent / "external" / "download_failures.txt"
        fail_path.parent.mkdir(parents=True, exist_ok=True)
        fail_path.write_text("\n".join(failures) + "\n", encoding="utf-8")
    return counts


def _one(session, url, dest: Path, retries: int, timeout: int, min_bytes: int) -> str:
    tmp = dest.with_suffix(dest.suffix + ".part")
    for attempt in range(1, retries + 1):
        try:
            with session.get(url, stream=True, timeout=timeout) as response:
                if response.status_code == 429:
                    wait = int(response.headers.get("Retry-After") or 5)
                    time.sleep(wait)
                    continue
                if response.status_code != 200:
                    continue
                with tmp.open("wb") as handle:
                    for chunk in response.iter_content(64 * 1024):
                        if chunk:
                            handle.write(chunk)
            if tmp.stat().st_size < min_bytes:
                tmp.unlink(missing_ok=True)
                continue
            tmp.replace(dest)
            return "ok"
        except requests.RequestException:
            time.sleep(min(2 ** attempt, 10))
    tmp.unlink(missing_ok=True)
    return "fail"
