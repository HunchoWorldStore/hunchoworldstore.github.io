# Huncho World Storefront

**Version 1.1.2**

A custom store site for the Huncho World Tebex store. One `index.html`, no build step.

* **Live catalog** from the Tebex Headless API (categories, packages, prices, sales)
* **Cart + checkout on the site**: Cfx.re sign-in, then the Tebex.js checkout popup, so buyers never leave
* **Docs site at `/docs`**, built from the GitBook docs repo (see below). Old: **GitBook Docs Embed** on desktop: "Ask the docs" widget, and every product's **Docs** button opens that script's docs in the widget. On phones, **Docs** opens the real docs page in a new tab instead
* Falls back to a built-in catalog with "Buy" links to the Tebex store if Tebex can't be reached

Live at **https://hunchoworldstore.github.io/**. Docs live separately in `HunchoWorldStore/huncho-phone-docs`.

## Docs site (`/docs`)

`tools/build_docs.py` turns the GitBook docs repo (`HunchoWorldStore/huncho-phone-docs`) into a JG-style docs site: hero search, Common solutions / Script guides / Need a hand cards, one A–Z sidebar, search (⌘K), and every GitBook hint, stepper, tab and expandable section.

* The deploy workflow rebuilds it on every push here, every hour, and on demand (Actions → Deploy storefront → Run workflow), so docs edits show up on their own within the hour.
* The built pages are also committed in `docs/`.
* New script? Add it to `SECTIONS` at the top of `tools/build_docs.py` (slug, title, folder, icon).
* GitBook keeps working as before. Nothing in the docs repo changes.

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
| `discord` | Buyers sign in with Discord before checkout; their Discord ID goes to Tebex as `discord_id` (for Discord roles / messages). Needs `clientId` from a Discord application (redirect `https://hunchoworldstore.github.io/`). Without it, buyers type their ID instead. `ask: false` turns it off |
| `docs` | Matches a package name to its docs section and a fallback image |

**New script?** Add it to Tebex (it shows up on the site by itself), then add a line to `CONFIG.docs` so its **Docs** button and image work.

## Changelog

### 1.1.2

* **Have a code?** box in the cart: Tebex coupons, gift cards and creator codes, applied right before the checkout opens

### 1.1.1

* Header and footer **Docs** links are plain links to `/docs/`

### 1.1.0

* New docs site at `/docs` in the JG layout, with the Huncho World logo, A–Z sidebar and search
* Store **Docs** buttons open the new docs (GitBook pop-up removed)

### 1.0.9

* Huncho World Store logo: header, hero, cart, browser tab icon and link previews
* Sign in with Discord switched on (Discord app client ID added)

### 1.0.8

* **Sign in with Discord** in the cart instead of typing a user ID (needs `CONFIG.discord.clientId`)
* Checkout carries on by itself after the Discord sign-in

### 1.0.7

* Discord user ID box in the cart, sent to Tebex as `discord_id` with every script (remembered for next time)

### 1.0.6

* If Tebex rejects a checkout, the cart shows which script failed and a **Finish on Tebex** button that opens that package on the Tebex store
* A failed checkout starts with a fresh basket next time

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
