# Step 1 — inventory only
# Paste into a new chat. Do not attach PDFs.

Do not open PDFs and do not paste page text or screenshots.
Using configs/<site>.yaml, run:
  python -m pdf_extract_lite --config configs/<site>.yaml discover
Reply with: url count, first URL host, last URL host, and the output path.
If discover fails, reply with the HTTP status only.
