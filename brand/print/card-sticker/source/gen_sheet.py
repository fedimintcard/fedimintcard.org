"""Letter sheet of Fedimint Card stickers from bleed-chip.png / bleed-nochip.png (render of face.html plus 1.5 mm bleed)."""
K=85.6/1048
CW,CH=85.6,54.0; SW,SH=85.0,53.6; R=3.0
IW,IH=1085*K,700*K
BW,BH=CW+3.0,CH+3.0
GX,GY=10.0,7.0; COLS,ROWS=2,4; PW,PH=215.9,279.4
LM=(PW-(COLS*BW+(COLS-1)*GX))/2; TM=8.0
WIN=(8.8,17.7,21.0,27.4)   # measured from a real blank (IMG_0738, perspective-corrected): chip 9.3-20.45 x 18.2-26.9 mm, plus 0.5 mm
def marks(x,y):
    cx0=x+1.5+(CW-SW)/2; cy0=y+1.5+(CH-SH)/2; cx1=cx0+SW; cy1=cy0+SH; o=''
    for cx in (cx0,cx1): o+=f'<line x1="{cx:.3f}" y1="{y-0.5:.3f}" x2="{cx:.3f}" y2="{y-3.0:.3f}"/><line x1="{cx:.3f}" y1="{y+BH+0.5:.3f}" x2="{cx:.3f}" y2="{y+BH+3.0:.3f}"/>'
    for cy in (cy0,cy1): o+=f'<line x1="{x-0.5:.3f}" y1="{cy:.3f}" x2="{x-3.5:.3f}" y2="{cy:.3f}"/><line x1="{x+BW+0.5:.3f}" y1="{cy:.3f}" x2="{x+BW+3.5:.3f}" y2="{cy:.3f}"/>'
    return o
def page(window, back=False):
    els='';m=''
    for r in range(ROWS):
        for c in range(COLS):
            x=LM+c*(BW+GX); y=TM+r*(BH+GY)
            img="bleed-back.png" if back else f'bleed-{"nochip" if window else "chip"}.png'
            els+=f'<div class="b" style="left:{x:.3f}mm;top:{y:.3f}mm"><img src="{img}">'
            if window:
                els+=f'<div class="win" style="left:{1.5+WIN[0]}mm;top:{1.5+WIN[1]}mm;width:{WIN[2]-WIN[0]}mm;height:{WIN[3]-WIN[1]}mm"></div>'
            els+='</div>'; m+=marks(x,y)
    cap=(f'Page 2, for blanks with gold contacts on the front: cut out the dashed window ({WIN[0]:g} to {WIN[2]:g} mm from the left edge, {WIN[1]:g} to {WIN[3]:g} mm from the top). Check it against one card first.') if window else \
        'Page 1, for blanks without contacts on the front: the chip is part of the artwork.'
    if back: cap='Page 3, the back of the card. The QR code opens fedimintcard.org.'
    return f'''<section class="page">{els}<svg class="marks" viewBox="0 0 {PW} {PH}" stroke="#000" stroke-width="0.2">{m}</svg>
<p class="cap">Fedimint Card stickers, {SW:g} x {SH:g} mm with {R:g} mm round corners. Print at 100% (Actual size) on white sticker vinyl. Cut on the marks.<br>{cap}</p></section>'''
bottom=TM+ROWS*BH+(ROWS-1)*GY
html=f'''<!doctype html><html><head><meta charset="utf-8"><title>Fedimint Card stickers</title><style>
@page{{size:{PW}mm {PH}mm;margin:0}}
*{{box-sizing:border-box}} html,body{{margin:0;padding:0}}
.page{{position:relative;width:{PW}mm;height:{PH}mm;overflow:hidden;break-after:page}}
.b{{position:absolute;width:{BW}mm;height:{BH}mm;overflow:hidden}}
.b img{{position:absolute;left:0;top:0;width:{IW:.3f}mm;height:{IH:.3f}mm}}
.win{{position:absolute;background:#fff;border:0.25mm dashed #000;border-radius:1.5mm}}
.marks{{position:absolute;left:0;top:0;width:{PW}mm;height:{PH}mm}}
.cap{{position:absolute;left:{LM:.2f}mm;right:{LM:.2f}mm;top:{bottom+4.5:.1f}mm;margin:0;font:7pt/1.35 Helvetica,Arial,sans-serif;color:#333}}
</style></head><body>{page(False)}{page(True)}{page(False, back=True)}</body></html>'''
open('sheet.html','w').write(html)
print('cards end at',bottom,'mm; caption starts',bottom+4.5)
