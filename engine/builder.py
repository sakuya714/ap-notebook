# -*- coding: utf-8 -*-
"""サイトの組み立て：notes/ のノートを theme/ の型に流し込んで docs/ に出す。全ノート共通。"""
import os, re, json, shutil, glob, importlib.util, inspect

from markup import Ctx, Builder, esc, attr, inline
from search import text_index
import check

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES = os.path.join(ROOT, "notes")
THEME = os.path.join(ROOT, "theme")
DOCS = os.path.join(ROOT, "docs")
ASSETS = "_"  # docs/_/ に共通の CSS・JS を置く
SITE = ("Notebook", "Hub")  # サイト名（前半・後半。後半がアクセント色になる）

def natural(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]

# ───────────── notes/ を読む ─────────────
def scan(dirpath, rel=""):
    """notes/ のフォルダ構造＝サイドバーの並び。note.json があるフォルダが1冊"""
    kids = []
    for name in sorted(os.listdir(dirpath), key=natural):
        full = os.path.join(dirpath, name)
        if name.startswith((".", "_")) or not os.path.isdir(full):
            continue
        r = f"{rel}/{name}" if rel else name
        if os.path.exists(os.path.join(full, "note.json")):
            with open(os.path.join(full, "note.json"), encoding="utf-8") as fh:
                kids.append({"type": "note", "name": name, "path": r, "dir": full, "cfg": json.load(fh)})
        else:
            kids.append({"type": "dir", "name": name, "path": r, "children": scan(full, r)})
    return [k for k in kids if k["type"] == "dir"] + [k for k in kids if k["type"] == "note"]

