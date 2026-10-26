# pdf-extract-lite

Many businesses share their monthly reports as PDF files—things like price lists, how many items they sold, and how many customers they had. These numbers are really useful for spotting trends over time, but there's a catch: PDFs aren't set up for easy analysis.

Getting the data out manually means downloading files, copying tables by hand, and making sure everything lines up properly. It takes forever and leaves room for mistakes. And while some people try to automate this with Bots or Agents, those tools often end up in a long agent turn, where the agents gives prompt in multiple steps that cost time and money.

This project shows you a semi-automated and cheaper way. Instead of dealing with PDFs manually or running expensive automated workflows, we separate the Token-expensive process locally, thus the agents only memorized the Token-cheap processing, such as: how many links, how many downloads, and which labels were found.

## How it works

You describe the site and the figures you want in a YAML config file (page URL or URL template, which links to keep, section markers, and the row labels to extract).  

A short local script then:
1. discovers the PDF links,
2. downloads the files,
3. extracts the numbers with `pdftotext` on your machine.

The LLM is used only in five short, separate chats. In each chat it runs one command and receives a count or a tiny table. No PDF text or page images ever enter the conversation, which keeps token use very low.

Built with Grok.

## Layout

```
pdf-extract-lite/
├── configs/          # one YAML per website
├── docs/             # customization, limitations, agent workflow
├── prompts/          # paste one file per chat
├── src/pdf_extract_lite/
│   ├── discover.py   # html_archive | url_template | link_list
│   ├── download.py   # retries, Retry-After, env auth
│   └── extract.py    # pdftotext section + label regex
└── data/             # created on run; raw PDFs are gitignored
```

| Path | Purpose |
|---|---|
| `configs/` | Site URL, filters, rate limit, section markers, series labels |
| `src/` | Shared pipeline. No publisher name |
| `prompts/` | Short chats that keep PDF text out of the model |
| `data/raw/pdfs/` | Immutable downloads |
| `data/processed/` | Long CSV |

## Setup

```bash
cd pdf-extract-lite
python -m pip install -r requirements.txt
# poppler: pdftotext must be on PATH
python -m pdf_extract_lite --config configs/html_archive.example.yaml discover
```

Install the package in editable mode if you want the console script:

```bash
python -m pip install -e .
pdf-extract-lite --config configs/html_archive.example.yaml discover
```

## Two website types

HTML archive (links already in the page), Swissmilk Marktlagebericht:

```bash
python -m pdf_extract_lite --config configs/html_archive.example.yaml discover
python -m pdf_extract_lite --config configs/html_archive.example.yaml download
python -m pdf_extract_lite --config configs/html_archive.example.yaml probe --pdf data/raw/pdfs/<one>.pdf
python -m pdf_extract_lite --config configs/html_archive.example.yaml extract
```

URL template (no scrape; stable monthly path). The example host is a placeholder — copy the file and set a real `url_template`:

```bash
python -m pdf_extract_lite --config configs/url_template.example.yaml discover
```

A third type, `link_list`, reads URLs from a text file (`source.list_path`) when you already exported them.

## Agent use

Paste `prompts/01_inventory.md` through `prompts/05_patch_one_series.md` as separate chats. See `docs/workflow.md`.

## Auth and rate limits

`auth.type` is `none`, `bearer_env`, or `cookie_env`. The token stays in the environment. `download.rate_limit_seconds` pauses between files. HTTP 429 uses `Retry-After`. Failed URLs go to `data/external/download_failures.txt`.

## Limitations

Section match is by title, not page number. Values are numbers on the label line, in order, not yet calendar months. Scanned PDFs and JavaScript-only archives are out of scope. Detail in `docs/limitations.md`. Custom fields in `docs/customization.md`.
