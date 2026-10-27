#!/usr/bin/env python3
"""Builds Tanay's five GitHub-safe animated SVGs from identity.json + portrait PNGs.
Usage: python3 source/build.py   (needs: pip install fonttools brotli pillow)
Every SVG is self-contained: inline PNG + base64 WOFF2 fonts, CSS + SMIL only."""
import base64, io, json, math, re, html
from pathlib import Path
from PIL import Image
from fontTools.ttLib import TTFont
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; OUT=ROOT/'assets'; OUT.mkdir(exist_ok=True)
D=json.loads((HERE/'identity.json').read_text())
NAVY='#070b16'; BLUE='#247bff'; RED='#ff354f'; INK='#eef3ff'; MUTED='#8e9db9'; SOFT='#b6c5dd'; LINE='#223149'
FONT_D=HERE/'fonts/SpaceGrotesk-700.woff2'; FONT_M=HERE/'fonts/JetBrainsMono-400.woff2'
b64=lambda p: base64.b64encode(Path(p).read_bytes()).decode()
FD,FM=b64(FONT_D),b64(FONT_M)
_tt={k:TTFont(str(v)) for k,v in (('d',FONT_D),('m',FONT_M))}
def tw(text,size,font='d',ls=0):
    f=_tt[font]; cmap=f.getBestCmap(); hm=f['hmtx']; upm=f['head'].unitsPerEm
    w=sum(hm[cmap.get(ord(ch),cmap.get(32))][0] for ch in text)
    return w*size/upm+ls*max(len(text)-1,0)
e=lambda s: html.escape(str(s),quote=True)
ICON_COL=json.loads((HERE/'icons/colors.json').read_text())
def icon_path(slug): return re.search(r' d="([^"]+)"',(HERE/f'icons/{slug}.svg').read_text()).group(1)
def icon_title(slug): return re.search(r'<title>([^<]+)</title>',(HERE/f'icons/{slug}.svg').read_text()).group(1)
def icon_fill(slug):
    c='#'+(ICON_COL.get(slug) or 'eef3ff')
    r,g,b=(int(c[i:i+2],16) for i in (1,3,5))
    lum=(0.2126*r+0.7152*g+0.0722*b)/255
    return INK if lum<0.22 else c   # dark brand marks (Next.js, Vercel, GitHub, X, NumPy, pandas) go off-white on navy
def icon(slug,x,y,size,fill=None):
    s=size/24
    return f'<path transform="translate({x:.1f} {y:.1f}) scale({s:.4f})" d="{icon_path(slug)}" fill="{fill or icon_fill(slug)}"/>'
def png_data(path,max_h):
    im=Image.open(path).convert('RGBA'); bb=im.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
    if bb: im=im.crop(bb)
    if im.height>max_h: im=im.resize((round(im.width*max_h/im.height),max_h),Image.Resampling.LANCZOS)
    buf=io.BytesIO(); im.save(buf,'PNG',optimize=True)
    return im.width,im.height,base64.b64encode(buf.getvalue()).decode()
def portrait(ns,path,box,max_h=900,anchor='bottom',cls=''):
    """fit a transparent PNG into box=(x,y,w,h); anchored bottom-centre."""
    x,y,w,h=box; iw,ih,data=png_data(path,max_h)
    sc=min(w/iw,h/ih); dw,dh=iw*sc,ih*sc
    dx=x+(w-dw)/2; dy=y+h-dh if anchor=='bottom' else y+(h-dh)/2
    return f'<image class="{cls}" x="{dx:.1f}" y="{dy:.1f}" width="{dw:.1f}" height="{dh:.1f}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{data}"/>',(dx,dy,dw,dh)
def css(extra=''):
    return ('<style>'
     f'@font-face{{font-family:"TBDisplay";font-weight:700;src:url(data:font/woff2;base64,{FD}) format("woff2")}}'
     f'@font-face{{font-family:"TBMono";font-weight:400;src:url(data:font/woff2;base64,{FM}) format("woff2")}}'
     'text{font-family:"TBDisplay","Segoe UI",Arial,sans-serif;font-weight:700;fill:#eef3ff}'
     '.m{font-family:"TBMono",Consolas,monospace;font-weight:400}'
     '.enter{animation:tb-enter .9s cubic-bezier(.16,1,.3,1) both}'
     '.fade{animation:tb-fade 1.2s ease-out both}'
     '.pulse{animation:tb-pulse 2.4s ease-in-out infinite both}'
     '.blink{animation:tb-blink 1s steps(2,end) infinite both}'
     '.float{animation:tb-float 6s ease-in-out infinite both}'
     '.nudge{animation:tb-nudge 2.6s ease-in-out infinite both}'
     '.still{display:none}'
     '@keyframes tb-enter{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}'
     '@keyframes tb-fade{from{opacity:0}to{opacity:1}}'
     '@keyframes tb-pulse{0%,100%{opacity:1}50%{opacity:.3}}'
     '@keyframes tb-blink{50%{opacity:0}}'
     '@keyframes tb-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}'
     '@keyframes tb-nudge{0%,62%,100%{transform:translateX(0)}80%{transform:translateX(9px)}}'
     + extra +
     '@media (prefers-reduced-motion:reduce){*{animation:none!important}.motion{display:none!important}.still{display:inline!important}}'
     '</style>')
