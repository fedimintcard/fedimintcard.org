#!/usr/bin/env python3
"""Draws the Fedimint Card brand library from one set of shapes and colors: the mark (gold, one-color navy and white,
and a heavier small version), the app icon and avatar, the wordmark lockups with outlined letters, the web icons and
the color tokens. Change this file, run it from the repo root and commit what it writes:

    python3 brand/generate.py

It needs fontTools and uharfbuzz (pip install fonttools uharfbuzz) and rsvg-convert (brew install librsvg).
"""
import io, json, os, struct, subprocess

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import uharfbuzz as hb

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, 'fonts', 'Figtree-Variable.ttf')

NAME, WORD, DOMAIN, SLUG = 'Fedimint Card', ('fedimint', 'card'), 'fedimintcard.org', 'fedimint-card'

# every color in the brand, with its use (written to tokens.json and tokens.css)
TOKENS = [
    ('night', '#1A3272', 'The deepest navy: the bottom of the site, the icon and the film.'),
    ('navy', '#22408A', 'The ground: backgrounds behind the gold mark.'),
    ('blue', '#2B4EA6', 'The lit navy at the top of the ground.'),
    ('sky', '#4F7FE6', 'The light falling on the ground from the upper right.'),
    ('ink', '#EEF3FF', 'Text on the navy.'),
    ('mist', '#B9C8EE', 'Secondary text on the navy, and "card" in the wordmark.'),
    ('gold-light', '#F4E9B0', 'The mark\'s gradient, corner to corner: light.'),
    ('gold', '#D2BB6A', 'The mark\'s gradient: middle. The accent: links and highlights.'),
    ('gold-deep', '#A88A3C', 'The mark\'s gradient: deep.'),
    ('paper', '#F5F7FD', 'Light background.'),
    ('ink-on-paper', '#1A3272', 'Text and the one-color mark on light grounds.'),
    ('mist-on-paper', '#5B6C9E', 'Secondary text on light grounds, and "card" in the light wordmark.'),
]
C = {k: v for k, v, _ in TOKENS}


# ---------------------------------------------------------------- the mark
# A rounded gold plate, the card's contacts: a heptagon (Fedimint's seven-sided figure) at the center with seven lines
# running out from its corners to the plate's edge, cut through the gold. 100 x 76 units.
MARK_W, MARK_H = 100, 76
HEPTAGON = [(50.00, 23.00), (61.73, 28.65), (64.62, 41.34), (56.51, 51.51), (43.49, 51.51), (35.38, 41.34), (38.27, 28.65)]


def mark(uid, paint='gold', stroke=2.8):
    """(defs, body) of the mark in a 100 x 76 box. paint: 'gold' (the gradient) or a color."""
    cx, cy = 50.0, 37.25
    lines = ''.join(f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{cx + (x - cx) * 6:.2f}" y2="{cy + (y - cy) * 6:.2f}"/>' for x, y in HEPTAGON)
    poly = ' '.join(f'{x:.2f},{y:.2f}' for x, y in HEPTAGON)
    defs = (f'<mask id="{uid}m" maskUnits="userSpaceOnUse" x="-10" y="-10" width="120" height="120">'
            f'<rect x="1" y="1" width="98" height="74" rx="13" fill="#fff"/>'
            f'<g stroke="#000" stroke-width="{stroke}" fill="none" stroke-linecap="round" stroke-linejoin="round">'
            f'<polygon points="{poly}"/>{lines}</g></mask>')
    fill = paint
    if paint == 'gold':
        defs += (f'<linearGradient id="{uid}g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="100" y2="76">'
                 f'<stop offset="0" stop-color="{C["gold-light"]}"/><stop offset=".45" stop-color="{C["gold"]}"/>'
                 f'<stop offset="1" stop-color="{C["gold-deep"]}"/></linearGradient>')
        fill = f'url(#{uid}g)'
    return defs, f'<rect x="-10" y="-10" width="120" height="120" fill="{fill}" mask="url(#{uid}m)"/>'


def mark_svg(uid, paint='gold', stroke=2.8):
    d, b = mark(uid, paint, stroke)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MARK_W} {MARK_H}" width="{MARK_W * 4}" height="{MARK_H * 4}"><defs>{d}</defs>{b}</svg>\n'


