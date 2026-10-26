"""CLI. Subcommands return counts. They do not print PDF page text."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from pdf_extract_lite.config import load_config
from pdf_extract_lite.discover import discover
from pdf_extract_lite.download import download_all
from pdf_extract_lite.extract import extract_file, probe_file, write_csv

STAMP = re.compile(r"(20\d{2})-(\d{2})_")


def _root(config) -> Path:
    return Path(config["_config_path"]).resolve().parents[1]


def _cmd_discover(config, args) -> int:
    urls = discover(config)
    out = Path(args.out) if args.out else _root(config) / "data" / "external" / "pdf_urls.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(urls) + ("\n" if urls else ""), encoding="utf-8")
    print(f"urls={len(urls)} out={out}")
    return 0


def _cmd_download(config, args) -> int:
    list_path = Path(args.url_list) if args.url_list else _root(config) / "data" / "external" / "pdf_urls.txt"
    urls = [line.strip() for line in list_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    out_dir = Path(args.out_dir) if args.out_dir else _root(config) / config["download"]["out_dir"]
    counts = download_all(config, urls, out_dir)
    print(f"ok={counts['ok']} skip={counts['skip']} fail={counts['fail']} dir={out_dir}")
    return 0 if counts["fail"] == 0 else 1


def _cmd_probe(config, args) -> int:
    files = [Path(p) for p in args.pdf]
    rows = [probe_file(path, config) for path in files]
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return 0


def _cmd_extract(config, args) -> int:
    pdf_dir = Path(args.pdf_dir) if args.pdf_dir else _root(config) / config["download"]["out_dir"]
    out = Path(args.out) if args.out else _root(config) / config["extract"]["out"]
    rows = []
    n_files = 0
    for path in sorted(pdf_dir.glob("*.pdf")):
        n_files += 1
        match = STAMP.search(path.name)
        year = int(match.group(1)) if match else None
        month = int(match.group(2)) if match else None
        try:
            rows.extend(extract_file(path, config, year, month))
        except Exception as exc:  # keep going; report the file name only
            print(f"fail={path.name} err={type(exc).__name__}", file=sys.stderr)
    write_csv(rows, out)
    print(f"files={n_files} rows={len(rows)} out={out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Config-driven PDF archive extract")
    parser.add_argument("--config", required=True, type=Path)
    sub = parser.add_subparsers(dest="cmd", required=True)

    discover_p = sub.add_parser("discover")
    discover_p.add_argument("--out", type=Path)

    download_p = sub.add_parser("download")
    download_p.add_argument("--url-list", type=Path)
    download_p.add_argument("--out-dir", type=Path)

    probe_p = sub.add_parser("probe")
    probe_p.add_argument("--pdf", nargs="+", required=True)

    extract_p = sub.add_parser("extract")
    extract_p.add_argument("--pdf-dir", type=Path)
    extract_p.add_argument("--out", type=Path)

    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.cmd == "discover":
        return _cmd_discover(config, args)
    if args.cmd == "download":
        return _cmd_download(config, args)
    if args.cmd == "probe":
        return _cmd_probe(config, args)
    return _cmd_extract(config, args)


if __name__ == "__main__":
    raise SystemExit(main())