def load_figs(note_dir):
    """ノートの figs.py を読む。中で定義した関数がそのまま @fig の名前になる"""
    import figkit
    path = os.path.join(note_dir, "figs.py")
    if not os.path.exists(path):
        return type("Figs", (), {"fig": staticmethod(figkit.fig), "REGISTRY": {}})
    spec = importlib.util.spec_from_file_location("figs_" + str(abs(hash(path))), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.REGISTRY = {k: v for k, v in vars(mod).items()
                    if inspect.isfunction(v) and v.__module__ == mod.__name__ and not k.startswith("_")}
    mod.fig = figkit.fig
    return mod

# ───────────── 全部読み終わってから入れる部品 ─────────────
def cover_html(ctx, cfg):
    d = getattr(ctx, "cover", {})
    labels = cfg.get("labels", {})
    title = d.get("title") or cfg.get("title", "")
    tag = f'<span class="k">{inline(d["tag"])}</span>' if d.get("tag") else ""
    eyebrow = f'<div class="eyebrow">{inline(d["eyebrow"])}</div>' if d.get("eyebrow") else ""
    lead = f'<p class="lead">{inline(d["lead"])}</p>' if d.get("lead") else ""
    # 凡例は「このノートで実際に使った印」だけ出す
    lg = []
    if "accent" in ctx.uses:
        lg.append(f'<span><i class="dot k"></i>{esc(labels.get("base", "ふつう"))}</span>')
        lg.append(f'<span class="o"><i class="dot o"></i>{esc(labels.get("accent", "大事なところ"))}</span>')
    if "star" in ctx.uses:
        lg.append(f'<span><span class="star">★</span>{esc(labels.get("star", "よく出る"))}</span>')
    if "xref" in ctx.uses:
        lg.append('<span><span class="xr">→章</span> つながってる章</span>')
    if "hook" in ctx.uses:
        lg.append('<span class="hand">✎ 覚え方メモ</span>')
    legend = f'<div class="legend">{"".join(lg)}</div>' if lg else ""
    return f'<header class="cover">{eyebrow}<h1>{esc(title)}{tag}</h1>{lead}{legend}</header>'

def toc_html(ctx):
    pg = ""
    for pid, title, sub, short, chs in ctx.parts:
        lis = "".join(f'<li><a href="#c-{attr(c)}"><i>{esc(c)}</i>{inline(t)}</a></li>' for c, t, _ in chs)
        h = f'<div class="h"><b>{esc(title)}</b><span>{esc(pid.upper())}</span></div><div class="fld">{inline(sub)}</div>' if title else ""
        pg += f'<div class="pcard">{h}<ul>{lis}</ul></div>'
    return f'<div class="pgrid">{pg}</div>'

def formulas_html(ctx):
    fs = "".join(f'<div class="fx{" o" if ou else ""}"><div class="fl">{esc(lab) if lab else "公式"} '
                 f'<a class="xr src" href="#c-{attr(ch or "")}">{esc(ch or "")}</a></div><div class="fxb">{chr(10).join(inline(l) for l in lines)}</div></div>'
                 for ch, lab, lines, ou in ctx.formulas)
    return f'<div class="fsheet">{fs}</div>'

def chip(ch):
    return f'<a class="xr" href="#c-{attr(ch)}">{esc(ch)}</a>' if ch else ""

def pairs_html(ctx):
    groups = {}
    for g, a, b, how, ch in ctx.pairs:
        groups.setdefault(g, []).append((a, b, how, ch))
    out = ""
    for g, rows in groups.items():
        trs = "".join(f'<tr><td>{inline(a)}</td><td>{inline(b)}</td><td>{inline(how)}</td>'
                      f'<td>{chip(ch)}</td></tr>' for a, b, how, ch in rows)
        head = f'<div class="sec">{esc(g)}</div>' if g else ""
        out += f'{head}<div class="tbw"><table class="tb pairs"><thead><tr><th>A</th><th>B</th><th>見分け方（A ／ B）</th><th></th></tr></thead><tbody>{trs}</tbody></table></div>'
    return out

# ───────────── 1冊を組み立てる ─────────────
TYPES = ("整理型", "理解型")  # どう書いたか（書く前に決めて note.json に入れる。見た目・部品は同じ）

def build_note(node, tpl):
    cfg, src = node["cfg"], node["dir"]
    if cfg.get("type") not in TYPES:
        raise SystemExit(f"{node['path']}/note.json: \"type\" に 整理型 か 理解型 を書いてください")
    ctx = Ctx(load_figs(src))
    b = Builder(ctx)
    files = sorted(glob.glob(os.path.join(src, "content", "*.txt")), key=lambda f: natural(os.path.basename(f)))
    if not files:
        raise SystemExit(f"{node['path']}: content/*.txt がありません")
    for f in files:
        with open(f, encoding="utf-8") as fh:
            for raw in fh:
                b.line(raw)
    body = b.html()
    body = (body.replace("\x01cover\x01", cover_html(ctx, cfg)).replace("\x01toc\x01", toc_html(ctx))
            .replace("\x01formulas\x01", formulas_html(ctx)).replace("\x01pairs\x01", pairs_html(ctx)))
    if "\x01cover\x01" not in body and "<header class=\"cover\">" not in body:
        body = cover_html(ctx, cfg) + body  # @cover を書かなくても表紙（タイトル）は出す

    depth = node["path"].count("/") + 1
    rootp = "../" * depth
    labels = cfg.get("labels", {})
    # 上部バー：パートがあればパート、無ければ章へ。@board の4つ目に名前を書いたボードも並べる
    named_parts = [p for p in ctx.parts if p[1]]
    chips = ([f'<a href="#{attr(p[0])}">{esc(p[0].upper())} {esc(p[3] or p[1])}</a>' for p in named_parts] if named_parts
             else [f'<a href="#c-{attr(c)}">{esc(c)}</a>' for p in ctx.parts for c, _, _ in p[4]])
    chips += [f'<a href="#{attr(bid)}">{esc(chip)}</a>' for bid, chip in ctx.boards]
    fil = ""
    if "accent" in ctx.uses or "formula" in ctx.uses:
        btn = ['<button type="button" data-mode="all" aria-pressed="true">全部</button>']
        if "accent" in ctx.uses:
            btn.append(f'<button type="button" data-mode="accent">{esc(labels.get("accentShort", "大事"))}だけ</button>')
        if "formula" in ctx.uses:
            btn.append('<button type="button" data-mode="fx">公式だけ</button>')
        fil = f'<div class="filters" role="group" aria-label="表示の切替">{"".join(btn)}</div>'
    ups = node["path"].split("/")[:-1]
    crumb = f'<a class="here" href="#top">{"".join(f"<span class=up>{esc(u)}</span><i>/</i>" for u in ups)}{esc(node["name"])}</a>'
    head = ""
    if "math" in ctx.uses:
        head = (f'<script>window.NOTE_MACROS = {json.dumps(cfg.get("macros", {}), ensure_ascii=False)};</script>\n'
                f'<script src="{rootp}{ASSETS}/math.js"></script>\n<script src="{rootp}{ASSETS}/mathjax/tex-svg.js" defer></script>')
    tail = ""
    if os.path.exists(os.path.join(src, "lab.js")):  # 動かせるラボだけはノート側に置いてよい
        tail = '<script src="lab.js"></script>'
    page = fill(tpl, S1=esc(SITE[0]), S2=esc(SITE[1]), TITLE=esc(cfg.get("title", node["name"])), A=f"{rootp}{ASSETS}/", ROOT=rootp, PATH=attr(node["path"]),
                CRUMB=crumb, CHIPS=f'<nav class="chips" aria-label="章">{"".join(chips)}</nav>' if chips else "",
                FILTERS=fil, BODY=body, HEAD_EXTRA=head, TAIL=tail)
    out = os.path.join(DOCS, *node["path"].split("/"))
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)
    if tail:
        shutil.copy(os.path.join(src, "lab.js"), out)
    outline = [(f"c-{c}", f"{c} {t}") for p in ctx.parts for c, t, _ in p[4]]
    return {"type": "note", "name": node["name"], "path": node["path"], "title": cfg.get("title", node["name"]), "type_": cfg["type"]}, text_index(page, outline)