def delay(s): return f' style="animation-delay:{s}s"'
def defs(ns,W,H):
    return f"""<defs>
<linearGradient id="{ns}-hair" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{BLUE}" stop-opacity=".75"/><stop offset=".5" stop-color="#4d6a93" stop-opacity=".22"/><stop offset="1" stop-color="{RED}" stop-opacity=".7"/></linearGradient>
<linearGradient id="{ns}-aurora" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#9ccbff"/><stop offset=".5" stop-color="{BLUE}"/><stop offset="1" stop-color="#1a44c4"/></linearGradient>
<linearGradient id="{ns}-flare" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{BLUE}"/><stop offset="1" stop-color="{RED}"/></linearGradient>
<radialGradient id="{ns}-halo"><stop stop-color="#1266ed" stop-opacity=".36"/><stop offset="1" stop-color="#1266ed" stop-opacity="0"/></radialGradient>
<radialGradient id="{ns}-rhalo"><stop stop-color="#ff1c3f" stop-opacity=".22"/><stop offset="1" stop-color="#ff1c3f" stop-opacity="0"/></radialGradient>
<linearGradient id="{ns}-card" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#101a31"/><stop offset="1" stop-color="#0a1122"/></linearGradient>
<linearGradient id="{ns}-fadeb" x1="0" y1="0" x2="0" y2="1"><stop offset=".72" stop-color="{NAVY}" stop-opacity="0"/><stop offset="1" stop-color="{NAVY}"/></linearGradient>
<pattern id="{ns}-dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".75" fill="#9fb4dc" opacity=".14"/></pattern>
<filter id="{ns}-glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="7"/></filter>
<filter id="{ns}-shadow" x="-40%" y="-30%" width="180%" height="170%"><feDropShadow dx="0" dy="16" stdDeviation="16" flood-color="#000" flood-opacity=".65"/></filter>
<clipPath id="{ns}-outer"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="24"/></clipPath>
</defs>"""
def frame(ns,W,H):
    return (f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="24" fill="{NAVY}"/>'
            f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="24" fill="url(#{ns}-dots)"/>')
def border(ns,W,H): return f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="24" fill="none" stroke="url(#{ns}-hair)" stroke-width="1.5"/>'
def head(ns,W,H,title,desc):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="{ns}-t {ns}-d">'
            f'<title id="{ns}-t">{e(title)}</title><desc id="{ns}-d">{e(desc)}</desc>')
def T(x,y,s,size,fill=INK,cls='',anchor='start',ls=0,extra=''):
    a='' if anchor=='start' else f' text-anchor="{anchor}"'
    l=f' letter-spacing="{ls}"' if ls else ''
    c=f' class="{cls}"' if cls else ''
    st='' if 'style=' in extra else f' style="fill:{fill}"'
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{st}{a}{l}{c}{extra}>{e(s)}</text>'
def slashes(x,y,n=3,c=RED,h=18):
    return ''.join(f'<path d="M{x+i*12} {y}h9l-7 {h}h-9z" fill="{c}"/>' for i in range(n))
def cube_mark(x,y,s,op=1):
    """small isometric cube glyph (Tanay's Rubik's-cube motif), top vertex at x,y"""
    c=math.cos(math.radians(30))*s; h=s/2
    return (f'<g opacity="{op}"><path d="M{x} {y}l{c:.1f} {h}l-{c:.1f} {h}l-{c:.1f} -{h}z" fill="#cfe0ff"/>'
            f'<path d="M{x-c:.1f} {y+h}l{c:.1f} {h}v{s}l-{c:.1f} -{h}z" fill="{BLUE}"/>'
            f'<path d="M{x+c:.1f} {y+h}l-{c:.1f} {h}v{s}l{c:.1f} -{h}z" fill="{RED}"/></g>')
def save(name,svg):
    assert '<script' not in svg and 'foreignObject' not in svg
    assert not re.search(r'(?:href|src|url\()\s*=?\s*["\']?(?:https?:)?//',svg), 'external ref in '+name
    (OUT/name).write_text(svg); print(name, round(len(svg)/1024),'KB')

