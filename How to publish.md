# Website guide — everything in one place

The single doc for all things adam-costa.com. Claude keeps this updated whenever a new process arises. (This note stays private — it's gitignored via `tools/.gitignore`.)

## How the site is put together

One folder, one repo, one publish. The whole site — homepage, books, essays, and the tools — lives in the **`Website`** folder, which is a single git repo published with GitHub Pages. Your domain **adam-costa.com** is pointed at this repo by the one-line `CNAME` file.

Think of the repo as a folder GitHub agrees to serve as a live website. "Publishing" just means uploading the latest version of that folder to GitHub (git calls this a *push*); GitHub notices and rebuilds the site about a minute later.

Tools live in `Website/tools/` and show up on the web at **adam-costa.com/tools/** — a subfolder in the repo becomes a subpath on the site, automatically. (Until 2026-07-23 the tools were a second, separate repo that had to be pushed on its own. That split is gone — there's just the one repo now.)

## Publish changes (the normal way — GitHub Desktop)

1. Open **GitHub Desktop** and select the **website** repo in the top-left dropdown.
2. The left panel lists everything you changed. Look it over.
3. Bottom-left: type a short summary (e.g. "add breathing timer"), click **Commit to main**.
4. Top of the window: click **Push origin**.
5. Wait about a minute, then hard-refresh the page (Cmd+Shift+R — browsers cache the old CSS).

That's the whole ritual. Or ask Claude to stage the commit for you, and you just click **Push origin**.

## Publish a new tool

1. Drop a self-contained `something.html` into `Website/tools/` (or ask Claude — "a static tool for my tools folder" gets the right kind of file). Tools must be static: HTML/CSS/JS, no server. Multi-file is fine.
2. Add a card for it in `tools/index.html` — copy an existing `<a class="card">` block, change the link/title/description.
3. Add it to the navbar: one `("/tools/x.html", "Label")` line in `Website/_source/navdata.py` (Tools section), then from `Website/_source` run `python3 patch_nav.py` (rewrites the nav across all pages).
4. Commit + push once in GitHub Desktop. Live at `adam-costa.com/tools/something.html`.

## Edit the navbar

The whole navbar — including dropdowns — lives in one file: `Website/_source/navdata.py`. Add or change a `("url", "label")` line in the right section's `items` list (tools use absolute paths like `/tools/x.html`; chapters and essays use site-relative ones like `life/new-essay/`). Then from `Website/_source` run `python3 patch_nav.py`, and publish.

## Edit book chapters or essays

Edit the page's `index.html` directly, or edit the markdown in `_source/` and re-run `build_site.py` (needs `pip install markdown`). Then publish.

## Rules that prevent disasters

- **Never delete `Website/CNAME`.** That one-line file binds adam-costa.com to the repo; losing it takes the whole site offline. (Learned the hard way, 2026-07-19.)
- **`build_site.py` is the nuclear rebuild — handle with care.** It wipes its output folder and regenerates from `_source/`. By default it builds to `/tmp/site` (safe). Never point its `SITE_OUT` at the `Website` folder itself — it would erase everything not generated from `_source/`, including the whole `tools/` folder. For small nav tweaks, prefer `patch_nav.py`, which edits pages in place.
- Everything in the repo becomes **public** when pushed — no private notes, keys, or drafts you're not ready to share. This note and anything in `tools/.gitignore` stay private. Drafts are safe until you push.

## Troubleshooting

- **Push asks for a password**: use GitHub Desktop — it handles login for you. (If ever using the terminal, paste a personal access token with `repo` scope, never your account password.)
- **Site not updating after push**: Pages takes about a minute; then hard-refresh (Cmd+Shift+R).
- **adam-costa.com 404s entirely**: check `CNAME` exists in the repo, and repo Settings → Pages shows the domain.

## Site history

- 2026-07-16 — site built from `_source` markdown, deployed to GitHub Pages
- 2026-07-18 — tools launched (originally a separate repo); FIRE calculator
- 2026-07-19 — custom domain unified, navbar dropdowns + Tools menu, Where to go when
- 2026-07-23 — Exhale breathing timer added; **tools folder merged into the main repo** (one repo, one push from here on); old separate `tools` repo retired
