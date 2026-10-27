
"""Draws the abstract placeholder portraits (no face): an isometric cube emblem.
Replace portrait/id.png and portrait/right_pointing.png with the real ones and re-run build.py."""
import math, asyncio, pathlib
from playwright.async_api import async_playwright
HERE=pathlib.Path(__file__).parent
def cube(cx,cy,s,gap=.09):
    c30,s30=math.cos(math.radians(30))*s, math.sin(math.radians(30))*s
    def P(x,y,z): return (cx+(x-y)*c30, cy+(x+y-3)*s30-(z-1.5)*s)
    cols={'top':['#eef3ff','#cfe0ff','#eef3ff','#ffffff','#9fc3ff','#eef3ff','#cfe0ff','#eef3ff','#ffffff'],
          'left':['#247bff','#1a5fd0','#3d8bff','#247bff','#1648a8','#247bff','#3d8bff','#247bff','#1a5fd0'],
          'right':['#ff354f','#d92a43','#ff5d72','#c21f37','#ff354f','#ff5d72','#ff354f','#d92a43','#ff354f']}
    out=[];k=0;g=gap/2
    for i in range(3):
        for j in range(3):
            q=[(i+g,j+g),(i+1-g,j+g),(i+1-g,j+1-g),(i+g,j+1-g)]
            out.append((cols['top'][k],[P(a,b,3) for a,b in q]))
            out.append((cols['left'][k],[P(a,3,3-b) for a,b in q]))
            out.append((cols['right'][k],[P(3,a,3-b) for a,b in q]))
            k+=1
    base=[P(0,0,3),P(3,0,3),P(3,0,0),P(3,3,0),P(0,3,0),P(0,3,3)]
    under=f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in base)}" fill="#070b16"/>'
    return under+''.join(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="{c}" rx="4"/>' for c,pts in out)
def svg(kind):
    W,H=(720,720) if kind=='id' else (900,760)
    cx,cy=(360,420) if kind=='id' else (300,400)
    s=72 if kind=='id' else 70
    body=cube(cx,cy,s)
    extra=''
    if kind=='right_pointing':
        for n in range(3):
            x=560+n*92; extra+=f'<path d="M{x} 330 l58 70 l-58 70" fill="none" stroke="#ff354f" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" opacity="{.45+.27*n:.2f}"/>'
    shade=f'<ellipse cx="{cx}" cy="{cy+s*2.4}" rx="{s*2.9}" ry="{s*.7}" fill="#000" opacity=".35" filter="url(#b)"/>'
    mono=f'<text x="{cx}" y="{cy+s*3.55}" text-anchor="middle" font-family="DejaVu Sans, Arial" font-weight="700" font-size="{s*1.05:.0f}" letter-spacing="{s*.12:.0f}" fill="#eef3ff" opacity=".92">T · B</text>' if kind=='id' else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><filter id="b"><feGaussianBlur stdDeviation="14"/></filter></defs>{shade}<g stroke="#070b16" stroke-width="3" stroke-linejoin="round">{body}</g>{extra}{mono}</svg>'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for kind in ['id','right_pointing']:
            s=svg(kind); W=int(s.split('width="')[1].split('"')[0]); H=int(s.split('height="')[1].split('"')[0])
            pg=await b.new_page(viewport={'width':W,'height':H})
            await pg.set_content(f"<html><body style='margin:0;background:transparent'>{s}</body></html>")
            await pg.screenshot(path=str(HERE/'portrait'/f'{kind}.png'),omit_background=True,clip={'x':0,'y':0,'width':W,'height':H})
        await b.close()
asyncio.run(main())
