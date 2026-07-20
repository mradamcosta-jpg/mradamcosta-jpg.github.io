# adam-costa.com

A static site—plain HTML and CSS, no build step, no dependencies.

## Structure

- `index.html` — homepage
- `financial-freedom/` — the financial freedom book (16 chapters, 4 parts)
- `productivity/` — How to live your best life (intro, 7 chapters, conclusion, resources)
- `life/` — standalone essays
- `privacy/`, `disclaimer/`, `404.html` — footer pages
- `style.css`, `images/` — shared assets
- `_source/` — original markdown exports + `build_site.py` (the script that generated this site). GitHub Pages ignores folders starting with `_`, so this stays unpublished.

## Deploying to GitHub Pages

Push this folder's contents to your GitHub Pages repo (for a user site, the root of `<username>.github.io`; for a project site, enable Pages on the main branch). No configuration needed—every page is a folder with an `index.html`, so URLs stay clean (e.g. `/financial-freedom/taxes/`).

## Editing content

Edit the HTML pages directly, or edit the markdown in `_source/` and re-run `build_site.py` (requires Python 3 with the `markdown` package; it regenerates the whole site).

## Editing the navbar (dropdowns)

The navbar lives in one place: `_source/navdata.py`. To add a tool, chapter, or essay to a dropdown:

1. Open `_source/navdata.py` and add a `("url", "label")` line to the right section's `items` list. Tool links are absolute (`/tools/...`); everything else is site-relative.
2. In Terminal:

   ```bash
   cd "_source" && python3 patch_nav.py
   ```

   That rewrites the nav in all 38 pages with correct relative paths. (`build_site.py` also uses navdata.py, so full rebuilds stay in sync.)
3. Commit and push (`git add -A && git commit -m "nav" && git push`).

One `CNAME` warning: never delete the `CNAME` file—it's what binds adam-costa.com to this repo.
