# fedimintcard.org

The one-page site for Fedimint Card, an experimental JavaCard that holds the spend keys for
Fedimint ecash notes and pays by tap.

`dist/` is the whole site (the home page, `/support` and `/privacy`, sharing `assets/site.css`): plain HTML and CSS, no scripts and no analytics. It is served by a
Cloudflare Worker with static assets (`wrangler.jsonc`). `worker.js` runs only for `/film/*`: it
answers byte-range requests with 206, which Safari and iOS need to play video, and Workers Caching
keeps the full file at the edge. Put showcase films in `dist/film/`. It is the same setup as
cashucard.org.

```sh
npx wrangler dev                 # local preview
npx wrangler versions upload     # preview URL, nothing published
npx wrangler deploy              # publish
```

The card art comes from the sticker renders of the card face; the font is Figtree (SIL Open
Font License, `dist/assets/fonts/OFL.txt`).

MIT licensed. Contact: hi@fedimintcard.org
