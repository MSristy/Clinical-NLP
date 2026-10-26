from pathlib import Path
from html import escape
from math import atan2,cos,sin
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
W,H=1600,1090
im=Image.new('RGB',(W,H),'#F7FAFD'); d=ImageDraw.Draw(im)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
     '<title id="title">Clinical NLP — recommendation system architecture</title>',
     '<desc id="desc">Implemented preparation: four protocols, extraction and visual review, 32 canonical cards and BM25 indexing. Patient facts and indexed evidence feed retrieval, Qwen model, shared applicability and missing-information checks, and four-category care plan with citations. Baseline takes the direct path; Improved alone adds the tested pre-model applicability preview. Patient context and source IDs remain attached. Zero cards causes no model call. Future dashed connections show NER with clinician confirmation, doctor acceptance, prescription draft and governed feedback to reviewed cards.</desc>',
     f'<rect width="{W}" height="{H}" fill="#F7FAFD"/>']
INK='#18364D'; MUTED='#5D7487'; TEAL='#087F8C'; PURPLE='#8461B5'; ORANGE='#B77913'
fonts={}
def font(size,bold=False):
    key=(size,bold)
    if key not in fonts: fonts[key]=ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size)
    return fonts[key]
def text(x,y,s,size=18,color=INK,bold=False,anchor='start'):
    svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(s)}</text>')
    width=d.textlength(s,font=font(size,bold)); xx=x-(width/2 if anchor=='middle' else width if anchor=='end' else 0)
    d.text((xx,y-size),s,font=font(size,bold),fill=color)
def rect(x,y,w,h,fill='white',stroke='#DAE6EE',r=14):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    d.rounded_rectangle((x,y,x+w,y+h),radius=r,fill=fill,outline=stroke,width=2)
def line(points,color=TEAL,width=2,dash=False,arrow=False):
    svg.append(f'<polyline points="'+ ' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'+(' stroke-dasharray="7 7"' if dash else '')+'/>')
    for (x1,y1),(x2,y2) in zip(points,points[1:]):
        if not dash: d.line((x1,y1,x2,y2),fill=color,width=width)
        else:
            length=((x2-x1)**2+(y2-y1)**2)**.5
            if length:
                for start in range(0,int(length),14):
                    end=min(start+7,length)
                    d.line((x1+(x2-x1)*start/length,y1+(y2-y1)*start/length,x1+(x2-x1)*end/length,y1+(y2-y1)*end/length),fill=color,width=width)
    if arrow:
        x,y=points[-1]; a=atan2(y-points[-2][1],x-points[-2][0])
        p=[(x,y),(x-10*cos(a-.5),y-10*sin(a-.5)),(x-10*cos(a+.5),y-10*sin(a+.5))]
        svg.append('<polygon points="'+' '.join(f'{xx:.1f},{yy:.1f}' for xx,yy in p)+f'" fill="{color}"/>')
        d.polygon(p,fill=color)
def ellipse(x,y,w,h,fill='white',stroke=TEAL):
    svg.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    d.ellipse((x,y,x+w,y+h),fill=fill,outline=stroke,width=2)
def icon(kind,x,y,color=TEAL):
    def l(p): line([(x+a,y+b) for a,b in p],color,2)
    def box(a,b,w,h): rect(x+a,y+b,w,h,'#FFFFFF',color,3)
    if kind in ('pdf','extract','cards','output','rx','ner'):
        if kind=='cards':
            box(1,0,25,29); box(6,5,25,29)
        else: box(5,1,27,32)
        l([(11,11),(25,11)]); l([(11,17),(25,17)]); l([(11,23),(21,23)])
        if kind=='extract': l([(21,29),(26,34),(36,23)])
        if kind=='rx': text(x+17,y+27,'R',19,color,True,anchor='middle')
        if kind=='ner': l([(0,7),(0,0),(7,0)]); l([(29,37),(37,37),(37,29)])
    elif kind=='database':
        rect(x+2,y+8,32,23,'#FFFFFF',color,0)
        ellipse(x+2,y+24,32,11,'#FFFFFF',color)
        ellipse(x+2,y+13,32,11,'#FFFFFF',color)
        ellipse(x+2,y+1,32,11,'#FFFFFF',color)
    elif kind=='patient':
        ellipse(x+12,y,13,13,'#FFFFFF',color)
        l([(3,34),(3,29),(6,23),(13,19),(24,19),(31,23),(34,29),(34,34)])
        l([(13,27),(24,27)]);l([(18,22),(18,32)])
    elif kind=='search':
        ellipse(x+2,y+1,25,25,'#FFFFFF',color);l([(24,24),(36,36)])
    elif kind=='model':
        box(7,7,24,24)
        for t in (12,20,27):
            l([(t,0),(t,7)]);l([(t,31),(t,38)]);l([(0,t),(7,t)]);l([(31,t),(38,t)])
        box(14,14,10,10)
    elif kind in ('check','doctor'):
        l([(18,1),(33,7),(32,22),(26,31),(18,37),(10,31),(4,22),(3,7),(18,1)])
        l([(10,18),(16,24),(27,12)])
    elif kind=='feedback':
        l([(7,12),(13,4),(26,4),(33,12),(33,24)]);l([(26,18),(33,25),(38,18)])
        l([(29,29),(23,36),(10,36),(3,28),(3,17)]);l([(0,23),(3,16),(10,22)])
