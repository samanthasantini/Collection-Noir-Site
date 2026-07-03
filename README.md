# Collection Noir — Sheet-to-Site Pipeline

## The idea
You never touch JSON or HTML for a routine update. You edit the Google
Sheet. I pull it, regenerate the pages, and hand you back a ready-to-push
site.

**Live sheet:** https://docs.google.com/spreadsheets/d/1sgNTij_a_Uvjq2HUv3ajgypno2oM9-WrUtxGmqNZCcM/edit

## What you do
Open the sheet. Edit a cell — a price, a description, a lead time, a
stone name, an image filename. Save (Sheets autosaves). That's it.

Columns:
- `slug` — never edit this, it's the URL (e.g. site.com/products/{slug})
- `name`, `category`, `price`, `short_description`
- `stone_1` / `stone_2` / `stone_3` — must match a name in `data/stones.json`
- `lead_time_weeks`, `dimensions`
- `primary_image_filename`, `spec_sheet_filename` — just the filename,
  the actual files live in `/assets/products/` and `/spec-sheets/`
- `status` — draft / live (for your own tracking, not yet wired into the build)

Leave `price` blank and the page automatically shows "Price on enquiry"
instead of a broken price field — so you can publish a product before
costing is finalised.

## What I do, when you say "sync the site" or "sync and deploy"
1. Pull the current sheet as CSV
2. `python3 build/sync_from_sheet.py` — turns each row into
   `data/products/{slug}.json`
3. `python3 build/build.py` — renders every product JSON through
   `templates/product-page.html` into `public/products/{slug}/index.html`
4. `python3 build/deploy.py <you>/<repo> <token>` — commits and pushes
   everything to GitHub. Netlify is watching that repo and redeploys
   automatically within about a minute.

Three commands, no manual file editing, no drag-and-drop, every time.

## One-time setup (do this once, before the first real deploy)
1. **GitHub** — create an empty repo, e.g. `collection-noir-site`.
2. **Netlify** — Add new site → Import an existing project → Deploy with
   GitHub → pick that repo → publish directory `public`.
3. **Token** — GitHub → Settings → Developer settings → Personal access
   tokens → Fine-grained token, scoped to just that repo, "Contents:
   Read and write." You paste this to me only when you want a deploy —
   it's never stored or committed anywhere; `deploy.py` strips it back
   out of `.git/config` immediately after pushing.

After that, every future "sync the site" is just you giving me the
green light — no re-setup.

## What this doesn't solve
- **New product with a different layout** (e.g. a product needing a
  second image gallery, or a totally new page type) — still needs an
  actual build session with me.
- **Structural page changes** — nav, homepage layout, new page types —
  same as above.
- **Photography** — the sheet only stores filenames; the actual images
  still need to be shot/generated and dropped into `/assets/products/`.

Everything else — 90% of what changes week to week — is a spreadsheet
edit away.

## File map
```
data/
  products_master.csv     ← local mirror of the Sheet (for reference/testing)
  products/*.json         ← auto-generated, don't hand-edit
  stones.json             ← shared material definitions
templates/
  product-page.html       ← the one template every product renders through
  partials/                header.html, footer.html
styles/
  tokens.css              ← brand colours, fonts — edit once, every page updates
build/
  sync_from_sheet.py       ← Sheet CSV -> JSON
  build.py                 ← JSON -> HTML
public/
  products/{slug}/index.html  ← what actually gets deployed
```