def place_mark(uid, x, y, w, paint='gold', stroke=2.8):
    """The mark as a nested svg at (x, y), w wide."""
    d, b = mark(uid, paint, stroke)
    return f'<svg x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{w * MARK_H / MARK_W:.2f}" viewBox="0 0 {MARK_W} {MARK_H}" overflow="visible"><defs>{d}</defs>{b}</svg>'


def ground(uid, size, rx=0):
    """The navy ground, lit from the upper right."""
    return (f'<defs><radialGradient id="{uid}r" gradientUnits="userSpaceOnUse" cx="{size * 0.86}" cy="{-size * 0.08}" r="{size * 1.25}">'
            f'<stop offset="0" stop-color="{C["sky"]}"/><stop offset=".42" stop-color="{C["blue"]}"/><stop offset="1" stop-color="{C["night"]}"/>'
            f'</radialGradient></defs><rect width="{size}" height="{size}" rx="{rx}" fill="url(#{uid}r)"/>')


def icon_svg(uid, size, share, rx=0, stroke=2.8):
    w = size * share
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
            f'{ground(uid, size, rx)}{place_mark(uid + "k", (size - w) / 2, (size - w * MARK_H / MARK_W) / 2, w, "gold", stroke)}</svg>\n')


# ---------------------------------------------------------------- type: Figtree, shaped with HarfBuzz and outlined
_inst = {}


def _font(weight):
    if weight not in _inst:
        f = instantiateVariableFont(TTFont(FONT), {'wght': weight})
        buf = io.BytesIO(); f.save(buf)
        _inst[weight] = (f, hb.Font(hb.Face(buf.getvalue())), f['head'].unitsPerEm)
    return _inst[weight]


def outline(text, weight, size, x, y, track=0.0):
    """Path data for `text` at font size `size`, its baseline starting at (x, y), letters spaced by `track` em;
    returns (d, width)."""
    f, hbf, upem = _font(weight)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(hbf, buf, {})
    glyphs, order, s, pen, adv = f.getGlyphSet(), f.getGlyphOrder(), size / upem, None, 0.0
    pen = SVGPathPen(glyphs)
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        glyphs[order[info.codepoint]].draw(TransformPen(pen, (s, 0, 0, -s, x + (adv + pos.x_offset) * s, y - pos.y_offset * s)))
        adv += pos.x_advance + track * upem
    return pen.getCommands(), adv * s - track * size


def lockup_svg(uid, dark):
    """The mark beside the wordmark: "fedimint" in Figtree 800 and "card" in 400, tracked in by 0.02 em, with the mark
    1.25 em tall and a 0.32 em gap; a quarter of the mark's height clear on every side."""
    size, track = 100.0, -0.02
    mh = 1.25 * size; mw = mh * MARK_W / MARK_H; gap = 0.32 * size; pad = mh / 4
    base = pad + mh / 2 + 0.36 * size
    tx = pad + mw + gap
    d1, w1 = outline(WORD[0], 800, size, tx, base, track)
    d2, w2 = outline(WORD[1], 400, size, tx + w1 + track * size, base, track)
    W, H = tx + w1 + track * size + w2 + pad, mh + 2 * pad
    c1, c2 = (C['ink'], C['mist']) if dark else (C['ink-on-paper'], C['mist-on-paper'])
    m = place_mark(uid, pad, pad, mw, 'gold' if dark else C['ink-on-paper'])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" width="{W:.0f}" height="{H:.0f}">'
            f'{m}<path d="{d1}" fill="{c1}"/><path d="{d2}" fill="{c2}"/></svg>\n'), W, H


# ---------------------------------------------------------------- files
def write(rel, text):
    path = os.path.join(HERE, rel); os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(text); return path