def fill(tpl, **kw):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: kw.get(m.group(1), ""), tpl)

def meta(x):
    """カードの2行目：整理型か理解型か（どう書いたノートか）"""
    return x["type_"]

def home_html(tree):
    flat = lambda ns: [x for n in ns for x in (flat(n["children"]) if n["type"] == "dir" else [n])]
    href = lambda p: "/".join(p.split("/")) + "/index.html"
    sec = ""
    for n in tree:
        notes = flat(n["children"]) if n["type"] == "dir" else [n]
        if not notes:
            continue
        cards = "".join(f'<a class="card" href="{attr(href(x["path"]))}"><span class="t">{esc(x["name"])}</span>'
                        f'<span class="m">{esc(meta(x))}</span></a>' for x in notes)
        sec += f'<h2>{esc(n["name"] if n["type"] == "dir" else "その他")}</h2><div class="cards">{cards}</div>'
    return f'<section class="home"><h1>{esc(SITE[0])} <span>{esc(SITE[1])}</span></h1><p class="lead">試験範囲の総まとめを1か所に。</p>{sec}</section>'

# ───────────── 全部 ─────────────
def note_dirs(nodes):
    return [x for n in nodes for x in (note_dirs(n["children"]) if n["type"] == "dir" else [n["dir"]])]

def run_check():
    errors, warns = check.run(note_dirs(scan(NOTES)))
    print(f"check: エラー {len(errors)} ／ 注意 {len(warns)}")
    return not errors

def build():
    if not run_check():
        raise SystemExit("エラーがあるのでビルドを止めました（docs/ は前のまま）")
    if os.path.isdir(DOCS):
        shutil.rmtree(DOCS)
    a = os.path.join(DOCS, ASSETS)
    os.makedirs(a)
    for f in ("theme.css", "blocks.css", "app.js", "math.js"):
        shutil.copy(os.path.join(THEME, f), a)
    shutil.copytree(os.path.join(THEME, "vendor", "mathjax"), os.path.join(a, "mathjax"))
    with open(os.path.join(THEME, "layout.html"), encoding="utf-8") as fh:
        tpl = fh.read()
    search = {}
    def walk(nodes):
        res = []
        for n in nodes:
            if n["type"] == "dir":
                res.append({"type": "dir", "name": n["name"], "path": n["path"], "children": walk(n["children"])})
            else:
                info, ix = build_note(n, tpl)
                search[n["path"]] = ix
                res.append(info)
        return res
    tree = walk(scan(NOTES))
    with open(os.path.join(a, "tree.js"), "w", encoding="utf-8") as fh:
        fh.write("window.HUB_TREE=" + json.dumps(tree, ensure_ascii=False) + ";\n")
    with open(os.path.join(a, "search.js"), "w", encoding="utf-8") as fh:
        fh.write("window.HUB_SEARCH=" + json.dumps(search, ensure_ascii=False) + ";\n")
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(fill(tpl, TITLE=esc(" ".join(SITE)), A=f"{ASSETS}/", ROOT="", PATH="", BODY=home_html(tree), S1=esc(SITE[0]), S2=esc(SITE[1]),
                      CRUMB=""))
    open(os.path.join(DOCS, ".nojekyll"), "w").close()  # GitHub Pages で _/ を無視させない
    n = sum(1 for _ in search)
    print(f"ok: {n} notes → docs/index.html")
