"""Build a portable, dependency-free GitHub Pages academic site."""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
BASE = 'https://drivanwho.github.io'
esc = html.escape

def translation_url(path, language):
    return 'https://translate.google.com/translate?' + urlencode({'sl': 'zh-CN', 'tl': language, 'u': BASE + path})

def languages(path):
    return ('<div class="translation-bar" aria-label="全文翻译">'
            '<span class="label">阅读语言</span>'
            f'<a class="lang-button active" aria-current="page" href="{path}">中文</a>'
            + ''.join(f'<a class="lang-button notranslate" lang="{code}" href="{esc(translation_url(path,code))}" target="_blank" rel="noopener noreferrer">{label}<span class="sr-only">（在新标签页打开全文翻译）</span></a>' for code,label in [('en','English'),('ko','한국어'),('ja','日本語')])
            + '<span class="translation-note">Google Translate · 自动翻译</span></div>')

def head(title, description, path):
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — 胡逸凡 Yifan Hu</title><meta name="description" content="{esc(description[:170])}">
<link rel="canonical" href="{BASE}{path}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description[:170])}"><meta property="og:type" content="article"><meta property="og:url" content="{BASE}{path}">
<meta name="theme-color" content="#fbfaf6"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css"><link rel="alternate" type="application/atom+xml" title="胡逸凡 · 写作" href="/feed.xml"><script src="/assets/site.js" defer></script></head>'''

def header(current=''):
    navigation=[('/', '首页', 'home'),('/cv/', '简历', 'cv'),('/#research', '研究', 'research'),('/life/', '生活', 'life'),('/contact/', '联系方式', 'contact')]
    links=''.join(f'<a href="{url}"'+(' aria-current="page"' if key==current else '')+f'>{label}</a>' for url,label,key in navigation)
    return '<a class="skip-link" href="#main">跳转至正文</a><header class="site-header"><a class="brand" href="/" aria-label="胡逸凡，返回首页"><strong>胡逸凡</strong><span>Yifan Hu</span></a><nav class="nav-links" aria-label="主导航">'+links+'</nav></header>'

def footer():
    return '<footer class="site-footer"><p>© 2026 胡逸凡 · Yifan Hu</p><div class="footer-links"><a href="/life/">生活与写作</a><a href="/feed.xml">RSS</a><a href="/contact/">联系方式 ↗</a><a href="/">返回首页</a></div></footer>'

def date_label(post):
    return post.get('dateLabel') or (post['date'].replace('-','.') if post.get('date') else '日期未详')

def article_body(post):
    content=[]
    for paragraph in post['paragraphs']:
        text=paragraph.strip()
        heading = len(text)<36 and bool(re.match(r'^(?:[一二三四五六七八九十]+[、.．]|[0-9]+[.．、]|篇[一二三四五六七八九十]+\s*[／/]|第[一二三四五六七八九十]+[节章])',text))
        tag='h2' if heading else 'p'
        content.append(f'<{tag}>'+esc(text).replace('\n','<br>')+f'</{tag}>')
    return '\n'.join(content)

def write(path, text):
    dest=OUT/path
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(text,encoding='utf-8')

