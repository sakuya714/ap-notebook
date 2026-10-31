# -*- coding: utf-8 -*-
"""図の部品（全ノート共通）。各ノートの figs.py は `from figkit import *` して、図を返す関数だけを書く。

図の関数は「SVG か HTML の文字列」を返す。色は theme の CSS クラス（s-ax, f-ou など）で付けるので、
ここにもノート側にも色の値は書かない（ダーク／ライトの切替で自動的に変わる）。
"""
import math  # noqa: F401  figs.py から使えるように

__all__ = ["math", "svg", "text", "path", "arrow_defs", "fig"]

def svg(w, h, body, label=""):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'

def text(x, y, s, cls="t-s f-ink2", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{s}</text>'

def path(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)

def arrow_defs(idn="ah"):
    """矢印の先端（id=idn は灰色、idn+'o' は金色）。marker-end="url(#ah)" のように使う"""
    return (f'<defs><marker id="{idn}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" class="f-ink3"/></marker>'
            f'<marker id="{idn}o" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" class="f-ou"/></marker></defs>')

def fig(inner, title="", cap="", cls=""):
    """図の枠（タイトル＋本体＋キャプション）。本文の @fig からも使う"""
    t = f'<div class="ttl">{title}</div>' if title else ""
    c = f'<div class="cap">{cap}</div>' if cap else ""
    return f'<div class="fig {cls}">{t}{inner}{c}</div>'
