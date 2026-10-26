# Agent workflow

Use one prompt per chat, from `prompts/`.

1. `01_inventory.md` — write `data/external/pdf_urls.txt`. Reply is a count.
2. `02_download.md` — write `data/raw/pdfs/`. Reply is ok / skip / fail.
3. `03_probe_layout.md` — three local PDFs. Reply is a table of label hits, not page text.
4. `04_extract_coverage.md` — full extract. Reply is counts by series.
5. `05_patch_one_series.md` — only if a series is missing. One file, one label.

Say "run it anyway" only if you accept a single long turn.