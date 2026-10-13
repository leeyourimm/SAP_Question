# 서면(필기) 시험용 문제집 페이지 생성기
# 입력: ../0*.md (형식은 README "파일 형식" 참고)  출력: ../abap-drill.html
import re, html, markdown, os
from markdown.extensions.codehilite import CodeHiliteExtension
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'

LIST=re.compile(r'^\s*(\d+\.|[-*])\s')
SUBQ=re.compile(r'^(\(\d+\)|\*\*\(\d+\)\*\*|\*\*\(\d+\))')
def fixlists(t):
    out=[]; fence=False; prev=''
    for line in t.split('\n'):
        if line.lstrip().startswith('```'): fence=not fence
        if not fence and SUBQ.match(line) and prev.strip():
            out.append('')
        if not fence and LIST.match(line) and prev.strip() and not LIST.match(prev) and not prev.startswith('    ') and not prev.lstrip().startswith('|'):
            out.append('')
        out.append(line); prev=line
    return '\n'.join(out)
def render(t):
    t=re.sub(r'^```(cds|bdef|bdl|ddl|ddls|dcl|sqlscript)\b', '```sql', t, flags=re.M)
    return markdown.markdown(fixlists(t), extensions=['fenced_code','tables',CodeHiliteExtension(css_class='hl', guess_lang=False)])

TYPES=['개념','코드','작성']
HEAD=re.compile(r'^(?P<id>[A-Z0-9]+-\d+)\.\s*(?P<title>.*?)\s*\[(?P<type>[^\]]+)\]\s*(?P<stars>★{1,3})\s*$')

FILES=[
 dict(f='01_abap_basics.md',code='A',name='ABAP 기초',desc='데이터 타입, 문자열, 날짜, 제어문, 생성자 표현식, 필드 심볼, 내부 테이블, ABAP SQL, 알고리즘 손코딩.'),
 dict(f='02_abap_practice.md',code='B',name='ABAP 실무',desc='DDIC, 리포트·화면, ALV, LUW, 인터페이스, 확장, 성능·도구, OOP·예외·Unit, T-code, 실무 손코딩.'),
 dict(f='03_s4_cds_rap.md',code='C',name='S/4 · CDS · RAP',desc='ABAP on HANA, CDS, AMDP, ABAP Cloud, RAP, OData와 Fiori Elements 연결.'),
 dict(f='04_ui5_fiori.md',code='D',name='SAPUI5 · Fiori',desc='Fiori·런치패드, manifest, MVC, 바인딩, OData V2/V4, 라우팅, Fiori Elements, JavaScript.'),
]

def parse(path):
    s=open(path,encoding='utf-8').read()
    s=s.split('\n## 출처')[0]
    units=[]; cur=None
    for block in re.split(r'^(## .*)$', s, flags=re.M):
        if block.startswith('## '):
            cur=dict(name=block[3:].strip(), probs=[]); units.append(cur); continue
        if cur is None: continue
        parts=re.split(r'^### (.*)$', block, flags=re.M)
        cur['intro']=parts[0].strip()
        for i in range(1,len(parts),2):
            m=HEAD.match(parts[i].strip())
            if not m: print('  !! bad heading:',parts[i]); continue
            body=re.sub(r'\n---\s*$','',parts[i+1].strip())
            src=''
            ms=re.match(r'<!--\s*src:\s*(.*?)\s*-->\s*',body)
            if ms: src=ms.group(1); body=body[ms.end():]
            q,a=body,''
            md_=re.search(r'<details>\s*<summary>.*?</summary>(.*)</details>',body,re.S)
            if md_: q=body[:md_.start()].strip(); a=md_.group(1).strip()
            cur['probs'].append(dict(id=m['id'],title=m['title'],type=m['type'],diff=len(m['stars']),src=src,q=q,a=a))
    return [u for u in units if u['probs']]

def plain(t): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',t)))[:1200].lower()
def inline(t): return re.sub(r'`([^`]+)`',r'<code>\1</code>',html.escape(t))

def card(p,sec):
    dots=''.join('<i class="on"></i>' if k<p['diff'] else '<i></i>' for k in range(3))
    tcls='t%d'%(TYPES.index(p['type']) if p['type'] in TYPES else 0)
    sup='<span class="sup" title="인터넷 출제 유형에 드물지만 중요해서 보충한 문제">보충</span>' if '보충' in p['src'] else ''
    qh=render(p['q']); ah=render(p['a']) if p['a'] else ''
    pid=p['id']
    return f'''<article class="card" id="{pid}" data-sec="{sec}" data-diff="{p['diff']}" data-type="{html.escape(p['type'])}" data-text="{html.escape(plain(p['title']+' '+qh))}">
<details class="prob"><summary><span class="pid">{pid}</span><span class="ttl">{inline(p['title'])}</span><span class="ty {tcls}">{html.escape(p['type'])}</span>{sup}<span class="diff" title="난이도 {p['diff']}">{dots}</span><label class="done" title="푼 문제로 표시"><input type="checkbox" data-id="{pid}"><span>풀었음</span></label></summary>
<div class="body">{qh}<textarea class="draft" data-id="{pid}" rows="3" placeholder="소문항 답을 먼저 손으로(또는 여기에) 써 본 뒤 정답을 여세요" aria-label="{pid} 내 답안"></textarea>
<details class="ans"><summary>정답·해설</summary><div class="ans-body">{ah}</div></details>
<p class="srcline">{('묶은 원본 문제: '+html.escape(p['src'])) if p['src'] else ''}</p></div></details></article>'''

secs=[]; nav=[]; total=0; tcount={t:0 for t in TYPES}
for F in FILES:
    path=D+F['f']
    if not os.path.exists(path): print('missing',F['f']); continue
    units=parse(path); n=sum(len(u['probs']) for u in units)
    groups=[]
    for u in units:
        for p in u['probs']: tcount[p['type']]=tcount.get(p['type'],0)+1
        intro=f'<div class="intro">{render(u["intro"])}</div>' if u.get('intro') else ''
        groups.append(f'<div class="group"><h3>{html.escape(u["name"])} <small>{len(u["probs"])}</small></h3>{intro}{"".join(card(p,F["code"]) for p in u["probs"])}</div>')
    total+=n; nav.append((F,n))
    secs.append(f'''<section class="sec" id="sec-{F['code']}" data-sec="{F['code']}">
<header class="sec-h"><div class="sec-tag">{F['code']}</div><div><h2>{html.escape(F['name'])} <span class="cnt">{n}문제</span></h2><p class="desc">{html.escape(F['desc'])}</p></div></header>{"".join(groups)}</section>''')
    print(F['f'], n)

navhtml=''.join(f'<a class="nav-i" href="#sec-{F["code"]}" data-sec="{F["code"]}"><span class="nav-code">{F["code"]}</span><span class="nav-name">{html.escape(F["name"])}</span><span class="nav-n">{n}</span></a>' for F,n in nav)
typechips=''.join(f'<button class="chip" data-t="{t}" aria-pressed="false">{t} <small>{tcount.get(t,0)}</small></button>' for t in TYPES)
tpl=open(D+'_web/tpl.html',encoding='utf-8').read()
out=tpl.replace('%%NAV%%',navhtml).replace('%%SECTIONS%%','\n'.join(secs)).replace('%%TOTAL%%',str(total)).replace('%%TYPECHIPS%%',typechips)
open(D+'abap-drill.html','w',encoding='utf-8').write(out)
print('total',total,tcount,len(out))
