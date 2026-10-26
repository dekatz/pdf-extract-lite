# Limitations and edge cases

- One HTML page only. Year accordions that load PDFs on click are invisible to `html_archive` unless the hrefs are already in the HTML.
- No login flow. Bearer token and cookie must already be in the environment. The tool will not click a login form.
- `pdftotext -layout` must be installed (poppler). Scanned PDFs without a text layer return empty sections. This package does not OCR.
- Series values are the numbers on the label line, in order. Wrapped rows, two-line headers, and year tokens inside the label are the usual miss. Probe is how you see that, without pasting the page.
- Position is not a month. A 2027 projection column is only flagged when it sits past position 12 (`tail_is_projection`). Confirm the grid before treating that flag as a forecast.
- Duplicate labels on the same page (Kempten vs Frankreich) need regexes that do not match both. The first matching line wins.
- Page numbers in the publisher's table of contents are not used. Section markers are. If a report renames the section, update `section_markers`.
- URL templates will request months that were never published. Those land in `download_failures.txt` (HTTP not 200 or file too small).
- Do not commit `data/raw/` or cookies. `.gitignore` excludes them.
- The agent workflow is the cost control. Running discover, download, probe, and extract inside one chat, or attaching page images, recreates the heavy turn this package is meant to avoid.
