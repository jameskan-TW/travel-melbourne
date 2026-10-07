#!/usr/bin/env python3
"""Build index.html (GitHub Pages) and artifact.html (Claude Artifact) from src/template.html + ../*.md"""
import re, html, pathlib, hashlib
ROOT=pathlib.Path(__file__).resolve().parent; TRIP=ROOT.parent
tpl=(ROOT/'src/template.html').read_text(encoding='utf-8')

def inline(t):
    t=html.escape(t,quote=False)
    t=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',t)
    t=re.sub(r'`([^`]+)`',r'<code>\1</code>',t)
    t=re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)',r'<a href="\2" target="_blank" rel="noopener">\1</a>',t)
    t=re.sub(r'(?<![">\w/])(https?://[^\s<)]+)',r'<a href="\1" target="_blank" rel="noopener">\1</a>',t)
    return t

def md2html(md, chk_prefix=None):
    out=[]; lines=md.splitlines(); i=0; mode=None; section=''
    def close():
        nonlocal mode
        if mode=='ul': out.append('</ul>')
        if mode=='chk': out.append('</ul>')
        if mode=='p': out.append('</p>')
        mode=None
    while i<len(lines):
        ln=lines[i]
        if ln.startswith('|') and i+1<len(lines) and re.match(r'^\|[\s:|-]+\|$',lines[i+1]):
            close(); hdr=[c.strip() for c in ln.strip('|').split('|')]; i+=2
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip('|').split('|')]); i+=1
            out.append('<div class="tbl"><table><thead><tr>'+''.join('<th>'+inline(c)+'</th>' for c in hdr)+'</tr></thead><tbody>')
            for r in rows: out.append('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in r)+'</tr>')
            out.append('</tbody></table></div>'); continue
        m=re.match(r'^(#{1,3})\s+(.*)',ln)
        if m:
            close(); lvl=len(m.group(1)); section=m.group(2)
            out.append(f'<h{lvl}>{inline(m.group(2))}</h{lvl}>'); i+=1; continue
        m=re.match(r'^-\s+\[( |x)\]\s+(.*)',ln)
        if m:
            if mode!='chk': close(); out.append('<ul class="chk">'); mode='chk'
            key=hashlib.md5((section+'|'+m.group(2)).encode()).hexdigest()[:10]
            out.append(f'<li class="chk"><label><input type="checkbox" data-key="{key}"><span>{inline(m.group(2))}</span></label></li>'); i+=1; continue
        m=re.match(r'^-\s+(.*)',ln)
        if m:
            if mode!='ul': close(); out.append('<ul>'); mode='ul'
            out.append('<li>'+inline(m.group(1))+'</li>'); i+=1; continue
        if ln.startswith('>'):
            close(); out.append('<blockquote>'+inline(ln[1:].strip())+'</blockquote>'); i+=1; continue
        if not ln.strip():
            close(); i+=1; continue
        if mode!='p': close(); out.append('<p>'); mode='p'
        out.append(inline(ln))
        i+=1
    close(); return '\n'.join(out)

def guide(title, path, gid, open_=False):
    body=md2html((TRIP/path).read_text(encoding='utf-8'))
    return f'  <details class="guide" id="{gid}"{" open" if open_ else ""}><summary>{html.escape(title)}</summary>\n  <div class="md">{body}</div></details>\n'

checklist=md2html((TRIP/'出國清單.md').read_text(encoding='utf-8'))
guides=''.join([
    guide('SkyBus 機場 ⇄ 市區','SkyBus指南.md','g-skybus'),
    guide('叫車：計程車 vs Uber、兒童座椅規定','叫車指南.md','g-taxi'),
    guide('景點 Google Maps 連結清單','景點清單.md','g-poi'),
])
page=tpl.replace('<!--CHECKLIST-->',checklist).replace('<!--GUIDES-->',guides)
(ROOT/'artifact.html').write_text(page,encoding='utf-8')

title=re.search(r'<title>.*?</title>',page).group(0); body=page.replace(title,'',1)
link=re.search(r'<link rel="stylesheet"[^>]*>',body).group(0); body=body.replace(link,'',1)
head=f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0f6e5a">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="墨爾本行程">
<meta name="robots" content="noindex, nofollow">
{title}
{link}
<style>
html{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
[hidden]{{display:none!important}}
</style>
</head>
'''
(ROOT/'index.html').write_text(head+'<body>\n'+body.strip()+'\n</body>\n</html>\n',encoding='utf-8')
print('BUILT index.html', len(page), 'chars; checklist items:', checklist.count('type="checkbox"'))
