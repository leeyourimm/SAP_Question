# RAP 실습 문제집 페이지 생성기 (탭 2개: RAP 실습 / 어노테이션 설명)
# 입력: ../rap/R*.md (문제), ../rap/annotations.md (어노테이션)  출력: ../abap-drill.html
# 문제 형식은 README "파일 형식" 참고: ## 단원 / ### R-01. 제목 [작성] ★★★(최대 ★★★★) / #### 1단계. 제목 / <details> 정답
import re, html, markdown, os, glob
from markdown.extensions.codehilite import CodeHiliteExtension
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
R = D + 'rap/'

LIST = re.compile(r'^\s*(\d+\.|[-*])\s')
def fixlists(t):
    out = []; fence = False; prev = ''
    for line in t.split('\n'):
        if line.lstrip().startswith('```'): fence = not fence
        if not fence and LIST.match(line) and prev.strip() and not LIST.match(prev) and not prev.startswith('    ') and not prev.lstrip().startswith('|'):
            out.append('')
        if not fence and line.startswith('**') and prev.strip() and not prev.startswith('**') and not LIST.match(prev) and not prev.lstrip().startswith('|'):
            out.append('')
        out.append(line); prev = line
    return '\n'.join(out)

def render(t):
    t = re.sub(r'^```\s*(cds|ddl|ddls|dcl|ddlx|srvd|sqlscript)\b', '```sql', t, flags=re.M)
    t = re.sub(r'^```\s*(bdef|bdl)\b', '```abap', t, flags=re.M)
    return markdown.markdown(fixlists(t), extensions=['fenced_code', 'tables', CodeHiliteExtension(css_class='hl', guess_lang=False)])

def slug(s): return 'a-' + re.sub(r'[^0-9A-Za-z]+', '-', s).strip('-')
def plain(t, n=4000): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))[:n].lower()
def inline(t): return re.sub(r'`([^`]+)`', r'<code>\1</code>', html.escape(t))
def cut_sources(s):
    parts = re.split(r'^## 출처\s*$', s, flags=re.M)
    return parts[0], (parts[1] if len(parts) > 1 else '')

# ---------- 어노테이션 ----------
ann_groups = []; ann_index = {}; ann_src = ''
if os.path.exists(R + 'annotations.md'):
    body, ann_src = cut_sources(open(R + 'annotations.md', encoding='utf-8').read())
    cur = None; used = set()
    for blk in re.split(r'^(## .*)$', body, flags=re.M):
        if blk.startswith('## '):
            cur = dict(name=blk[3:].strip(), intro='', items=[]); ann_groups.append(cur); continue
        if cur is None: continue
        parts = re.split(r'^### (.*)$', blk, flags=re.M)
        cur['intro'] = parts[0].strip()
        for i in range(1, len(parts), 2):
            head = parts[i].strip()
            m = re.match(r'(@[\w.]+)', head)
            key = m.group(1).rstrip('.') if m else head
            aid = slug(key)
            while aid in used: aid += '-x'
            used.add(aid)
            if m and key not in ann_index: ann_index[key] = aid
            cur['items'].append(dict(head=head, id=aid, body=parts[i + 1].strip()))

def ann_link(name):
    n = name.rstrip('.')
    while n:
        if n in ann_index: return ann_index[n]
        if '.' not in n: break
        n = n.rsplit('.', 1)[0]
    return None

def link_annotations(h):
    def code_rep(m):
        aid = ann_link(m.group(1))
        return f'<a class="alink" href="#{aid}"><code>{m.group(1)}</code></a>' if aid else m.group(0)
    h = re.sub(r'<code>(@[\w.]+)</code>', code_rep, h)
    def tab_rep(m):
        aid = ann_link(m.group(2))
        return f'{m.group(1)}<a class="alink" href="#{aid}">{m.group(2)}</a>' if aid else m.group(0)
    h = re.sub(r'(어노테이션 탭:\s*)(@[\w.]+)', tab_rep, h)
    return h

def link_problems(h):
    # 코드 블록(<pre>) 밖의 R-01 같은 문제 번호만 링크로
    parts = re.split(r'(<pre>.*?</pre>)', h, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'(?<![\w#/>-])(R-\d{2})(?![\w-])', r'<a class="plink" href="#\1">\1</a>', parts[i])
    return ''.join(parts)