def hero():
    ns='hero'; W,H=1200,640
    roles=D['roles']; n=len(roles); per=4.0; dur=per*n
    first,last=D['name_first'],D['name_last']
    # name sizing: fit the longer word into 600px
    size=min(150, int(600/max(tw(first,1,ls=0),tw(last,1))))
    pimg,(px,py,pw,ph)=portrait(ns,HERE/'portrait/id.png',(690,132,460,508),max_h=760)
    pcx=px+pw/2; pcy=330
    s=[head(ns,W,H,f"{D['full_name']} — hero",f"Hi, I'm {D['full_name']}. {' / '.join(roles)}. {D['edu_line']}, {D['college']}, {D['location']}."),
       css('.ring{transform-origin:%dpx %dpx}'%(pcx,pcy)), defs(ns,W,H)]
    tw_hi=tw("Hi there, I'm",18,'m')+8
    steps=8; vals=';'.join(['0','0']+[f'{tw_hi*i/steps:.0f}' for i in range(1,steps+1)])
    kts=';'.join(['0','.08']+[f'{.08+.84*i/steps:.3f}' for i in range(1,steps+1)])
    s.append(f'<defs><clipPath id="{ns}-typing"><rect x="40" y="152" width="{tw_hi:.0f}" height="34"><animate attributeName="width" begin="0s" dur="1.5s" values="{vals}" keyTimes="{kts}" calcMode="discrete" fill="freeze"/></rect></clipPath>'
             f'<mask id="{ns}-reveal" maskUnits="userSpaceOnUse" x="20" y="170" width="680" height="290"><rect x="20" y="170" width="680" height="290" fill="#fff"><animate attributeName="y" begin="0s" dur="1.7s" values="460;460;170" keyTimes="0;.18;1" calcMode="spline" keySplines="0 0 1 1;.16 1 .3 1" fill="freeze"/></rect></mask>'
             f'<clipPath id="{ns}-pclip"><rect x="640" y="0" width="560" height="640"/></clipPath></defs>')
    s.append(f'<g clip-path="url(#{ns}-outer)">'+frame(ns,W,H))
    s.append(f'<ellipse cx="{pcx:.0f}" cy="320" rx="420" ry="400" fill="url(#{ns}-halo)"/><ellipse cx="1190" cy="80" rx="300" ry="360" fill="url(#{ns}-rhalo)"/>')
    for i in range(8): s.append(f'<path d="M{640+i*84} 96 L{330+i*84} 640" stroke="#193057" stroke-width="1.4" opacity=".28"/>')
    # orbit rings around portrait
    for r,c,d,dash in ((228,BLUE,26,90),(250,RED,40,70)):
        circ=2*math.pi*r
        s.append(f'<circle cx="{pcx:.0f}" cy="{pcy}" r="{r}" fill="none" stroke="{c}" opacity=".15"/>'
                 f'<circle class="motion" cx="{pcx:.0f}" cy="{pcy}" r="{r}" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="{dash} {circ-dash:.1f}">'
                 f'<animateTransform attributeName="transform" type="rotate" begin="0s" dur="{d}s" values="0 {pcx:.0f} {pcy};360 {pcx:.0f} {pcy}" repeatCount="indefinite"/></circle>')
    # floating cubes
    for (x,y,sz,op,dl) in ((1112,150,13,.9,0),(724,520,10,.7,1.5),(1130,470,8,.55,3)):
        s.append(f'<g class="float"{delay(dl)}>{cube_mark(x,y,sz,op)}</g>')
    # top bar
    s.append(f'<path d="M42 76H1158" stroke="{LINE}" stroke-width="1.5"/>')
    s.append(cube_mark(56,30,11))
    s.append(T(80,46,f"TB / {' · '.join(r.upper() for r in roles)}",12.5,MUTED,'m',ls=1.6))
    loc=f"{D['location'].upper()} · {D['country']}"
    s.append(T(1100-tw(loc,12.5,'m',1.6),46,loc,12.5,MUTED,'m',ls=1.6)+slashes(1124,31,3,RED,16))
    # status pill
    pw_=tw(D['status'],11,'m',1)+58
    s.append(f'<g class="enter"><rect x="44" y="102" width="{pw_:.0f}" height="30" rx="7" fill="#122c49"/><circle cx="{44+pw_-17:.0f}" cy="117" r="4.5" fill="#3ddc97" class="pulse"/><circle cx="{44+pw_-17:.0f}" cy="117" r="9" fill="#3ddc97" opacity=".18"/>'
             + T(58,121,D['status'],11,INK,'m',ls=1)+'</g>')
    s.append(T(45,178,"Hi there, I'm",18,SOFT,'m',extra=f' clip-path="url(#{ns}-typing)"'))
    s.append(f'<rect x="{45+tw_hi-4:.0f}" y="162" width="9" height="20" fill="{RED}" class="blink"/>')
    s.append(f'<g mask="url(#{ns}-reveal)">'+T(38,170+size*0.82,first,size,INK,ls=0)+T(40,170+size*0.82+size*0.84,last,size,f'url(#{ns}-aurora)',ls=0,extra=f' style="fill:url(#{ns}-aurora)"')+'</g>')
    ytop=170+size*0.82+size*0.84
    # roles cycle
    ry=ytop+58
    s.append(T(44,ry,'>',26,RED,'m'))
    for i,r in enumerate(roles):
        a,b=i/n,(i+1)/n; fi=.04/n*n*0.25
        if n==1:
            vals,kt='1;1','0;1'
        elif i==0:
            vals='1;1;0;0;1'; kt=f'0;{b-0.03:.3f};{b:.3f};{1-0.03:.3f};1'
        else:
            vals='0;0;1;1;0;0'; kt=f'0;{a-0.03:.3f};{a:.3f};{b-0.03:.3f};{b:.3f};1' if b<1 else None
            if b>=1: vals='0;0;1;1;0'; kt=f'0;{a-0.03:.3f};{a:.3f};{1-0.03:.3f};1'
        base='1' if i==0 else '0'
        s.append(f'<g class="motion" opacity="{base}"><animate attributeName="opacity" begin="0s" dur="{dur}s" values="{vals}" keyTimes="{kt}" repeatCount="indefinite"/>'
                 f'<g><animateTransform attributeName="transform" type="translate" begin="0s" dur="{dur}s" values="0 14;0 14;0 0;0 0;0 -10" keyTimes="0;{a:.3f};{a+0.04:.3f};{max(b-0.04,a+0.05):.3f};{b:.3f}" repeatCount="indefinite"/>'
                 + T(76,ry,r,30,INK)+f'<rect x="{78+tw(r,30):.0f}" y="{ry-24}" width="3" height="28" fill="{BLUE}" class="blink"/></g></g>')
    s.append(f'<g class="still">'+T(76,ry,' / '.join(roles),30,INK)+'</g>')
    # pitch
    for i,line in enumerate(D['pitch']):
        s.append(f'<g class="enter"{delay(1.1+i*.12)}>'+T(46,ry+44+i*24,line,15,SOFT,'m')+'</g>')
    # bottom chips
    chips=[D['edu_line'],D['college']]
    x=44; cy_=ry+44+len(D['pitch'])*24+26
    for i,c in enumerate(chips):
        w=tw(c,12,'m')+28
        s.append(f'<g class="enter"{delay(1.4+i*.12)}><rect x="{x}" y="{cy_}" width="{w:.0f}" height="30" rx="15" fill="#0f1b33" stroke="{["#2a5cad","#7a2a3f"][i%2]}"/>'+T(x+14,cy_+20,c,12,INK,'m')+'</g>')
        x+=w+10
    # portrait
    s.append(f'<defs><radialGradient id="{ns}-pfade" cx=".5" cy=".36" r=".66"><stop offset=".72" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>'
             f'<mask id="{ns}-pmask" maskUnits="userSpaceOnUse" x="{px-2:.0f}" y="{py-2:.0f}" width="{pw+4:.0f}" height="{ph+4:.0f}"><rect x="{px-2:.0f}" y="{py-2:.0f}" width="{pw+4:.0f}" height="{ph+4:.0f}" fill="url(#{ns}-pfade)"/></mask></defs>')
    s.append(f'<g class="fade"{delay(.3)}><g mask="url(#{ns}-pmask)">{pimg}</g></g>')
    s.append(f'<rect x="640" y="520" width="560" height="120" fill="url(#{ns}-fadeb)"/>')
    s.append('</g>'+border(ns,W,H)+'</svg>')
    save('hero.svg',''.join(s))

