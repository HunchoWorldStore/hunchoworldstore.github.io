# Huncho World Storefront

**Version 1.0.5**

A custom store site for the Huncho World Tebex store. One `index.html`, no build step.

* **Live catalog** from the Tebex Headless API (categories, packages, prices, sales)
* **Cart + checkout on the site**: Cfx.re sign-in, then the Tebex.js checkout popup, so buyers never leave
* **GitBook Docs Embed** on desktop: "Ask the docs" widget, and every product's **Docs** button opens that script's docs in the widget. On phones, **Docs** opens the real docs page in a new tab instead
* Falls back to a built-in catalog with "Buy" links to the Tebex store if Tebex can't be reached

Live at **https://hunchoworldstore.github.io/**. Docs live separately in `HunchoWorldStore/huncho-phone-docs`.

## Setup

1. **Tebex public token.** Tebex Creator Panel → Developers → API Keys (creator.tebex.io/developers/api-keys) → copy the **Public Token**. Paste it into `CONFIG.tebexToken` at the top of the script in `index.html`. The public token is meant for websites; never put the **private key** here.
2. **Turn on GitHub Pages.** Repo → Settings → Pages → Source: **GitHub Actions**. Every push to `main` deploys the site to `https://hunchoworldstore.github.io/`.
3. **Docs widget.** GitBook → your docs site → Settings → **AI & MCP**: make sure Docs Embed is on. The script URL it shows should be `CONFIG.docsSiteUrl` + `/~gitbook/embed/script.js`.
4. **Custom domain (optional).** Add it under Settings → Pages, e.g. `store.hunchoworld.com`.

## Config

| Key | What it does |
| --- | --- |
| `tebexToken` | Public token. Empty = preview mode with the built-in catalog |
| `tebexStoreUrl` | Where "Buy" links go when the live catalog isn't loaded |
| `docsSiteUrl` | Your GitBook site, used for the docs widget |
| `discordUrl` | Discord invite in the header and footer |
| `brand` | Checkout popup colours |
| `hide` | Package or category names to keep off the site (Fayettenam is hidden) |
| `docs` | Matches a package name to its docs section and a fallback image |

**New script?** Add it to Tebex (it shows up on the site by itself), then add a line to `CONFIG.docs` so its **Docs** button and image work.

## Changelog

### 1.0.5

* Fayettenam packages hidden from the store (`CONFIG.hide`)
* Scripts listed A–Z

### 1.0.4

* Designer bags: Docs button shows whatever the Tebex package is called (bags, bookbags, backpacks, designer)

### 1.0.3

* Phones: no docs pop-up. **Docs** buttons open the docs page in a new tab

### 1.0.2

* Moved to its own repo: new address https://hunchoworldstore.github.io/

### 1.0.1

* Tebex public token added: live catalog and checkout are on

### 1.0.0

* First version: live Tebex catalog, cart, Cfx.re sign-in, Tebex.js checkout, GitBook docs widget