# ---------- 문제 ----------
HEAD = re.compile(r'^(?P<id>R-\d+)\.\s*(?P<title>.*?)\s*\[(?P<type>[^\]]+)\]\s*(?P<stars>★{1,4})\s*$')
units = {}; order = []; sources = []
for f in sorted(glob.glob(R + 'R*.md')):
    body, src = cut_sources(open(f, encoding='utf-8').read())
    if src.strip(): sources.append(src.strip())
    unit = None
    for blk in re.split(r'^(## .*)$', body, flags=re.M):
        if blk.startswith('## '):
            unit = blk[3:].strip()
            if unit not in units: units[unit] = []; order.append(unit)
            continue
        if unit is None: continue
        parts = re.split(r'^### (.*)$', blk, flags=re.M)
        for i in range(1, len(parts), 2):
            m = HEAD.match(parts[i].strip())
            if not m: print('  !! bad heading:', parts[i]); continue
            pb = parts[i + 1].strip()
            covers = ''
            mc = re.search(r'<!--\s*covers:\s*(.*?)\s*-->', pb, re.S)
            if mc: covers = mc.group(1); pb = pb[:mc.start()] + pb[mc.end():]
            steps = re.split(r'^#### (.*)$', pb, flags=re.M)
            intro = steps[0].strip(); st = []
            for j in range(1, len(steps), 2):
                sb = re.sub(r'\n---\s*$', '', steps[j + 1].strip())
                q, a = sb, ''
                md_ = re.search(r'<details>\s*<summary>.*?</summary>(.*)</details>', sb, re.S)
                if md_: q = (sb[:md_.start()] + sb[md_.end():]).strip(); a = md_.group(1).strip()
                st.append(dict(title=steps[j].strip(), q=q, a=a))
            units[unit].append(dict(id=m['id'], title=m['title'], diff=len(m['stars']), covers=covers, intro=intro, steps=st))
for u in order: units[u].sort(key=lambda p: p['id'])

def post(h): return link_problems(link_annotations(h))

def step_html(p, k, s):
    sid = f"{p['id']}-s{k}"
    qh = post(render(s['q'])); ah = post(render(s['a'])) if s['a'] else '<p>정답 없음</p>'
    return f'''<details class="step" id="{sid}"><summary><span class="snum">{k}</span><span class="stt">{inline(re.sub(r'^\d+\s*단계\.\s*', '', s['title']))}</span><label class="done sdone" title="이 단계 끝냄"><input type="checkbox" data-id="{sid}"><span>끝냄</span></label></summary>
<div class="sbody">{qh}<textarea class="draft" data-id="{sid}" rows="3" placeholder="막힌 점, 내가 쓴 코드, 오류 메시지를 메모해 두세요" aria-label="{sid} 메모"></textarea>
<details class="ans"><summary>정답·해설</summary><div class="ans-body">{ah}</div></details></div></details>'''

def card(p):
    dots = ''.join('<i class="on"></i>' if k < p['diff'] else '<i></i>' for k in range(max(3, p['diff'])))
    ih = post(render(p['intro']))
    steps = ''.join(step_html(p, k + 1, s) for k, s in enumerate(p['steps']))
    cov = ''
    if p['covers']:
        chips = ''.join(f'<span class="kw">{html.escape(c.strip())}</span>' for c in p['covers'].split(',') if c.strip())
        cov = f'<div class="covers"><b>다루는 기능</b>{chips}</div>'
    text = plain(p['title'] + ' ' + p['covers'] + ' ' + ' '.join(s['title'] + ' ' + s['q'] + ' ' + s['a'] for s in p['steps']), 60000)
    return f'''<article class="card" id="{p['id']}" data-diff="{p['diff']}" data-text="{html.escape(text)}">
<details class="prob"><summary><span class="pid">{p['id']}</span><span class="ttl">{inline(p['title'])}</span><span class="prog" data-pid="{p['id']}" data-n="{len(p['steps'])}">0/{len(p['steps'])}단계</span><span class="diff" title="난이도 {p['diff']}">{dots}</span></summary>
<div class="body">{cov}<div class="intro">{ih}</div><div class="steps">{steps}</div></div></details></article>'''