def render(svg, rel, w=None, h=None, fmt='png'):
    path = os.path.join(HERE, rel); os.makedirs(os.path.dirname(path), exist_ok=True)
    cmd = ['rsvg-convert', '-f', fmt, '-o', path]
    if w: cmd += ['-w', str(w)]
    if h: cmd += ['-h', str(h)]
    subprocess.run(cmd + [svg], check=True); return path


def ico(rel, sources):
    """A .ico of PNG entries: sources = [(png path, size), ...]."""
    data = [open(p, 'rb').read() for p, _ in sources]
    head, off = struct.pack('<HHH', 0, 1, len(sources)), 6 + 16 * len(sources)
    entries = b''
    for (_, n), d in zip(sources, data):
        entries += struct.pack('<BBBBHHII', n % 256, n % 256, 0, 0, 1, 32, len(d), off); off += len(d)
    open(os.path.join(HERE, rel), 'wb').write(head + entries + b''.join(data))


def main():
    # the mark
    for name, paint in (('', 'gold'), ('-navy', C['ink-on-paper']), ('-white', '#FFFFFF')):
        svg = write(f'mark/{SLUG}-mark{name}.svg', mark_svg('m', paint))
        render(svg, f'mark/{SLUG}-mark{name}-1024.png', w=1024)
    # below 40 px the cut lines would be under a pixel wide: the small mark cuts them twice as wide
    write(f'mark/{SLUG}-mark-small.svg', mark_svg('m', 'gold', 5.6))
    write(f'mark/{SLUG}-mark-small-navy.svg', mark_svg('m', C['ink-on-paper'], 5.6))
    # the icon: the mark at 62% of the side on the lit navy; square (iOS and the stores round the corners)
    icon = write(f'icon/{SLUG}-icon.svg', icon_svg('i', 1024, 0.62))
    render(icon, f'icon/{SLUG}-icon-1024.png', 1024, 1024)
    # the avatar: the mark smaller, so a circle crop keeps room around it
    av = write(f'icon/{SLUG}-avatar.svg', icon_svg('a', 400, 0.46))
    render(av, f'icon/{SLUG}-avatar-400.png', 400, 400)
    # the wordmark
    for dark in (True, False):
        svg, W, H = lockup_svg('l', dark)
        p = write(f'lockup/{SLUG}-lockup-on-{"dark" if dark else "light"}.svg', svg)
        render(p, f'lockup/{SLUG}-lockup-on-{"dark" if dark else "light"}.png', w=int(W * 3))
    # web
    fav = write('web/favicon.svg', icon_svg('f', 64, 0.74, rx=14, stroke=5.6))
    for n in (16, 32, 48):
        render(fav, f'web/.f{n}.png', n, n)
    ico('web/favicon.ico', [(os.path.join(HERE, f'web/.f{n}.png'), n) for n in (16, 32, 48)])
    os.replace(os.path.join(HERE, 'web/.f32.png'), os.path.join(HERE, 'web/favicon-32.png'))
    for n in (16, 48):
        os.remove(os.path.join(HERE, f'web/.f{n}.png'))
    for n, rel in ((180, 'web/apple-touch-icon.png'), (192, 'web/icon-192.png'), (512, 'web/icon-512.png')):
        render(icon, rel, n, n)
    # tokens
    write('tokens.json', json.dumps({'name': NAME, 'font': 'Figtree', 'colors': [{'token': k, 'value': v, 'use': u} for k, v, u in TOKENS]}, indent=2) + '\n')
    write('tokens.css', f'/* {NAME} colors (brand/generate.py writes this file) */\n:root {{\n'
          + ''.join(f'  --{k}: {v};  /* {u} */\n' for k, v, u in TOKENS) + '  --font: "Figtree", ui-sans-serif, system-ui, sans-serif;\n}\n')
    print('wrote the', NAME, 'brand library in', HERE)


if __name__ == '__main__':
    main()