def illo(kind,cx,cy,ns):
    """vector illustrations for the interests carousel"""
    if kind=='code':
        x,y=cx-150,cy-95; o=[f'<rect x="{x}" y="{y}" width="300" height="190" rx="14" fill="#0b1427" stroke="#2a4a80"/>',
           f'<path d="M{x} {y+14}a14 14 0 0 1 14-14h272a14 14 0 0 1 14 14v18H{x}z" fill="#13213e"/>']
        o+= [f'<circle cx="{x+18+i*16}" cy="{y+16}" r="4.5" fill="{c}"/>' for i,c in enumerate((RED,'#f5b544','#3ddc97'))]
        lines=[("const","#ff7a8c",[(" build ",INK),("= ","#8e9db9"),("() =>",BLUE)]),("  ship","#7fb2ff",[("(idea)",INK)]),("  learn","#7fb2ff",[("()",INK),(";",MUTED)]),("  repeat","#7fb2ff",[("();",INK)])]
        for i,(k,kc,rest) in enumerate(lines):
            yy=y+62+i*28; xx=x+22
            seg=f'<tspan style="fill:{kc}">{e(k)}</tspan>'+''.join(f'<tspan style="fill:{c}">{e(t)}</tspan>' for t,c in rest)
            o.append(f'<g class="type-{i}"><text x="{xx}" y="{yy}" font-size="15" class="m">{seg}</text></g>')
        o.append(f'<rect x="{x+22}" y="{y+160}" width="9" height="16" fill="{RED}" class="blink"/>')
        return ''.join(o)
    if kind=='pad':
        g=[f'<g transform="translate({cx} {cy})">',
           '<path d="M-118 -38c-40 0-62 40-66 92-3 40 14 66 40 66 22 0 34-20 50-44h188c16 24 28 44 50 44 26 0 43-26 40-66-4-52-26-92-66-92z" fill="#13213e" stroke="#2a4a80" stroke-width="2"/>',
           f'<rect x="-97" y="-8" width="16" height="50" rx="4" fill="{BLUE}"/><rect x="-114" y="9" width="50" height="16" rx="4" fill="{BLUE}"/>',
           f'<circle cx="90" cy="-4" r="11" fill="{RED}" class="pulse"/><circle cx="114" cy="18" r="11" fill="#f5b544" class="pulse" style="animation-delay:.6s"/><circle cx="66" cy="18" r="11" fill="#3ddc97" class="pulse" style="animation-delay:1.2s"/><circle cx="90" cy="40" r="11" fill="#7fb2ff" class="pulse" style="animation-delay:1.8s"/>',
           '<circle cx="-34" cy="48" r="20" fill="#0b1427" stroke="#2a4a80"/><circle cx="34" cy="48" r="20" fill="#0b1427" stroke="#2a4a80"/>',
           '<rect x="-22" y="-20" width="16" height="8" rx="3" fill="#2a4a80"/><rect x="8" y="-20" width="16" height="8" rx="3" fill="#2a4a80"/></g>']
        return ''.join(g)
    if kind=='map':
        pts=[(cx-150,cy+60),(cx-60,cy-40),(cx+40,cy+30),(cx+150,cy-60)]
        d=f'M{pts[0][0]} {pts[0][1]} C{cx-120} {cy-40} {cx-90} {cy-60} {pts[1][0]} {pts[1][1]} S{cx+10} {cy+50} {pts[2][0]} {pts[2][1]} S{cx+110} {cy-30} {pts[3][0]} {pts[3][1]}'
        o=[f'<path d="M{cx-170} {cy-90}l110 -20 120 20 110 -20v200l-110 20 -120 -20 -110 20z" fill="#0b1427" stroke="#2a4a80"/>',
           f'<path d="M{cx-60} {cy-110}v200M{cx+60} {cy-90}v200" stroke="#1d3157"/>',
           f'<path d="{d}" fill="none" stroke="#2a4a80" stroke-width="3" stroke-dasharray="2 9" stroke-linecap="round"/>',
           f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="3" stroke-linecap="round" stroke-dasharray="600" stroke-dashoffset="0"><animate attributeName="stroke-dashoffset" begin="0s" dur="4s" values="600;0;0" keyTimes="0;.7;1" repeatCount="indefinite"/></path>']
        for (x,y) in pts[1:3]: o.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{BLUE}"/><circle cx="{x}" cy="{y}" r="12" fill="{BLUE}" opacity=".2"/>')
        x,y=pts[3]; o.append(f'<path d="M{x} {y+4}c-14-18-20-26-20-36a20 20 0 0 1 40 0c0 10-6 18-20 36z" fill="{RED}"/><circle cx="{x}" cy="{y-32}" r="7" fill="{NAVY}"/>')
        x,y=pts[0]; o.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{INK}"/>')
        return ''.join(o)
    return ''
def about():
    ns='about'; W,H=1200,600
    s=[head(ns,W,H,f"{D['full_name']} — about","What I do: "+'; '.join(c[0]+' — '+c[1] for c in D['capabilities'])+". Beyond the screen: "+', '.join(i[1].title() for i in D['interests'])+'.'),
       css(''.join(f'.type-{i}{{animation:tb-fade .5s ease-out both;animation-delay:{.4+i*.35}s}}' for i in range(4))),defs(ns,W,H)]
    s.append(f'<g clip-path="url(#{ns}-outer)">'+frame(ns,W,H))
    s.append(f'<ellipse cx="900" cy="300" rx="360" ry="300" fill="url(#{ns}-halo)"/><ellipse cx="80" cy="600" rx="300" ry="200" fill="url(#{ns}-rhalo)"/>')
    s.append(T(44,58,'02 / ABOUT',12.5,MUTED,'m',ls=1.6)+slashes(44+tw('02 / ABOUT',12.5,'m',1.6)+18,45,3,RED,15))
    s.append(f'<g class="enter">'+T(42,120,'WHAT I DO',54,INK,ls=0.5)+'</g>')
    y=168
    for i,(t,d) in enumerate(D['capabilities']):
        assert tw(d,13,'m')<=500, 'capability line too long: '+d
        yy=y+i*98
        s.append(f'<g class="enter"{delay(.25+i*.12)}><path d="M44 {yy}H580" stroke="{LINE}"/>'
                 + T(44,yy+40,f'0{i+1}',13,[BLUE,RED][i%2],'m',ls=1)
                 + T(92,yy+42,t,26,INK)+T(92,yy+70,d,13,SOFT,'m')+'</g>')
    s.append(f'<path d="M44 {y+4*98}H580" stroke="{LINE}"/>')
    # carousel card
    cx0,cy0,cw,chh=632,40,524,520
    s.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{chh}" rx="22" fill="url(#{ns}-card)" stroke="url(#{ns}-hair)" filter="url(#{ns}-shadow)"/>')
    s.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{chh}" rx="22" fill="url(#{ns}-dots)"/>')
    s.append(T(cx0+28,cy0+42,'BEYOND THE SCREEN',12.5,MUTED,'m',ls=1.6))
    n=len(D['interests']); per=4; dur=per*n
    bw=(cw-56-(n-1)*10)/n
    for i in range(n):
        bx=cx0+28+i*(bw+10); a,b=i/n,(i+1)/n
        s.append(f'<rect x="{bx:.1f}" y="{cy0+62}" width="{bw:.1f}" height="4" rx="2" fill="#1f2d48"/>')
        base=f'{bw:.1f}' if i==0 else '0'
        vals=f'0;0;{bw:.1f};{bw:.1f}' if i>0 else f'0;{bw:.1f};{bw:.1f}'
        kt=f'0;{a:.4f};{b:.4f};1' if i>0 else f'0;{b:.4f};1'
        if i>0 and b>=1: vals=f'0;0;{bw:.1f}'; kt=f'0;{a:.4f};1'
        s.append(f'<rect x="{bx:.1f}" y="{cy0+62}" width="{base}" height="4" rx="2" fill="url(#{ns}-flare)"><animate attributeName="width" begin="0s" dur="{dur}s" values="{vals}" keyTimes="{kt}" repeatCount="indefinite"/></rect>')
    for i,(num,title,l1,l2,kind) in enumerate(D['interests']):
        a,b=i/n,(i+1)/n; f=.025
        if i==0: vals='1;1;0;0;1'; kt=f'0;{b-f:.4f};{b:.4f};{1-f:.4f};1'
        elif b<1: vals='0;0;1;1;0;0'; kt=f'0;{a-f:.4f};{a:.4f};{b-f:.4f};{b:.4f};1'
        else: vals='0;0;1;1;0'; kt=f'0;{a-f:.4f};{a:.4f};{1-f:.4f};1'
        base='1' if i==0 else '0'
        g=(f'<g opacity="{base}" class="{"" if i==0 else "motion"}"><animate attributeName="opacity" begin="0s" dur="{dur}s" values="{vals}" keyTimes="{kt}" repeatCount="indefinite"/>'
           + illo(kind,cx0+cw/2,cy0+210,ns)
           + T(cx0+28,cy0+390,num,13,[BLUE,RED,BLUE][i%3],'m',ls=1)
           + T(cx0+70,cy0+392,f'/ {n:02d}',13,MUTED,'m')
           + T(cx0+28,cy0+440,title,42,INK,ls=.5)
           + T(cx0+28,cy0+472,l1+' '+l2 if tw(l1+' '+l2,14,'m')<cw-56 else l1,14,SOFT,'m')
           + ('' if tw(l1+' '+l2,14,'m')<cw-56 else T(cx0+28,cy0+494,l2,14,SOFT,'m'))
           + '</g>')
        s.append(g)
    s.append('</g>'+border(ns,W,H)+'</svg>')
    save('about-life.svg',''.join(s))

def icon_badge(slug,x,y,r=23,label=True):
    col=icon_fill(slug)
    o=(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#0e1830" stroke="{col}" stroke-opacity=".55" stroke-width="1.5"/>'
       + icon(slug,x-r*0.5,y-r*0.5,r))
    if label: o+=T(x,y+r+16,icon_title(slug),12,SOFT,'m',anchor='middle')
    return o
def stack():
    ns='stack'; W,H=1200,640
    allslugs=[s_ for g in D['stack_groups'] for s_ in g[1]]
    s=[head(ns,W,H,f"{D['full_name']} — tech stack","Stack: "+'; '.join(g[0].title()+': '+', '.join(icon_title(x) for x in g[1]) for g in D['stack_groups'])+'.'),
       css('.core{transform-origin:318px 402px;animation:tb-core 4s ease-in-out infinite both}@keyframes tb-core{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}'),defs(ns,W,H)]
    s.append(f'<g clip-path="url(#{ns}-outer)">'+frame(ns,W,H))
    cx,cy=318,402
    s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="330" ry="300" fill="url(#{ns}-halo)"/><ellipse cx="1150" cy="40" rx="260" ry="220" fill="url(#{ns}-rhalo)"/>')
    s.append(T(44,58,'03 / STACK',12.5,MUTED,'m',ls=1.6)+slashes(44+tw('03 / STACK',12.5,'m',1.6)+18,45,3,RED,15))
    s.append(f'<g class="enter">'+T(42,118,'TOOLS I SHIP WITH',44,INK,ls=.5)+'</g>')
    orbits=D['orbits']; spec=[(112,58,-12,24),(190,104,9,36),(262,150,-5,50)]
    for oi,(rx,ry,tilt,dur) in enumerate(spec):
        col=[BLUE,'#5d78a8',RED][oi]
        s.append(f'<g transform="translate({cx} {cy}) rotate({tilt})"><ellipse rx="{rx}" ry="{ry}" fill="none" stroke="{col}" stroke-opacity=".4" stroke-width="1.3" stroke-dasharray="{"4 6" if oi==1 else "none"}"/></g>')
    # core
    s.append(f'<g class="core"><circle cx="{cx}" cy="{cy}" r="46" fill="{BLUE}" opacity=".25" filter="url(#{ns}-glow)"/><circle cx="{cx}" cy="{cy}" r="40" fill="#0e1830" stroke="url(#{ns}-hair)" stroke-width="2"/>{cube_mark(cx,cy-24,16)}</g>')
    for oi,(rx,ry,tilt,dur) in enumerate(spec):
        items=orbits[oi]; n=len(items)
        th=math.radians(tilt)
        for k,slug in enumerate(items):
            a0=2*math.pi*k/n+oi*0.6
            px,py=rx*math.cos(a0),ry*math.sin(a0)
            # world position of start point
            wx=cx+px*math.cos(th)-py*math.sin(th); wy=cy+px*math.sin(th)+py*math.cos(th)
            # path relative to start point, in the tilted frame
            qx,qy=-2*px,-2*py
            path=f'M0 0A{rx} {ry} 0 1 1 {qx:.2f} {qy:.2f}A{rx} {ry} 0 1 1 0 0'
            badge=f'<g transform="rotate({-tilt})">{icon_badge(slug,0,0,21)}</g>'
            s.append(f'<g class="motion" transform="translate({cx} {cy}) rotate({tilt}) translate({px:.2f} {py:.2f})"><g>{badge}<animateMotion begin="0s" dur="{dur}s" repeatCount="indefinite" path="{path}"/></g></g>')
            s.append(f'<g class="still">{icon_badge(slug,wx,wy,21)}</g>')
    # chips
    x0=640; y=160
    for gi,(gname,slugs) in enumerate(D['stack_groups']):
        s.append(f'<g class="enter"{delay(.2+gi*.15)}>'+T(x0,y,gname,11,[BLUE,RED,MUTED][gi%3],'m',ls=1.6)+f'<path d="M{x0+tw(gname,11,"m",1.6)+12:.0f} {y-4}H1156" stroke="{LINE}"/>')
        x=x0; y+=16
        for slug in slugs:
            lab=icon_title(slug); w=tw(lab,13,'m')+56
            if x+w>1156: x=x0; y+=46
            s.append(f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="38" rx="11" fill="#0e1830" stroke="#22365c"/>'+icon(slug,x+13,y+10,18)+T(x+40,y+24,lab,13,INK,'m'))
            x+=w+10
        s.append('</g>'); y+=38+44
    s.append('</g>'+border(ns,W,H)+'</svg>')
    save('stack.svg',''.join(s))

if __name__=='__main__':
    hero(); about(); stack()

LANG_COL={'TypeScript':'#3178c6','JavaScript':'#f1e05a','CSS':'#663399','C':'#8a9bb3','Python':'#3572A5','HTML':'#e34c26'}
def id_dash():
 ns='idd';W,H=1200,680; G=D['github_snapshot']; ox=290
 cssx=(f'.drop{{transform-origin:{ox}px 0;animation:tb-drop 1.15s cubic-bezier(.2,1.3,.4,1) both}}'
       f'.damp{{transform-origin:{ox}px 0;animation:tb-damp 4.6s ease-out .6s both}}'
       f'.swing{{transform-origin:{ox}px 0;animation:tb-swing 6s ease-in-out 5.2s infinite both}}'
       '@keyframes tb-drop{from{transform:translateY(-720px)}to{transform:none}}'
       '@keyframes tb-damp{0%{transform:rotate(0)}12%{transform:rotate(7deg)}30%{transform:rotate(-5deg)}48%{transform:rotate(3.4deg)}66%{transform:rotate(-2.3deg)}84%{transform:rotate(1.4deg)}100%{transform:rotate(-1.7deg)}}'
       '@keyframes tb-swing{0%,100%{transform:rotate(-1.7deg)}50%{transform:rotate(1.7deg)}}'
       '.sweep{animation:tb-sweep 6s ease-in-out 1.6s infinite both}@keyframes tb-sweep{0%{transform:translateX(-520px)}45%,100%{transform:translateX(520px)}}'
       '.bar{transform-box:fill-box;transform-origin:0 0;animation:tb-grow 1.4s cubic-bezier(.16,1,.3,1) both}@keyframes tb-grow{from{transform:scaleX(0)}to{transform:none}}')
 s=[head(ns,W,H,D['full_name']+' — builder ID and public dashboard',
  f"Builder ID: {D['full_name']}, {' / '.join(D['roles'])}, {D['edu_line']}, {D['college']}. Public GitHub snapshot {G['date']}: {G['public_repos']} public repositories, {G['live_products']} live products, on GitHub since {G['joined'].title()}."), css(cssx),defs(ns,W,H)]
 s.append(f'<defs><linearGradient id="{ns}-steel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e7efff"/><stop offset=".25" stop-color="#5a6a84"/><stop offset=".5" stop-color="#eef5ff"/><stop offset=".7" stop-color="#7d8fae"/><stop offset="1" stop-color="#26364d"/></linearGradient><linearGradient id="{ns}-strap" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#1a4fb8"/><stop offset="1" stop-color="{BLUE}"/></linearGradient><linearGradient id="{ns}-foil" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#9fd0ff" stop-opacity="0"/><stop offset=".42" stop-color="#9fd0ff" stop-opacity="0"/><stop offset=".5" stop-color="#e2f2ff" stop-opacity=".32"/><stop offset=".58" stop-color="{RED}" stop-opacity=".12"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient><clipPath id="{ns}-cardclip"><rect x="{ox-170}" y="214" width="340" height="440" rx="22"/></clipPath><clipPath id="{ns}-photoclip"><rect x="{ox-150}" y="282" width="128" height="150" rx="14"/></clipPath></defs>')
 s.append(f'<g clip-path="url(#{ns}-outer)">'+frame(ns,W,H))
 s.append(f'<ellipse cx="{ox}" cy="420" rx="320" ry="300" fill="url(#{ns}-halo)"/><ellipse cx="1180" cy="660" rx="300" ry="220" fill="url(#{ns}-rhalo)"/>')
 card=['<g class="drop"><g class="damp"><g class="swing">']
 card.append(f'<path d="M{ox-58} -10L{ox-12} 178" stroke="url(#{ns}-strap)" stroke-width="22"/><path d="M{ox+58} -10L{ox+12} 178" stroke="#c42a40" stroke-width="22"/>')
 card.append(f'<rect x="{ox-22}" y="168" width="44" height="22" rx="5" fill="url(#{ns}-steel)"/><rect x="{ox-9}" y="188" width="18" height="20" rx="3" fill="url(#{ns}-steel)"/><circle cx="{ox}" cy="214" r="11" fill="none" stroke="url(#{ns}-steel)" stroke-width="5"/>')
 cx0,cy0=ox-170,214
 card.append(f'<g filter="url(#{ns}-shadow)"><rect x="{cx0}" y="{cy0}" width="340" height="440" rx="22" fill="url(#{ns}-card)" stroke="url(#{ns}-hair)" stroke-width="1.5"/></g>')
 card.append(f'<g clip-path="url(#{ns}-cardclip)"><rect x="{cx0}" y="{cy0}" width="340" height="440" fill="url(#{ns}-dots)"/>')
 card.append(f'<rect x="{cx0}" y="{cy0}" width="340" height="50" fill="{BLUE}"/><rect x="{ox-26}" y="{cy0+10}" width="52" height="8" rx="4" fill="{NAVY}"/>')
 card.append(T(cx0+20,cy0+40,'BUILDER ID',13,INK,'m',ls=2)+T(cx0+320,cy0+40,'TB-001',13,INK,'m',anchor='end',ls=2))
 _cw,_ch,_cb=png_data(HERE/'portrait/id_card.png',450); pimg=f'<image x="{ox-150}" y="282" width="128" height="150" preserveAspectRatio="xMidYMid slice" href="data:image/png;base64,{_cb}"/>'
 card.append(f'<rect x="{ox-150}" y="282" width="128" height="150" rx="14" fill="#13213e"/><g clip-path="url(#{ns}-photoclip)">{pimg}</g><rect x="{ox-150}" y="282" width="128" height="150" rx="14" fill="none" stroke="#2a4a80"/>')
 card.append(T(ox-6,316,D['name_first'],30,INK)+T(ox-6,348,D['name_last'],30,f'url(#{ns}-aurora)'))
 for i,r in enumerate(D['roles']): card.append(T(ox-6,376+i*20,r.upper(),12,[BLUE,RED][i%2],'m',ls=1.2))
 for i,(k,v) in enumerate([('PROGRAM','B.Tech CSE (AI & ML)'),('COLLEGE',D['college']),('BASE',D['location'])]):
  yy=462+i*34
  card.append(f'<path d="M{cx0+20} {yy-18}H{cx0+320}" stroke="{LINE}"/>'+T(cx0+20,yy,k,11,MUTED,'m',ls=1.4)+T(cx0+100,yy,v,12,INK,'m'))
 xx=cx0+20;code=''.join(format(ord(ch),'08b') for ch in D['github'].upper())
 for bit in code:
  w=2.6 if bit=='1' else 1.2
  card.append(f'<rect x="{xx:.1f}" y="576" width="{w}" height="40" fill="{INK}" opacity="{.95 if bit=="1" else .55}"/>');xx+=w+1.6
 card.append(T(cx0+20,634,f"@{D['github'].upper()} · BUILDER",11,MUTED,'m',ls=1.6)+cube_mark(cx0+300,584,11))
 card.append(f'<rect class="sweep" x="{cx0-60}" y="{cy0}" width="460" height="440" fill="url(#{ns}-foil)"/></g></g></g></g>')
 s.append(''.join(card))
 dx=600
 s.append(T(dx,62,'04 / PUBLIC DASHBOARD',12.5,MUTED,'m',ls=1.6)+slashes(dx+tw('04 / PUBLIC DASHBOARD',12.5,'m',1.6)+18,49,3,RED,15))
 s.append(f'<g class="enter">'+T(dx-2,122,'BUILT IN PUBLIC',48,INK)+'</g>')
 s.append(T(dx,152,f"GITHUB SNAPSHOT · {G['date']} · PUBLIC API",12,SOFT,'m',ls=1.2))
 tiles=[(G['public_repos'],'PUBLIC REPOS'),(G['live_products'],'LIVE PRODUCTS'),(G['joined'],'ON GITHUB SINCE')]
 tw_=176
 for i,(v,lab) in enumerate(tiles):
  tx=dx+i*(tw_+14)
  s.append(f'<g class="enter"{delay(.3+i*.12)}><rect x="{tx}" y="180" width="{tw_}" height="112" rx="16" fill="url(#{ns}-card)" stroke="#22365c"/>'
    +f'<rect x="{tx}" y="180" width="4" height="112" rx="2" fill="{[BLUE,RED,BLUE][i]}"/>'
    +T(tx+22,248,str(v),46 if isinstance(v,int) else 30,INK)
    +T(tx+22,276,lab,12,MUTED,'m',ls=1.4)+'</g>')
 tot=sum(c for _,c in G['lang_counts']);bw=tw_*3+28;x=dx
 s.append(T(dx,334,'PRIMARY LANGUAGE BY REPO',12,MUTED,'m',ls=1.4)+'<g class="bar" style="animation-delay:.6s">')
 for lang,c in G['lang_counts']:
  w=bw*c/tot;s.append(f'<rect x="{x:.1f}" y="348" width="{w-3:.1f}" height="10" rx="5" fill="{LANG_COL.get(lang,"#888")}"/>');x+=w
 s.append('</g>');x=dx
 for lang,c in G['lang_counts']:
  lab=f'{lang} {c}';s.append(f'<circle cx="{x+5}" cy="379" r="5" fill="{LANG_COL.get(lang,"#888")}"/>'+T(x+16,383,lab,11.5,SOFT,'m'));x+=tw(lab,11.5,'m')+36
 s.append(T(dx,428,'REPOSITORIES',12,MUTED,'m',ls=1.4))
 for i,(name,lang,live) in enumerate(G['repos']):
  yy=446+i*42
  s.append(f'<g class="enter"{delay(.8+i*.1)}><rect x="{dx}" y="{yy}" width="{bw}" height="34" rx="10" fill="#0e1830" stroke="#1d2f52"/>'
   +icon('github',dx+12,yy+9,16,MUTED)+T(dx+38,yy+22,name,13,INK,'m')
   +f'<circle cx="{dx+bw-150}" cy="{yy+17}" r="5" fill="{LANG_COL.get(lang,"#888")}"/>'+T(dx+bw-140,yy+21,lang,11,SOFT,'m')
   +(f'<rect x="{dx+bw-52}" y="{yy+8}" width="42" height="18" rx="9" fill="#123a2b"/>'+T(dx+bw-31,yy+21,'LIVE',11,'#3ddc97','m',anchor='middle',ls=1) if live else '')+'</g>')
 s.append('</g>'+border(ns,W,H)+'</svg>');save('id-dashboard.svg',''.join(s))

def globe(x,y,s,c):
    k=s/24
    return (f'<g transform="translate({x} {y}) scale({k:.4f})" fill="none" stroke="{c}" stroke-width="1.8"><circle cx="12" cy="12" r="10"/>'
            '<ellipse cx="12" cy="12" rx="4.2" ry="10"/><path d="M2 12h20M4 6.5h16M4 17.5h16"/></g>')
LINKEDIN_IN='M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z'
def connect():
    ns='conn'; W,H=1200,640
    soc=D['socials']
    s=[head(ns,W,H,D['full_name']+" — let's connect","Let's build something real. "+'; '.join(f'{v[0]}: {v[1]}' for v in soc.values())+'. Clickable links are listed below this image.'),
       css('.pt{animation:tb-float 6s ease-in-out infinite both}'),defs(ns,W,H)]
    s.append(f'<g clip-path="url(#{ns}-outer)">'+frame(ns,W,H))
    s.append(f'<ellipse cx="270" cy="400" rx="360" ry="330" fill="url(#{ns}-halo)"/><ellipse cx="1180" cy="40" rx="300" ry="240" fill="url(#{ns}-rhalo)"/>')
    pimg,(px,py,pw,ph)=portrait(ns,HERE/'portrait/right_pointing.png',(10,70,560,570),max_h=640)
    s.append(f'<g class="fade"><g class="pt">{pimg}</g></g><rect x="0" y="560" width="600" height="80" fill="url(#{ns}-fadeb)"/>')
    x0=620
    s.append(T(x0,62,'05 / CONNECT',12.5,MUTED,'m',ls=1.6)+slashes(x0+tw('05 / CONNECT',12.5,'m',1.6)+18,49,3,RED,15))
    s.append(f'<g class="enter">'+T(x0-2,124,"LET'S BUILD",50,INK)+T(x0-2,178,'SOMETHING REAL.',50,f'url(#{ns}-aurora)')+'</g>')
    s.append(f'<g class="enter"{delay(.2)}>'+T(x0,212,'Open to collabs, projects and good conversations.',13.5,SOFT,'m')+'</g>')
    y=240; ch=66; gap=11; cw=1156-x0; hc=ch/2
    cols={'linkedin':'#0A66C2','instagram':'#FF0069','website':BLUE,'youtube':'#FF0000','gmail':'#EA4335'}
    for i,(k,(name,handle,url)) in enumerate(soc.items()):
        yy=y+i*(ch+gap); c=cols.get(k,BLUE)
        if k=='linkedin': ic=f'<path transform="translate({x0+30} {yy+hc-12}) scale({24/24})" d="{LINKEDIN_IN}" fill="{c}"/>'
        elif k=='website': ic=globe(x0+30,yy+hc-12,24,c)
        else: ic=icon(k,x0+30,yy+hc-12,24,c)
        s.append(f'<g class="enter"{delay(.35+i*.13)}><rect x="{x0}" y="{yy}" width="{cw}" height="{ch}" rx="18" fill="url(#{ns}-card)" stroke="#22365c"/>'
                 f'<rect x="{x0}" y="{yy+15}" width="4" height="{ch-30}" rx="2" fill="{c}"/>'
                 f'<circle cx="{x0+42}" cy="{yy+hc}" r="22" fill="{c}" opacity=".14"/>{ic}'
                 + T(x0+86,yy+hc-4,name,20,INK)+T(x0+86,yy+hc+17,handle,13,SOFT,'m')
                 + f'<g class="nudge"{delay(i*.35)}><circle cx="{x0+cw-40}" cy="{yy+hc}" r="17" fill="none" stroke="{c}" stroke-opacity=".6"/>'
                 f'<path d="M{x0+cw-47} {yy+hc}h13m-5-5 5 5-5 5" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g></g>')
    s.append('</g>'+border(ns,W,H)+'</svg>')
    save('connect.svg',''.join(s))
if __name__=='__main__': id_dash(); connect()

def readme_and_preview(v=8):
    import html as H
    P_=D['projects']; soc=D['socials']
    rows=[]; hrows=[]
    for name,live,code,desc,built in P_:
        cell=f"[**{name}**]({live or code})"+(f" · [code]({code})" if live and code else '')
        rows.append(f"| {cell} | {desc} | {built} |")
        hc=f'<a href="{H.escape(live or code)}"><b>{H.escape(name)}</b></a>'+(f' · <a href="{H.escape(code)}">code</a>' if live and code else '')
        hrows.append(f"<tr><td>{hc}</td><td>{H.escape(desc)}</td><td>{H.escape(built)}</td></tr>")
    links=[(f"{v_[0]}" if k in('linkedin',) else f"{v_[0]} — {v_[1]}",v_[2]) for k,v_ in soc.items()]
    links=[(n if not n.startswith('Email') else soc['gmail'][1],u) for n,u in links]+[(n,u) for n,u in D['extra_links'] if n!='GitHub']
    G=D['github_snapshot']; roles=' and '.join(D['roles'])
    alts={'hero':f"Hi, I'm {D['full_name']}: {roles}. {D['edu_line']}, {D['college']}, {D['location']}.",
      'about-life':"What I do: "+'; '.join(c[0] for c in D['capabilities'])+". Beyond the screen: "+', '.join(i[1].title() for i in D['interests'])+'.',
      'stack':"My stack. "+' '.join(g[0].title()+': '+', '.join(icon_title(x) for x in g[1])+'.' for g in D['stack_groups']),
      'id-dashboard':f"{D['name_first'].title()}'s builder ID and public GitHub dashboard. Snapshot {G['date'].title()}: {G['public_repos']} public repositories, {G['live_products']} live products, on GitHub since {G['joined'].title()}.",
      'connect':"Let's build something real. Connect on "+', '.join(v_[0] for v_ in soc.values())+' using the links below.'}
    img=lambda n: f'<img src="./assets/{n}.svg?v={v}" width="100%" alt="{H.escape(alts[n])}" />'
    md=[f"<!-- {D['github']}/{D['github']} profile README. Upload README.md + assets/ to the repo root. -->",
        '<p align="center">\n  '+img('hero')+'\n</p>','',img('about-life'),'',img('stack'),'',"### Things I've built",'',
        '| Project | What it does | Built with |','| :--- | :--- | :--- |',*rows,'',img('id-dashboard'),'',img('connect'),'',
        '<p align="center">\n'+' &nbsp;·&nbsp;\n'.join(f'  <a href="{H.escape(u)}">{H.escape(n)}</a>' for n,u in links)+'\n</p>','',
        f'<p align="center"><sub>{H.escape(D["footer"])}</sub></p>','']
    (ROOT/'README.md').write_text('\n'.join(md))
    pv=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{D['github']} · profile preview</title>
<style>body{{margin:0;background:#0d1117;color:#e6edf3;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
.wrap{{max-width:1012px;margin:24px auto;padding:0 16px}}.box{{border:1px solid #30363d;border-radius:6px;padding:24px 32px}}
@media(max-width:600px){{.wrap{{padding:0 8px;margin:8px auto}}.box{{padding:12px}}}}
.hd{{font-size:12px;color:#8b949e;margin-bottom:12px}}img{{max-width:100%;display:block;margin:0 0 8px}}
table{{border-collapse:collapse;margin:16px 0;width:100%;display:block;overflow:auto}}th,td{{border:1px solid #30363d;padding:6px 13px;text-align:left}}tr:nth-child(2n){{background:#161b22}}
a{{color:#4493f8;text-decoration:none}}h3{{border-bottom:1px solid #30363d;padding-bottom:.3em;font-size:1.25em}}p.c{{text-align:center}}</style></head>
<body><div class="wrap"><div class="hd">{D['github']} / README.md · local preview in GitHub's dark theme</div><div class="box" id="readme">
{img('hero')}{img('about-life')}{img('stack')}
<h3>Things I've built</h3><table><tr><th>Project</th><th>What it does</th><th>Built with</th></tr>{''.join(hrows)}</table>
{img('id-dashboard')}{img('connect')}
<p class="c">{' · '.join(f'<a href="{H.escape(u)}">{H.escape(n)}</a>' for n,u in links)}</p>
<p class="c"><sub>{H.escape(D['footer'])}</sub></p></div></div></body></html>"""
    (ROOT/'preview.html').write_text(pv.replace('src="./assets/','src="assets/'))
    print('README.md + preview.html')
if __name__=='__main__': readme_and_preview()
