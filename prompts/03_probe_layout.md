# Step 3 — probe three files already on disk

Do not paste page text or screenshots.
Probe only these three local PDFs (adjust names to files that exist):
  data/raw/pdfs/<early>.pdf
  data/raw/pdfs/<middle>.pdf
  data/raw/pdfs/<latest>.pdf
Run:
  python -m pdf_extract_lite --config configs/<site>.yaml probe --pdf <those three>
Reply with the probe table only: file, section_pages, n_labels_present, n_labels_missing, missing_ids.
Do not extract values.
