# Fedimint Card brand

The Fedimint Card mark is a card's chip drawn in gold: a heptagon, Fedimint's seven-sided figure, at the center of the contacts, with seven lines running out from its corners. This folder holds the marks, the icons, the wordmark, the web icons, the colors and the card stickers. `generate.py` draws everything except the stickers from one set of shapes and colors: change it, run it, and commit what it writes.

```sh
pip install fonttools uharfbuzz   # once; rsvg-convert comes from: brew install librsvg
python3 brand/generate.py
```

## The mark

| File | Use |
| --- | --- |
| `mark/fedimint-card-mark.svg` | The color mark, in the chip's gold gradient: on the navy and other dark grounds. |
| `mark/fedimint-card-mark-navy.svg` | One color, navy: on light grounds, in print and for embossing. |
| `mark/fedimint-card-mark-white.svg` | One color, white: on photos and colored grounds. |
| `mark/fedimint-card-mark-small.svg`, `-small-navy.svg` | The mark with its lines cut twice as wide, for 40 px and below, where the regular lines would be under a pixel wide. |
| `mark/*-1024.png` | The gold, navy and white marks as 1024 px PNGs. |

## The icon

| File | Use |
| --- | --- |
| `icon/fedimint-card-icon.svg`, `-1024.png` | The app icon: the gold mark at 62% of the side, on the navy lit from the upper right. It is square; iOS and the stores round the corners. |
| `icon/fedimint-card-avatar.svg`, `-400.png` | Social profiles and the GitHub org. The mark sits smaller, so a circle crop keeps room around it. |

## The wordmark

`lockup/fedimint-card-lockup-on-dark` and `-on-light` (SVG and PNG) set the mark beside "fedimintcard": "fedimint" in Figtree 800 and "card" in Figtree 400, tracked in by 0.02 em, with the mark 1.25 em tall and a 0.32 em gap. On dark grounds the mark is gold and the letters ink and mist; on light grounds the mark and "fedimint" are navy. The letters are outlines, so the files work without the font.

## Web

`web/favicon.svg` (the small mark on a rounded navy tile), `favicon.ico` (16, 32 and 48 px), `favicon-32.png`, `apple-touch-icon.png` (180 px), and `icon-192.png` and `icon-512.png` for a web app manifest.

## Colors and type

`tokens.json` and `tokens.css` list every color with its use. The main ones:

| Token | Value | Use |
| --- | --- | --- |
| `navy` | `#22408A` | The ground behind the gold mark. |
| `night`, `blue`, `sky` | `#1A3272`, `#2B4EA6`, `#4F7FE6` | The ground's light, from its deepest to where the light falls. |
| `ink` | `#EEF3FF` | Text on the navy. |
| `gold-light`, `gold`, `gold-deep` | `#F4E9B0`, `#D2BB6A`, `#A88A3C` | The mark's gradient, corner to corner. `gold` is the accent. |
| `paper` | `#F5F7FD` | Light background. |

Figtree is the typeface for every word in the brand. `fonts/Figtree-Variable.ttf` covers every weight, under the SIL Open Font License in `fonts/OFL.txt`.

## Using the mark

- Keep clear space of at least a quarter of the mark's height on every side.
- Use the regular mark from 41 px up, or 10 mm in print, and the small mark below that.
- Put the gold mark on the navy or another dark ground, the navy mark on light grounds, and the white mark on photos.
- Keep the mark's shape, angle and gradient as drawn. Stretching, turning, outlining or recoloring it makes a different mark.

## Print: card stickers

`print/card-sticker/fedimint-card-stickers.pdf` is a US Letter sheet of stickers for a blank J3R180 card, eight to a page with 1.5 mm bleed and crop marks: page 1 is the front with a drawn chip, page 2 the front with a window cut where the card's real contacts sit (measured from the blank, 9.3 to 20.45 mm across and 18.2 to 26.9 mm down), and page 3 the back, with a QR code to fedimintcard.org. `preview-front.png` and `preview-back.png` show one of each. `source/` holds the HTML each face is drawn from and `gen_sheet.py`, which lays out the sheet; they render in headless Chrome at 4x and need `Figtree-Variable.ttf` beside them.

## What uses it

fedimintcard.org's favicon, header and film use the mark already; its icons move to `web/` when the site next changes. The GitHub org avatar was drawn the same way before this library existed; `icon/fedimint-card-avatar-400.png` replaces it if it ever changes.
