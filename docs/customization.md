# Customizing pdf-extract-lite

Python stays generic. A new website is a new YAML file, not a fork.

## Pick a source type

| Website shape | `source.type` | You set |
|---|---|---|
| Publications page with `<a href="...pdf">` | `html_archive` | `page_url`, `link_must_contain` |
| Predictable monthly path | `url_template` | `url_template`, `year_min`, `year_max` |
| URLs already in a text file | `link_list` | `list_path` |

`html_archive` reads the HTML of one page. It does not click year toggles in a browser. If the links are absent until JavaScript runs, either save the expanded HTML as a `link_list`, or use `url_template` if the paths are regular.

## Series labels

Each series is an id plus a regex matched against one line of `pdftotext -layout` inside the section. Prefer a short unique label (`EU Butter \\(lose, Kempten\\)`) over a whole sentence.

Probe three files before a full extract. `missing_ids` is the list to fix. Change the YAML, not the parser, unless the section marker itself moved.

## Filenames

`stamp_regex` must expose named groups `year` and `month` if you want `YYYY-MM_` prefixes. Month may be `01` or a name in German or English (`januar`, `june`).

## Auth

Leave secrets out of YAML.

```yaml
auth:
  type: bearer_env
  env_var: PDF_AUTH_TOKEN
```

or `cookie_env` with a `Cookie` header value in the environment. `type: none` is the default.

## Rate limits

`download.rate_limit_seconds` is the pause between files. A `429` response sleeps for `Retry-After` (or 5 seconds) and retries. Failures are listed in `data/external/download_failures.txt` and do not stop the rest of the batch.

## Output

`extract` writes a long CSV: one row per series value position in that report. Position 1 is the first number on the label line after years are dropped. It is not yet a calendar month. Map positions to months in a later, separate step once probe shows the column order is stable.
