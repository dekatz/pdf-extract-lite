# Step 2 — download, no reading

Do not extract text and do not paste PDF bytes.
Using configs/<site>.yaml and data/external/pdf_urls.txt, run:
  python -m pdf_extract_lite --config configs/<site>.yaml download
Reply with ok, skip, fail, and the raw directory path.
If fail > 0, name data/external/download_failures.txt and stop.