def build():
    posts=json.loads((ROOT/'content/posts.json').read_text(encoding='utf-8'))
    posts.sort(key=lambda p:p.get('date') or '',reverse=True)
    OUT.mkdir(exist_ok=True)
    for child in OUT.iterdir():
        if child.is_dir(): shutil.rmtree(child)
        else: child.unlink()
    shutil.copytree(ROOT/'assets',OUT/'assets')
    shutil.copytree(ROOT/'images',OUT/'images')
    write('.nojekyll','')
    rows=[]
    for i,post in enumerate(posts):
        path=f'/writing/{post["slug"]}/'
        excerpt=post.get('excerpt') or post['paragraphs'][0][:88]
        tags=' · '.join(post.get('tags',[]))
        rows.append(f'''<li class="post-row" data-date="{post.get('date') or ''}"><a class="post-link" href="{path}"><time class="post-date"{f' datetime="{post["date"]}"' if post.get('date') else ''}>{esc(date_label(post))}</time><div class="post-main"><h3>{esc(post['title'])}</h3><p>{esc(excerpt[:104])}{'…' if len(excerpt)>104 else ''}</p><span class="post-tags">{esc(tags)}</span></div><span class="post-arrow" aria-hidden="true">↗</span></a></li>''')
        length=sum(len(p) for p in post['paragraphs'])
        minutes=max(1,round(length/450))
        source=(f'<a href="{esc(post["sourceUrl"])}" target="_blank" rel="noopener noreferrer">阅读发布原文 ↗</a>' if post.get('sourceUrl') else '')
        navigation=[]
        for offset,classname,label in [(-1,'prev','上一篇'),(1,'next','下一篇')]:
            n=i+offset
            if 0<=n<len(posts):
                other=posts[n]
                navigation.append(f'<a class="{classname}" href="/writing/{other["slug"]}/"><span>{label}</span><strong>{esc(other["title"])}</strong></a>')
        article=f'''{head(post['title'],excerpt,path)}<body class="reader-page">{header('life')}
<main class="reader" id="main"><a class="back-link" href="/life/">← 返回文集</a><div class="article-kicker">生活与写作 / 随笔</div><article><h1 class="article-title">{esc(post['title'])}</h1>
<div class="article-meta"><span>{esc(date_label(post))}</span><span>约 {minutes} 分钟阅读</span><span>{length:,} 字</span></div>
{languages(path)}<div class="article-content">{article_body(post)}</div>
<div class="article-footer"><span>文集收录 · 保留原文</span>{source}<button type="button" class="text-button" data-copy-link>复制文章链接</button></div></article>
<nav class="post-navigation" aria-label="相邻文章">{''.join(navigation)}</nav></main>{footer()}</body></html>'''
        write(f'writing/{post["slug"]}/index.html',article)
    home=(ROOT/'templates/home.html').read_text(encoding='utf-8')
    replacements={'{{POST_ROWS}}':'\n'.join(rows[:6]),'{{POST_COUNT}}':str(min(6,len(posts))),'{{POST_TOTAL}}':str(len(posts)),'{{TRANSLATE_EN}}':esc(translation_url('/','en')),'{{TRANSLATE_KO}}':esc(translation_url('/','ko')),'{{TRANSLATE_JA}}':esc(translation_url('/','ja'))}
    for key,value in replacements.items(): home=home.replace(key,value)
    write('index.html',home)
    life=head('生活与写作','故乡、朋友，和路上的日常。胡逸凡的个人文集与兴趣。','/life/')+'<body class="life-page">'+header('life')+'''<main class="shell" id="main"><section class="page-intro"><p class="eyebrow">BEYOND RESEARCH</p><h1 class="page-title">生活与写作<span class="title-dot" aria-hidden="true">.</span></h1><p class="page-description">故乡、朋友，和路上的日常。</p><p class="interest-line">文学写作 · 枞阳记忆 · 手风琴 · 俄罗斯文化 · 跳舞</p></section><section class="life-archive" aria-label="全部文章"><div class="post-toolbar"><label class="search-field" for="post-search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"></circle><path d="m16 16 5 5"></path></svg><input id="post-search" type="search" placeholder="搜索文章标题或简介" aria-label="搜索文章标题或简介"></label><select id="post-sort" aria-label="文章时间排序"><option value="newest">由新到旧</option><option value="oldest">由旧到新</option></select></div>'''+f'<div class="post-status"><span id="post-count" aria-live="polite">{len(posts)} 篇文章</span><span>21 篇有发布日期 · 3 篇日期未详</span></div><ul id="post-list" class="post-list">'+''.join(rows)+'''</ul><p id="empty-state" hidden>没有找到相关文章，试试其他关键词。</p></section></main>'''+footer()+'</body></html>'
    write('life/index.html',life)
    contact=head('联系方式','与胡逸凡联系：学术交流、合作与写作。','/contact/')+'<body class="contact-page">'+header('contact')+'''<main class="shell" id="main"><section class="page-intro contact-intro"><p class="eyebrow">GET IN TOUCH</p><h1 class="page-title">保持联系<span class="title-dot" aria-hidden="true">.</span></h1><p class="page-description">关于研究、写作，或只是想聊一聊。<br>欢迎给我写信。</p></section><section class="contact-list" aria-label="联系与学术资料"><a class="contact-row" href="mailto:drivanhu@gmail.com"><span class="contact-label">EMAIL · 电子邮箱</span><strong class="contact-value">drivanhu@gmail.com</strong><span class="contact-arrow" aria-hidden="true">↗</span></a><div class="email-copy"><button class="text-button" type="button" data-copy-email="drivanhu@gmail.com">复制邮箱地址</button><span data-email-status role="status"></span></div><a class="contact-row" href="https://scholar.google.com/citations?user=07jq_D0AAAAJ" target="_blank" rel="noopener noreferrer"><span class="contact-label">ACADEMIC · 学术资料</span><strong class="contact-value">Google Scholar</strong><span class="contact-arrow" aria-hidden="true">↗</span></a><a class="contact-row" href="https://orcid.org/0000-0003-2268-8419" target="_blank" rel="noopener noreferrer"><span class="contact-label">ORCID · 研究者标识</span><strong class="contact-value">0000-0003-2268-8419</strong><span class="contact-arrow" aria-hidden="true">↗</span></a><a class="contact-row" href="https://github.com/drivanwho" target="_blank" rel="noopener noreferrer"><span class="contact-label">GITHUB · 代码</span><strong class="contact-value">@drivanwho</strong><span class="contact-arrow" aria-hidden="true">↗</span></a></section></main>'''+footer()+'</body></html>'
    write('contact/index.html',contact)
    cv=head('学术履历','胡逸凡的教育、研究与学术成果。','/cv/')+'<body class="reader-page">'+header('cv')+'''<main class="reader" id="main"><a class="back-link" href="/">← 返回首页</a><div class="article-kicker">CURRICULUM VITAE</div><h1 class="article-title">胡逸凡 <small>Yifan Hu</small></h1><p class="article-meta">东京科学大学 · 电气电子工程博士在读 · 日本东京</p>'''+languages('/cv/')+'''<div class="article-content"><p><a href="mailto:drivanhu@gmail.com">drivanhu@gmail.com</a> · <a href="https://scholar.google.com/citations?user=07jq_D0AAAAJ">Google Scholar</a> · <a href="https://orcid.org/0000-0003-2268-8419">ORCID</a></p>
<h2>研究方向</h2><p>原子层沉积（ALD）、超薄磁性薄膜、Co/Pt 多层膜与界面驱动垂直磁各向异性、非易失性存储器、机器学习辅助工艺优化。</p>
<h2>教育背景</h2><p><strong>东京科学大学（原东京工业大学）</strong><br>电气电子工程 · 博士在读<br>2024.03 — 2027.03（预计） · 日本东京</p><p><strong>成均馆大学</strong><br>电子与计算机工程 · 硕士<br>2021.09 — 2024.02 · 韩国水原</p><p><strong>山东大学</strong><br>应用物理学 · 学士<br>2017.09 — 2021.06 · 中国山东</p>
<h2>研究经历</h2><p><strong>三维赛道存储器与 ALD Co/Pt 多层薄膜</strong><br>2025.09 — 2026.04 · 项目独立负责人<br>建立全 ALD 的 Co/Pt 多层膜制备流程，系统优化沉积条件、膜厚设计与界面工程，实现垂直磁各向异性。</p><p><strong>超薄热 ALD Co 薄膜</strong><br>2024.09 — 2025.08 · 项目独立负责人<br>开发无等离子体热 ALD 工艺，优化表面反应与杂质控制，制备平整、保形的超薄 Co 薄膜。</p><p><strong>机器学习辅助电荷俘获存储器工艺优化</strong><br>2023.03 — 2024.02 · 项目独立负责人 · 三星电子产学合作项目<br>结合支持向量回归与群体优化算法，进行工艺参数筛选和存储性能预测。</p><p><strong>基于 HfAlO 的非易失性电荷俘获存储器</strong><br>2021.09 — 2023.09 · 项目组成员 · 三星电子产学合作项目<br>设计 Al 掺杂 HfO₂ 电荷俘获层，优化 ALD 与热退火工艺，完成器件制备及 C–V、I–V 特性验证。</p>
<h2>论文成果</h2><p><strong>Interface-Driven Perpendicular Magnetic Anisotropy in In-Situ ALD-Grown Co/Pt Multilayers</strong><br>2026 · 审稿中（据最近简历）</p><p><strong>Atomically Smooth Ultrathin Cobalt Films Prepared by Thermal ALD</strong><br>2026 · 审稿中（据最近简历）</p><p><strong>Support Vector Regression Model for Determining Optimal Parameters of HfAlO Based Charge Trapping Memory Devices</strong><br>2023</p><p><strong>Ferroelectricity-Based Memory Devices: Next-Generation Materials and Applications</strong><br>2023</p>
<h2>学术会议</h2><p>International Conference of Asian Union of Magnetics Societies · 日本冲绳 · 2025<br>International Meeting on Information Display · 韩国釜山 · 2023<br>International Conference on Advanced Electromaterials · 韩国济州 · 2023</p>
<h2>方法与工具</h2><p>ALD、PVD / CVD、MBE、热蒸发、光刻；SEM / TEM、AFM、AES、电学与磁学表征；Python、MATLAB、C++、CAD、Origin。</p></div><div class="article-footer"><button class="text-button" type="button" data-print>打印 / 保存为 PDF</button><a href="/">返回首页</a></div></main>'''+footer()+'</body></html>'
    write('cv/index.html',cv)
    write('404.html',head('页面未找到','返回胡逸凡的主页。','/404.html')+'<body class="reader-page">'+header()+'<main class="reader" id="main"><div class="article-kicker">404</div><h1 class="article-title">这页走远了。</h1><p>回到首页，继续读一点别的。</p><a class="back-link" href="/">← 返回首页</a></main>'+footer()+'</body></html>')
    urls=['/','/cv/','/life/','/contact/']+[f'/writing/{p["slug"]}/' for p in posts]
    write('sitemap.xml','<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE}{p}</loc></url>' for p in urls)+'</urlset>')
    write('robots.txt',f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    entries=[]
    for p in posts:
        if not p.get('date'): continue
        url=f'{BASE}/writing/{p["slug"]}/'
        entries.append(f'<entry><title>{esc(p["title"])}</title><id>{url}</id><link href="{url}"/><updated>{p["date"]}T00:00:00+09:00</updated><summary>{esc(p.get("excerpt") or p["paragraphs"][0][:140])}</summary></entry>')
    write('feed.xml','<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>胡逸凡 · 写作与生活</title><id>'+BASE+'/</id><link href="'+BASE+'/feed.xml" rel="self"/><link href="'+BASE+'/#writing"/><updated>2026-10-22T00:00:00+09:00</updated>'+''.join(entries)+'</feed>')
    print(json.dumps({'pages':len(posts)+5,'articles':len(posts),'characters':sum(sum(len(s) for s in p['paragraphs']) for p in posts),'output':str(OUT)},ensure_ascii=False))

if __name__=='__main__': build()