rap_secs = []; rap_nav = []; nprob = 0; nstep = 0
for ui, u in enumerate(order):
    ps = units[u]; nprob += len(ps); nstep += sum(len(p['steps']) for p in ps)
    uid = f'u{ui + 1}'
    rap_secs.append(f'<section class="sec" id="{uid}"><h2 class="uh">{html.escape(u)} <small>{len(ps)}문제</small></h2>' + ''.join(card(p) for p in ps) + '</section>')
    items = ''.join(f'<a class="nav-p" href="#{p["id"]}"><span class="nav-code">{p["id"]}</span><span class="nav-name">{inline(p["title"])}</span></a>' for p in ps)
    rap_nav.append(f'<div class="nav-g"><a class="nav-u" href="#{uid}">{html.escape(u)}</a>{items}</div>')
    print(u, [p['id'] + ':' + str(len(p['steps'])) for p in ps])

fmap = {}
for u in order:
    for p in units[u]:
        for c in p['covers'].split(','):
            c = c.strip()
            if c: fmap.setdefault(c, []).append(p['id'])
fmap_rows = ''.join(f'<tr><td>{html.escape(k)}</td><td>{" ".join(f"<a class=plink href=#{i}>{i}</a>" for i in dict.fromkeys(v))}</td></tr>' for k, v in fmap.items())
fmap_html = f'<details class="fmap"><summary>RAP 기능 지도 · 기능 {len(fmap)}개가 어느 문제에 나오는지</summary><div class="fmap-body"><table><thead><tr><th>기능</th><th>문제</th></tr></thead><tbody>{fmap_rows}</tbody></table></div></details>' if fmap else ''

def merge_sources(srcs):
    lines = []
    for s in srcs:
        for ln in s.split('\n'):
            ln = ln.rstrip()
            if ln.strip() and ln not in lines: lines.append(ln)
    return render('\n'.join(lines)) if lines else ''
src_html = merge_sources(sources + ([ann_src.strip()] if ann_src.strip() else []))

ann_secs = []; ann_nav = []; nann = 0
for gi, g in enumerate(ann_groups):
    gid = f'g{gi}'; nann += len(g['items'])
    items = []
    for it in g['items']:
        bh = link_problems(link_annotations(render(it['body'])))
        first = re.search(r'\*\*하는 일\*\*\s*(.+)', it['body'])
        lead = inline(first.group(1).strip()[:110]) if first else ''
        items.append(f'''<article class="acard" id="{it['id']}" data-text="{html.escape(plain(it['head'] + ' ' + it['body'], 3000))}"><details class="aent"><summary><span class="aname">{inline(it['head'])}</span><span class="alead">{lead}</span></summary><div class="abody">{bh}</div></details></article>''')
    intro = link_problems(link_annotations(render(g['intro']))) if g['intro'] else ''
    ann_secs.append(f'<section class="asec" id="{gid}"><h2 class="uh">{html.escape(g["name"])} <small>{len(g["items"])}개</small></h2><div class="gintro">{intro}</div>{"".join(items)}</section>')
    ann_nav.append(f'<a class="nav-u" href="#{gid}">{html.escape(g["name"])} <small>{len(g["items"])}</small></a>')

tpl = open(D + '_web/tpl.html', encoding='utf-8').read()
rep = {'%%RAPNAV%%': ''.join(rap_nav), '%%RAPSECS%%': fmap_html + '\n'.join(rap_secs),
       '%%ANNNAV%%': ''.join(ann_nav), '%%ANNSECS%%': '\n'.join(ann_secs),
       '%%NPROB%%': str(nprob), '%%NSTEP%%': str(nstep), '%%NANN%%': str(nann), '%%SOURCES%%': src_html}
out = tpl
for k, v in rep.items(): out = out.replace(k, v)
open(D + 'abap-drill.html', 'w', encoding='utf-8').write(out)
print('problems', nprob, 'steps', nstep, 'annotations', nann, 'features', len(fmap), 'bytes', len(out))
