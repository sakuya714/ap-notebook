# -*- coding: utf-8 -*-
"""本文の記法（notes/*/content/*.txt）→ HTML。全ノート共通。記法の一覧は README.md。

ここには「どの科目でも使う部品」だけを置く。科目の言葉（応用・基本情報・パーセプトロン…）は書かない。
"""
import re, html

def esc(s):
    return html.escape(s, quote=False)

def attr(s):
    return html.escape(s, quote=True)

class Ctx:
    """1冊ぶんの共有情報（章の一覧・公式・ペアなど、巻末や表紙に集めるもの）"""
    def __init__(self, figs):
        self.figs = figs
        self.parts = []      # [(id, title, sub, short, [(ch_id, title, sub)])]
        self.chapters = {}   # ch_id → title
        self.formulas = []   # (ch_id, label, lines, accent)
        self.pairs = []      # (group, a, b, how, ch_id)
        self.boards = []     # (id, chip)  上部バーに出す見出し
        self.uses = set()    # 使った部品（凡例・フィルタ・数式の読み込みに使う）

# ───────────── 文中の記法 ─────────────
MATH_INLINE = re.compile(r"(?<![\\$])\$(?!\$)(.+?)(?<!\\)\$")

def inline(s, ctx=None):
    # 数式は先に退避して、中身を ** や == の置換から守る
    maths = []
    def keep(m):
        maths.append(m.group(1)); return f"\x00{len(maths) - 1}\x00"
    s = MATH_INLINE.sub(keep, s)
    s = esc(s)
    if ctx is not None and "{{" in s:
        ctx.uses.add("xref")
    s = re.sub(r"\{\{([\w.-]+)\}\}", lambda m: f'<a class="xr" href="#c-{m.group(1)}">→{m.group(1)}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"==(.+?)==", r'<span class="hl">\1</span>', s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    if maths and ctx is not None:
        ctx.uses.add("math")
    return re.sub(r"\x00(\d+)\x00", lambda m: "\\(" + esc(maths[int(m.group(1))]) + "\\)", s)

def split_bar(s, n):
    parts = [x.strip() for x in s.split("|")]
    return (parts + [""] * n)[:n]

def flow_html(spec, ctx):
    """A::補足 >[ラベル] +B > C  →  箱を矢印でつないだ流れ図（+ はアクセント色の箱）"""
    toks = re.split(r"\s>(\[[^\]]*\])?\s", " " + spec.strip() + " ")
    nodes, labs = toks[0::2], toks[1::2]
    out = []
    for k, n in enumerate(nodes):
        n = n.strip()
        if not n:
            continue
        cls = "n"
        if n.startswith("+"):
            cls += " o"; n = n[1:].strip()
        a, _, b = n.partition("::")
        inner = inline(a.strip(), ctx) + (f"<small>{inline(b.strip(), ctx)}</small>" if b else "")
        if out:
            lab = labs[k - 1] if k - 1 < len(labs) else None
            lab = f"<small>{inline(lab[1:-1], ctx)}</small>" if lab else ""
            out.append(f'<span class="seg"><span class="a">{lab}→</span><span class="{cls}">{inner}</span></span>')
        else:
            out.append(f'<span class="{cls}">{inner}</span>')
    return f'<div class="flow">{"".join(out)}</div>'

# ───────────── ブロック ─────────────
# 1ブロック = (種類, html)。種類 "dense" は用語・公式などの短いもので、続いたら2段組にまとめる。
# "wide" は文章・数式・図など、1段で読ませるもの。
DENSE, WIDE = "dense", "wide"

class Builder:
    def __init__(self, ctx, nested=False):
        self.ctx = ctx
        self.nested = nested
        self.blocks = []        # 今のシート（章・ボード）の中身
        self.out = []           # 完成した HTML
        self.items = None       # 用語グループ
        self.glabel = None
        self.auto_grp = False
        self.fx = None          # 公式 (label, lines, accent)
        self.tbl = None
        self.block = None       # @xxx … @end の中身 (kind, head, lines)
        self.depth = 0          # 入れ子の @xxx を数える
        self.code = None        # ``` の中身
        self.list = None        # 1. 番号付きリスト
        self.container = None   # "sheet" / "board" / None（表紙）
        self.ch = None

    # ── 小さい部品を閉じる ──
    def add(self, kind, h):
        self.blocks.append((kind, h))

    def flush_fx(self):
        if self.fx is None:
            return
        label, lines, ou = self.fx
        self.ctx.formulas.append((self.ch, label, lines, ou))
        self.ctx.uses.add("formula")
        body = "\n".join(esc(l) for l in lines)
        self.add(DENSE, f'<div class="fx{" o" if ou else ""}"><div class="fl">{esc(label) if label else "公式"}</div><pre>{body}</pre></div>')
        self.fx = None

    def flush_tbl(self):
        if self.tbl is None:
            return
        rows = self.tbl
        head = "<tr>" + "".join(f"<th>{inline(c, self.ctx)}</th>" for c in rows[0][1]) + "</tr>"
        body = "".join(f'<tr class="{"o" if ou else ""}">' + "".join(f"<td>{inline(c, self.ctx)}</td>" for c in cells) + "</tr>" for ou, cells in rows[1:])
        base = not any(ou for ou, _ in rows[1:])
        self.add(DENSE, f'<div class="tbw{" k" if base else ""}"><table class="tb"><thead>{head}</thead><tbody>{body}</tbody></table></div>')
        self.tbl = None

    def flush_items(self):
        if self.items is None:
            return
        gl = f'<div class="gl">{inline(self.glabel, self.ctx)}</div>' if self.glabel else ""
        self.add(DENSE, f'<div class="grp">{gl}<div class="items">{"".join(self.items)}</div></div>')
        self.items = None; self.glabel = None

    def flush_list(self):
        if self.list is None:
            return
        self.add(WIDE, "<ol class=\"ol\">" + "".join(f"<li>{x}</li>" for x in self.list) + "</ol>")
        self.list = None

    def flush_small(self):
        self.flush_fx(); self.flush_tbl(); self.flush_list()

    def flush_all(self):
        self.flush_small(); self.flush_items()

    # ── シート（章・ボード）──
    def render_blocks(self):
        """dense が3つ以上続いた所だけ2段組にする。文章・数式・図は1段のまま"""
        res, run = [], []
        def close_run():
            if len(run) >= 3:
                res.append('<div class="cols">' + "".join(run) + "</div>")
            else:
                res.extend(run)
            run.clear()
        for kind, h in self.blocks:
            if kind == DENSE:
                run.append(h)
            else:
                close_run(); res.append(h)
        close_run()
        self.blocks = []
        return "".join(res)

    def close_container(self):
        self.flush_all()
        if self.container:
            self.out.append(self.render_blocks() + "</div></section>")
        elif self.blocks:
            self.out.append(self.render_blocks())
        self.container = None

    def html(self):
        self.close_container()
        return "\n".join(self.out)

    # ── @xxx … @end の中身 ──
    def sub(self, lines):
        b = Builder(self.ctx, nested=True)
        b.ch = self.ch
        for l in lines:
            b.line(l)
        return b.html()

    def render_block(self):
        kind, head, lines = self.block
        self.block = None
        ctx = self.ctx
        title, _, extra = head.partition("|")
        title, extra = title.strip(), extra.strip()
        figs = ctx.figs
        if kind == "map":
            inner = "".join(flow_html(l[5:], ctx) if l.startswith("flow:") else f'<div class="gist">{inline(l.strip(), ctx)}</div>' for l in lines if l.strip())
            self.add(WIDE, f'<div class="cmap"><div class="ml">この章の流れ</div>{inner}</div>')
        elif kind in ("stack", "lad"):
            rows = ""
            if kind == "lad":
                top, bot = split_bar(extra, 2)
                rows += f'<div class="end">{inline(top, ctx)}</div>' if top else ""
            for l in lines:
                if not l.strip():
                    continue
                ou = l.startswith("+"); l = l[1:] if ou else l
                a, _, b = l.partition("::")
                rows += f'<div class="r{" o" if ou else ""}"><b>{inline(a.strip(), ctx)}</b><span>{inline(b.strip(), ctx)}</span></div>'
            if kind == "lad":
                rows += f'<div class="end">{inline(bot, ctx)}</div>' if bot else ""
            cap = inline(extra, ctx) if kind == "stack" and extra else ""
            self.add(DENSE, figs.fig(f'<div class="{kind}">{rows}</div>', inline(title, ctx), cap))
        elif kind == "mx":
            d = {}
            for l in lines:
                k, _, v = l.partition(":")
                d[k.strip()] = v.strip()
            xl, xr = split_bar(d.get("x", "|"), 2)
            yt, yb = split_bar(d.get("y", "|"), 2)
            def cell(key):
                v = d.get(key, "")
                ou = v.startswith("+"); v = v[1:] if ou else v
                a, _, b = v.partition("::")
                return f'<div class="c{" o" if ou else ""}"><b>{inline(a.strip(), ctx)}</b><span>{inline(b.strip(), ctx)}</span></div>'
            g = (f'<div class="mx"><div></div><div class="ax">{inline(xl, ctx)}</div><div class="ax">{inline(xr, ctx)}</div>'
                 f'<div class="ax v">{inline(yt, ctx)}</div>{cell("TL")}{cell("TR")}'
                 f'<div class="ax v">{inline(yb, ctx)}</div>{cell("BL")}{cell("BR")}</div>')
            self.add(DENSE, figs.fig(g, inline(title, ctx), inline(extra, ctx) if extra else ""))
        elif kind == "flows":
            self.add(DENSE, figs.fig("".join(flow_html(l, ctx) for l in lines if l.strip()), inline(title, ctx), inline(extra, ctx) if extra else ""))
        elif kind == "html":
            self.add(WIDE, "\n".join(lines))
        elif kind == "box":
            # @box why|exam|warn|goal 見出し
            tone, _, label = title.partition(" ")
            names = {"why": "なぜ？", "exam": "試験で取る", "warn": "勘違いしやすい", "goal": "ゴール"}
            lab = label.strip() or names.get(tone, "")
            ctx.uses.add("box-" + tone)
            self.add(WIDE, f'<div class="box {attr(tone)}"><div class="bh">{inline(lab, ctx)}</div>{self.sub(lines)}</div>')
        elif kind == "fold":
            self.add(WIDE, f'<details class="fold"><summary>{inline(title or "開く", ctx)}</summary><div class="fb">{self.sub(lines)}</div></details>')
        elif kind == "quiz":
            ctx.uses.add("quiz")
            self.add(WIDE, f'<details class="fold quiz"><summary><span class="qt">確認</span>{inline(title, ctx)}</summary><div class="fb">{self.sub(lines)}</div></details>')
        elif kind == "ox":
            ctx.uses.add("ox")
            rows = ""
            for l in lines:
                l = l.strip()
                if not l:
                    continue
                ans, body = l[0], l[1:].strip()
                q, _, why = body.partition("::")
                ok = "o" if ans in "○oO〇" else "x"
                rows += (f'<li class="oxq" data-a="{ok}"><span class="oxt">{inline(q.strip(), ctx)}</span>'
                         f'<span class="oxb"><button type="button" data-v="o">○</button><button type="button" data-v="x">×</button></span>'
                         f'<span class="oxw">{"○" if ok == "o" else "×"}　{inline(why.strip(), ctx)}</span></li>')
            self.add(WIDE, f'<div class="ox"><div class="bh">{inline(title or "○×で確認", ctx)}</div><ol>{rows}</ol></div>')
        elif kind == "check":
            ctx.uses.add("check")
            rows = "".join(f'<li><label><input type="checkbox"><span>{inline(l.strip(), ctx)}</span></label></li>' for l in lines if l.strip())
            self.add(WIDE, f'<div class="check"><div class="bh">{inline(title or "これが言えたら次へ", ctx)}</div><ul>{rows}</ul></div>')
        elif kind == "steps":
            rows = ""
            for l in lines:
                if not l.strip():
                    continue
                a, _, b = l.partition("::")
                rows += f'<li><b>{inline(a.strip(), ctx)}</b>{f"<span>{inline(b.strip(), ctx)}</span>" if b else ""}</li>'
            bh = f'<div class="bh">{inline(title, ctx)}</div>' if title else ""
            self.add(WIDE, f'<div class="steps">{bh}<ol>{rows}</ol></div>')
        elif kind == "stats":
            cells = ""
            for l in lines:
                if l.strip():
                    a, _, b = l.partition("::")
                    cells += f'<div><div class="n">{inline(a.strip(), ctx)}</div><div class="l">{inline(b.strip(), ctx)}</div></div>'
            self.add(WIDE, f'<div class="stats">{cells}</div>')
        elif kind == "routes":
            # 名前 | ひとこと | 01-1 反復試行, 02-2 RAID …  （色は順番に自動で付く）
            rows = ""
            for i, l in enumerate(x for x in lines if x.strip()):
                nm, sub, sts = split_bar(l, 3)
                st = ""
                for s in [x.strip() for x in sts.split(",") if x.strip()]:
                    cid, _, lab = s.partition(" ")
                    st += f'<span class="st"><a href="#c-{attr(cid)}"><i>{esc(cid)}</i>{inline(lab.strip(), ctx)}</a></span>'
                rows += f'<div class="mline r{i % 5}"><div class="nm">{inline(nm, ctx)}<small>{inline(sub, ctx)}</small></div><div class="stations">{st}</div></div>'
            self.add(WIDE, f'<div class="metro">{rows}</div>')
        elif kind == "cover":
            d = {}
            for l in lines:
                k, _, v = l.partition(":")
                d[k.strip()] = v.strip()
            ctx.cover = d
            self.add(WIDE, "\x01cover\x01")

    # ── 1行ずつ ──
    def line(self, raw):
        l = raw.rstrip("\n")
        s = l.strip()
        # ``` コード
        if self.code is not None:
            if s.startswith("```"):
                self.add(WIDE, f'<pre class="code">{esc(chr(10).join(self.code))}</pre>'); self.code = None
            else:
                self.code.append(l)
            return
        # @xxx … @end（入れ子に対応）
        if self.block is not None:
            if re.match(r"@(box|fold|quiz|ox|check|steps|stack|lad|mx|flows|html|map|stats|routes|cover)\b", s):
                self.depth += 1
            if s == "@end":
                if self.depth == 0:
                    return self.render_block()
                self.depth -= 1
            self.block[2].append(l)
            return
        if s.startswith("```"):
            self.flush_all(); self.code = []; return
        if not s or s.startswith("//"):
            if not s:
                self.flush_small()
                if self.items is not None and self.auto_grp:
                    self.flush_items()
            return
        # 公式
        if s.startswith("=") and not s.startswith("=="):
            self.flush_tbl(); self.flush_list()
            if self.fx is None:
                self.flush_items(); self.fx = ("", [], False)
            label, lines, ou = self.fx
            body = s[1:]
            if body.lstrip().startswith("#"):
                lab = body.lstrip()[1:].strip()
                if lab.startswith("+"):
                    ou = True; lab = lab[1:].strip()
                self.fx = (lab, lines, ou)
            else:
                lines.append(body[1:] if body.startswith(" ") else body)
            return
        self.flush_fx()
        # 表
        if s.startswith("|") or s.startswith("+|"):
            self.flush_list()
            ou = s.startswith("+|")
            cells = [c.strip() for c in (s[1:] if ou else s).strip().strip("|").split("|")]
            if self.tbl is None:
                self.flush_items(); self.tbl = []
            if ou:
                self.ctx.uses.add("accent")
            self.tbl.append((ou, cells))
            return
        self.flush_tbl()
        # 番号付きリスト
        m = re.match(r"^(\d+)[.．]\s+(.*)$", s)
        if m:
            self.flush_items()
            if self.list is None:
                self.list = []
            self.list.append(inline(m.group(2), self.ctx))
            return
        self.flush_list()

        if re.match(r"@part\s", s):
            self.close_container()
            pid, title, sub, short = split_bar(s[5:], 4)
            self.ctx.parts.append((pid, title, sub, short, []))
            self.out.append(f'<div class="part" id="{attr(pid)}"><span class="pn">{esc(pid.upper())}</span><h2>{esc(title)}</h2><span class="pf">{inline(sub, self.ctx)}</span></div>')
            return
        if re.match(r"@ch\s", s):
            self.close_container()
            cid, title, sub = split_bar(s[3:], 3)
            self.ch = cid
            self.ctx.chapters[cid] = title
            if not self.ctx.parts:
                self.ctx.parts.append(("", "", "", "", []))
            self.ctx.parts[-1][4].append((cid, title, sub))
            self.out.append(f'<section class="sheet" id="c-{attr(cid)}"><header class="sh-head"><div class="divider"><span class="no">{esc(cid)}</span></div>'
                            f'<h3>{inline(title, self.ctx)}</h3><div class="sub">{inline(sub, self.ctx)}</div></header><div class="sh-body">')
            self.container = "sheet"
            return
        if re.match(r"@board\s", s):
            self.close_container()
            bid, title, sub, chip = split_bar(s[6:], 4)
            if chip:
                self.ctx.boards.append((bid, chip))
            bsub = f'<div class="bsub">{inline(sub, self.ctx)}</div>' if sub else ""
            self.out.append(f'<section class="board" id="{attr(bid)}"><h3>{inline(title, self.ctx)}</h3>{bsub}<div class="bb">')
            self.container = "board"
            return
        if s.startswith("@pair "):
            grp, a, b, how, cid = split_bar(s[6:], 5)
            self.ctx.pairs.append((grp, a, b, how, cid))
            return
        for tag in ("@toc", "@formulas", "@pairs", "@legend"):
            if s == tag:
                self.flush_all(); self.add(WIDE, f"\x01{tag[1:]}\x01")  # 全部読み終わってから中身を入れる
                return
        m = re.match(r"@(map|stack|mx|lad|html|flows|box|fold|quiz|ox|check|steps|stats|routes|cover)\b\s*(.*)", s)
        if m:
            self.flush_all()
            self.block = (m.group(1), m.group(2), [])
            self.depth = 0
            return
        if s.startswith("@flow "):
            self.flush_all()
            spec, _, cap = s[6:].partition(" || ")
            self.add(DENSE, self.ctx.figs.fig(flow_html(spec, self.ctx), "", inline(cap, self.ctx) if cap else ""))
            return
        if re.match(r"@fig!?\s", s):
            # @fig 名前 | タイトル | キャプション　（@fig! にすると1段まるごと使う大きい図）
            self.flush_all()
            wide = s.startswith("@fig!")
            name, title, cap = split_bar(s[5 if wide else 4:], 3)
            fn = self.ctx.figs.REGISTRY.get(name)
            if fn is None:
                raise SystemExit(f"@fig {name}: figs.py にその名前の図がありません")
            self.add(WIDE if wide else DENSE, self.ctx.figs.fig(fn(), inline(title, self.ctx), inline(cap, self.ctx), "w" if wide else ""))
            return
        if s.startswith("$$"):
            self.flush_all()
            self.ctx.uses.add("math")
            body = s[2:-2] if s.endswith("$$") and len(s) > 4 else s[2:]
            self.add(WIDE, f'<div class="eq">\\[{esc(body.strip())}\\]</div>')
            return
        if s.startswith("##"):
            self.flush_all()
            self.add(DENSE, f'<div class="sec">{inline(s[2:].strip(), self.ctx)}</div>')
            return
        if s == ")":
            self.flush_items(); return
        if s.startswith("(") and not s.startswith("(（"):
            self.flush_items()
            self.items = []; self.auto_grp = False
            self.glabel = s[1:].strip() or None
            return
        if s.startswith(">"):
            self.flush_items()
            self.ctx.uses.add("hook")
            self.add(DENSE, f'<div class="hook">{inline(s[1:].strip(), self.ctx)}</div>')
            return
        if s.startswith("!"):
            self.flush_items()
            self.add(DENSE, f'<div class="trap">{inline(s[1:].strip(), self.ctx)}</div>')
            return
        m = re.match(r"^([-+])(\*?)\s+(.*)$", s)
        if m:
            kind = "o" if m.group(1) == "+" else "k"
            if kind == "o":
                self.ctx.uses.add("accent")
            if m.group(2):
                self.ctx.uses.add("star")
            star = '<span class="star">★</span>' if m.group(2) else ""
            body = m.group(3)
            if self.items is None:
                self.items = []; self.glabel = None; self.auto_grp = True
            if " — " in body:
                t, d = body.split(" — ", 1)
                self.items.append(f'<span class="t {kind}">{inline(t, self.ctx)}{star}</span><span class="d {kind}">{inline(d, self.ctx)}</span>')
            else:
                self.items.append(f'<span class="full {kind}">{inline(body, self.ctx)}{star}</span>')
            return
        # ふつうの文。短い1行は用語の間に混ぜる（dense）、長い文章は1段で読ませる（wide）
        self.flush_items()
        self.add(DENSE if len(s) <= 60 else WIDE, f'<p class="note">{inline(s, self.ctx)}</p>')