def node(x,y,w,h,title,subtitle,kind,tone='implemented'):
    fill,stroke,color=('#FFFFFF','#BFDADD',TEAL) if tone=='implemented' else ('#FFF7E8','#E7CA8B',ORANGE) if tone=='tested' else ('#FBF8FF','#D6C8E9',PURPLE)
    rect(x,y+4,w,h,'#EAF0F5','#EAF0F5')
    rect(x,y,w,h,fill,stroke)
    icon(kind,x+18,y+19,color)
    text(x+68,y+44,title,20,color=INK,bold=True)
    text(x+18,y+h-22,subtitle,15,color=MUTED)

text(44,58,'Clinical NLP',34,bold=True)
text(260,58,'System architecture',28,color=MUTED)
text(45,94,'Protocol knowledge → patient-specific, source-linked recommendations',19,color=MUTED)
for x,label,color in [(1030,'Implemented',TEAL),(1220,'Tested change',ORANGE),(1430,'Future',PURPLE)]:
    rect(x,43,11,11,color,color,3); text(x+20,56,label,15,color=MUTED)

rect(40,130,1480,205,'#EFF6FA','#E0EAF1',18)
text(60,161,'01  /  KNOWLEDGE PREPARATION',15,color=MUTED,bold=True)
rect(40,390,1480,400,'#FFFFFF','#E0EAF1',18)
text(60,418,'02  /  RECOMMENDATION ENGINE',15,color=MUTED,bold=True)
rect(40,840,1480,200,'#F5F1FB','#E0D6EF',18)
text(60,872,'03  /  FUTURE INTEGRATIONS',15,color=PURPLE,bold=True)

# Implemented source flow and index connector.
for a,b in [(360,440),(740,820),(1120,1200)]: line([(a,256),(b,256)],arrow=True)
line([(1350,312),(1350,358),(480,358),(480,540)],color='#7297A5',arrow=True)
text(920,350,'indexed cards',14,color=MUTED,anchor='middle')

# Five-stage runtime. Baseline is direct; only Improved takes the orange branch.
for a,b in [(300,360),(600,660),(900,960),(1200,1260)]: line([(a,600),(b,600)],arrow=True)
text(630,588,'Baseline',12,color=MUTED,anchor='middle')
line([(540,540),(540,460),(620,460)],color=ORANGE,arrow=True)
line([(900,460),(925,460),(925,510),(780,510),(780,540)],color=ORANGE,arrow=True)
line([(480,660),(480,691)],color='#7297A5',arrow=True)
line([(1080,660),(1080,691)],color='#7297A5',arrow=True)

# Future links stay outside the main operational flow.
line([(60,944),(24,944),(24,600),(60,600)],color=PURPLE,dash=True,arrow=True)
line([(1500,600),(1534,600),(1534,820),(590,820),(590,900)],color=PURPLE,dash=True,arrow=True)
line([(740,944),(820,944)],color=PURPLE,dash=True,arrow=True)
line([(590,988),(590,1015),(1350,1015),(1350,988)],color=PURPLE,dash=True,arrow=True)
line([(1500,944),(1570,944),(1570,174),(970,174),(970,200)],color=PURPLE,dash=True,arrow=True)

node(60,200,300,112,'Protocol PDFs','4 protocols · 45 assigned pages','pdf')
node(440,200,300,112,'Extract + review','Text · tables · footnotes','extract')
node(820,200,300,112,'Canonical cards','32 cards · rules + evidence IDs','cards')
node(1200,200,300,112,'BM25 index','Local JSON · source-linked RAG','database')

node(60,540,240,120,'Patient facts','Symptoms · history · unknowns','patient')
node(360,540,240,120,'Retrieve cards','Positive anchors · 0–10 cards','search')
node(660,540,240,120,'Qwen model','Same model · both modes','model')
node(960,540,240,120,'Shared checks','Rules · missing info · citations','check')
node(1260,540,240,120,'Care plan','Dx · tests · medicines · advice','output')
rect(620,425,280,70,'#FFF7E8','#E7CA8B',12)
text(640,449,'TESTED · IMPROVED ONLY',12,color=ORANGE,bold=True)
text(640,477,'Applicability preview',20,color=INK,bold=True)
rect(360,694,240,35,'#F1F6FA','#DCE8EF',9)
text(480,717,'0 cards → no model call',15,color=MUTED,anchor='middle')
rect(960,694,240,35,'#F1F6FA','#DCE8EF',9)
text(1080,717,'Saved run + evidence log',15,color=MUTED,anchor='middle')
rect(1260,694,240,35,'#F1F6FA','#DCE8EF',9)
text(1380,717,'Source title · version · page',14,color=MUTED,anchor='middle')
rect(60,751,1440,26,'#E9F6F4','#E9F6F4',8)
text(780,770,'Patient context + source IDs stay attached throughout the pipeline',15,color=TEAL,anchor='middle')

node(60,900,300,88,'NER + doctor review','Extract → confirm → patient facts','ner','future')
node(440,900,300,88,'Doctor acceptance','Accept · edit · reject','doctor','future')
node(820,900,300,88,'Prescription draft','Accepted items · clinician signs','rx','future')
node(1200,900,300,88,'Feedback + review','Governed updates → source cards','feedback','future')
text(60,1072,'Solid arrows: implemented flow     Dashed arrows: future design only     No NER or prescription integration is implemented.',15,color=MUTED)
svg.append('</svg>')
target=ROOT/'docs/architecture.svg'
target.write_text('\n'.join(svg),encoding='utf-8')
im.save(ROOT/'docs/architecture.png')
print('Rendered docs/architecture.svg and docs/architecture.png.')
