# -*- coding: utf-8 -*-
"""機械学習1 中間の図。部品は engine/figkit.py（全ノート共通）。
クラスは色だけに頼らず形でも区別する：ω1＝丸（オレンジ）、ω2＝三角（青緑）、ω3＝四角（グレー）。
座標はすべて本文の例題の数値そのもの。"""
from figkit import *  # noqa: F401,F403


# ───────────── 図の中だけで使う小道具（名前が _ で始まるものは @fig には出ない） ─────────────
class _Frame:
    """数学の座標 (x, y) → SVG の座標。y は上向きを正にする。sx＝sy にしておくと角度がそのまま見える"""
    def __init__(self, xmin, xmax, ymin, ymax, w, h, pad=34):
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.w, self.h, self.pad = w, h, pad
        self.sx = (w - 2 * pad) / (xmax - xmin)
        self.sy = (h - 2 * pad) / (ymax - ymin)

    def X(self, x):
        return self.pad + (x - self.xmin) * self.sx

    def Y(self, y):
        return self.h - self.pad - (y - self.ymin) * self.sy

    def P(self, x, y):
        return self.X(x), self.Y(y)

    def axes(self, xl="x₁", yl="x₂", ticks=True):
        b = ""
        if self.ymin <= 0 <= self.ymax:
            b += f'<line x1="{self.X(self.xmin):.1f}" y1="{self.Y(0):.1f}" x2="{self.X(self.xmax):.1f}" y2="{self.Y(0):.1f}" class="s-ax"/>'
        if self.xmin <= 0 <= self.xmax:
            b += f'<line x1="{self.X(0):.1f}" y1="{self.Y(self.ymin):.1f}" x2="{self.X(0):.1f}" y2="{self.Y(self.ymax):.1f}" class="s-ax"/>'
        ax_y = self.Y(0) if self.ymin <= 0 <= self.ymax else self.Y(self.ymin)
        ax_x = self.X(0) if self.xmin <= 0 <= self.xmax else self.X(self.xmin)
        b += text(self.X(self.xmax) + 4, ax_y + 4, xl, "t-m f-ink3")
        b += text(ax_x + 5, self.Y(self.ymax) - 6, yl, "t-m f-ink3")
        if ticks:
            for t in range(int(math.ceil(self.xmin)), int(self.xmax) + 1):
                if t != 0:
                    b += text(self.X(t), ax_y + 14, str(t), "t-s f-ink3", "middle")
            for t in range(int(math.ceil(self.ymin)), int(self.ymax) + 1):
                if t != 0:
                    b += text(ax_x - 6, self.Y(t) + 4, str(t), "t-s f-ink3", "end")
        return b

    def line(self, x1, y1, x2, y2, cls="s-main", extra=""):
        return f'<line x1="{self.X(x1):.1f}" y1="{self.Y(y1):.1f}" x2="{self.X(x2):.1f}" y2="{self.Y(y2):.1f}" class="{cls}" {extra}/>'

    def clip_line(self, a, b, c, cls="s-main", extra=""):
        """a·x + b·y + c = 0 を枠の中だけ描く"""
        pts = []
        for x in (self.xmin, self.xmax):
            if abs(b) > 1e-12:
                y = -(a * x + c) / b
                if self.ymin - 1e-9 <= y <= self.ymax + 1e-9:
                    pts.append((x, y))
        for y in (self.ymin, self.ymax):
            if abs(a) > 1e-12:
                x = -(b * y + c) / a
                if self.xmin - 1e-9 <= x <= self.xmax + 1e-9:
                    pts.append((x, y))
        pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in pts))
        if len(pts) < 2:
            return ""
        (x1, y1), (x2, y2) = pts[0], pts[-1]
        return self.line(x1, y1, x2, y2, cls, extra)

    def along(self, x, y, slope, s, cls="t-s f-ink3", off=-6, anchor="middle"):
        """直線（傾き slope）に沿って字を置く。off は線からのずらし（px、負で線の上側）"""
        ang = -math.degrees(math.atan2(slope * self.sy, self.sx))
        X, Y = self.P(x, y)
        r = math.radians(ang)
        X += -math.sin(r) * off
        Y += math.cos(r) * off
        return text(X, Y, s, cls, anchor, f'transform="rotate({ang:.1f} {X:.1f} {Y:.1f})"')


def _mark(fr, x, y, cls, r=6):
    """クラスの印：ω1 丸／ω2 三角／ω3 四角"""
    X, Y = fr.P(x, y)
    if cls == 1:
        return f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" class="f-ou"/>'
    if cls == 2:
        return f'<path d="M{X:.1f},{Y - r - 1:.1f} L{X + r + 1:.1f},{Y + r:.1f} L{X - r - 1:.1f},{Y + r:.1f} z" class="f-link"/>'
    return f'<rect x="{X - r + 1:.1f}" y="{Y - r + 1:.1f}" width="{2 * r - 2}" height="{2 * r - 2}" class="f-k"/>'


def _ring(fr, x, y, r=11):
    X, Y = fr.P(x, y)
    return f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" class="s-main"/>'


def _arrow(fr, x1, y1, x2, y2, idn, accent=False, cls=None):
    """矢印。idn は arrow_defs(idn) で作った印の名前（図ごとに変える）"""
    c = cls or ("s-main" if accent else "s-2")
    return fr.line(x1, y1, x2, y2, c, f'marker-end="url(#{idn}{"o" if accent else ""})"')


# ───────────────────────────── 第1回 ─────────────────────────────
def nn_boundary():
    """お手本がクラスに1個ずつの最近傍決定則 → 境界は垂直二等分線（直線）の組み合わせ"""
    P = {1: (1, 3), 2: (4, 4), 3: (3, 1)}
    fr = _Frame(0, 5, 0, 5, 340, 340)
    b = fr.axes()
    # 外心（3本の垂直二等分線が交わる点）
    (ax, ay), (bx, by), (cx, cy) = P[1], P[2], P[3]
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    # pi と pj の垂直二等分線のうち、残りの pk より pi・pj に近い側（＝境界として残る半直線）だけ描く
    for i, j, k in ((1, 2, 3), (2, 3, 1), (1, 3, 2)):
        (xi, yi), (xj, yj), (xk, yk) = P[i], P[j], P[k]
        mx, my = (xi + xj) / 2, (yi + yj) / 2
        dx, dy = -(yj - yi), (xj - xi)
        if dx * (mx - xk) + dy * (my - yk) < 0:
            dx, dy = -dx, -dy
        tt = []
        for bound, comp, s in ((fr.xmin, dx, ux), (fr.xmax, dx, ux), (fr.ymin, dy, uy), (fr.ymax, dy, uy)):
            if abs(comp) > 1e-12:
                tv = (bound - s) / comp
                if tv > 0:
                    tt.append(tv)
        t = min(tt)
        b += fr.line(ux, uy, ux + dx * t, uy + dy * t, "s-main")
    x = (2, 3)
    for k, p in P.items():
        b += fr.line(x[0], x[1], p[0], p[1], "s-dash")
        b += _mark(fr, p[0], p[1], k, 7)
    lab = {1: ("p₁（ω₁）", 0, -14, "middle"), 2: ("p₂（ω₂）", 0, -14, "middle"), 3: ("p₃（ω₃）", 12, 16, "start")}
    for k, (s, ox, oy, an) in lab.items():
        X, Y = fr.P(*P[k])
        b += text(X + ox, Y + oy, s, "t-m f-ink2", an)
    X, Y = fr.P(*x)
    b += f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="4.5" class="f-ink"/>'
    b += text(X - 4, Y + 18, "x", "t-m f-ink", "end")
    b += text(fr.X(1.5), fr.Y(2.78), "1", "t-s f-ou", "middle")
    b += text(fr.X(3.1), fr.Y(3.6), "√5", "t-s f-ink3", "middle")
    b += text(fr.X(2.65), fr.Y(2.1), "√5", "t-s f-ink3", "middle")
    return svg(340, 340, b, "最近傍決定則の決定境界")


# ───────────────────────────── 第2回 ─────────────────────────────
def perceptron_update():
    """講義と同じ見せ方：1次元の特徴 x₁ に x₀＝1 を足すと、全パターンは x₀＝1 の横線に並び、境界は原点を通る直線になる。
    ω₁ なのに g＜0 になったパターン x を w に足す（w′＝w＋ρx）と、境界が回って x が正しい側に入る"""
    fr = _Frame(-4, 4, -2, 2, 420, 248, pad=34)
    b = arrow_defs("pu") + fr.axes("x₁", "x₀", ticks=False)
    b += fr.line(fr.xmin, 1, fr.xmax, 1, "s-grid")
    b += text(fr.X(fr.xmax) + 4, fr.Y(1) + 4, "x₀＝1", "t-s f-ink3")
    w, rho = (-1.0, -1.5), 0.5          # (w₁, w₀)
    xm = (-1.2, 1.0)                    # 間違えた ω₁ のパターン
    w2 = (w[0] + rho * xm[0], w[1] + rho * xm[1])
    b += fr.clip_line(w[0], w[1], 0, "s-dash")       # 修正前の境界 w₁x₁＋w₀x₀＝0
    b += fr.clip_line(w2[0], w2[1], 0, "s-main")     # 修正後の境界
    for x1 in (-3.4, -2.8, -2.2):
        b += _mark(fr, x1, 1, 1, 6)
    b += _mark(fr, xm[0], 1, 1, 6) + _ring(fr, xm[0], 1, 10)
    for x1 in (-0.4, 0.5, 1.4, 3.0):
        b += _mark(fr, x1, 1, 2, 6)
    b += _arrow(fr, 0, 0, *w, "pu")
    b += _arrow(fr, *w, *w2, "pu", cls="s-3")
    b += _arrow(fr, 0, 0, *w2, "pu", accent=True)
    X, Y = fr.P(*w)
    b += text(X + 8, Y + 4, "w", "t-m f-ink2")
    X, Y = fr.P(*w2)
    b += text(X - 8, Y + 2, "w′＝w＋ρx", "t-m f-ou", "end")
    X, Y = fr.P((w[0] + w2[0]) / 2, (w[1] + w2[1]) / 2)
    b += text(X - 6, Y + 14, "ρx", "t-s f-link", "end")
    X, Y = fr.P(xm[0], 1)
    b += text(X, Y - 15, "x", "t-m f-ink", "middle")
    b += text(fr.X(-3.9), fr.Y(0.45), "ω₁（g＞0 にしたい）", "t-s f-ink2")
    b += text(fr.X(3.9), fr.Y(0.45), "ω₂（g＜0 にしたい）", "t-s f-ink2", "end")
    b += fr.line(0.45, 1.78, 0.95, 1.78, "s-main") + text(fr.X(1.05), fr.Y(1.78) + 4, "修正後の境界（w′ に垂直）", "t-s f-ou")
    b += fr.line(0.45, 1.43, 0.95, 1.43, "s-dash") + text(fr.X(1.05), fr.Y(1.43) + 4, "修正前の境界（w に垂直）", "t-s f-ink3")
    return svg(420, 248, b, "パーセプトロンの誤り訂正")


def perceptron_example():
    """例題の4点と、収束後の境界 2＋5x₁−6x₂＝0"""
    fr = _Frame(0, 3, 0, 3.5, 300, 340, pad=34)
    b = fr.axes()
    b += fr.clip_line(5, -6, 2, "s-main")
    for (x1, x2, c, s, ox, oy) in ((1, 1, 1, "x₁", 10, 14), (1, 2, 2, "x₂", -10, 4), (2, 3, 2, "x₃", 11, 4), (2, 1, 1, "x₄", 10, 14)):
        b += _mark(fr, x1, x2, c, 7)
        X, Y = fr.P(x1, x2)
        b += text(X + ox, Y + oy, s, "t-m f-ink2", "end" if ox < 0 else "start")
    b += fr.along(0.75, (2 + 5 * 0.75) / 6, 5 / 6, "2＋5x₁−6x₂＝0", "t-s f-ou", -7)
    b += text(fr.X(2.95), fr.Y(0.25), "g＞0 → ω₁", "t-s f-ink3", "end")
    b += text(fr.X(0.12), fr.Y(3.3), "g＜0 → ω₂", "t-s f-ink3")
    return svg(300, 340, b, "例題の決定境界")


# ───────────────────────────── 第3回 ─────────────────────────────
def bayes_1d():
    """1次元のベイズ識別：P(ω)p(x|ω) の大きい方を選ぶ。2つの山が交わる所が境界"""
    def gauss(x, m, s):
        return math.exp(-(x - m) ** 2 / (2 * s * s)) / (math.sqrt(2 * math.pi) * s)
    P1, m1, s1 = 0.6, -1.0, 1.0
    P2, m2, s2 = 0.4, 1.5, 0.8
    f1 = lambda x: P1 * gauss(x, m1, s1)
    f2 = lambda x: P2 * gauss(x, m2, s2)
    lo, hi = -1.0, 1.5                  # 交点を二分法で
    for _ in range(60):
        mid = (lo + hi) / 2
        if (f1(lo) - f2(lo)) * (f1(mid) - f2(mid)) <= 0:
            hi = mid
        else:
            lo = mid
    xb = (lo + hi) / 2
    fr = _Frame(-4, 4, 0, 0.27, 420, 250, pad=30)
    b = fr.axes("x", "", ticks=False)
    xs = [fr.xmin + i * (fr.xmax - fr.xmin) / 200 for i in range(201)]
    b += f'<path d="{path([fr.P(x, f1(x)) for x in xs])}" class="s-main"/>'
    b += f'<path d="{path([fr.P(x, f2(x)) for x in xs])}" class="s-3"/>'
    b += fr.line(xb, 0, xb, 0.25, "s-dash")
    b += text(fr.X(xb), fr.Y(0) + 16, "境界", "t-s f-ink2", "middle")
    b += text(fr.X(-1.0), fr.Y(f1(-1.0)) - 8, "P(ω₁)p(x|ω₁)", "t-m f-ou", "middle")
    b += text(fr.X(2.3), fr.Y(f2(1.5)) - 8, "P(ω₂)p(x|ω₂)", "t-m f-link", "middle")
    b += text(fr.X(-3.9), fr.Y(0) + 16, "← ω₁ と判定", "t-s f-ink3")
    b += text(fr.X(3.9), fr.Y(0) + 16, "ω₂ と判定 →", "t-s f-ink3", "end")
    return svg(420, 250, b, "1次元のベイズ識別")


def boundary_ratio():
    """境界比 r(x)＝‖x′−y‖ / ‖x−y‖。x が境界に近いほど 1 に近い"""
    fr = _Frame(-0.6, 3.6, -0.7, 1.3, 380, 200, pad=26)
    b = ""
    x, y, xp = (0, 0), (3, 0), (2.2, 0.6)
    b += fr.line(*x, *y, "s-dash")
    b += fr.line(*xp, *y, "s-main")
    b += _mark(fr, *x, 1, 7) + _mark(fr, *xp, 1, 7) + _mark(fr, *y, 2, 7)
    X, Y = fr.P(*x)
    b += text(X, Y + 22, "x", "t-m f-ink", "middle")
    X, Y = fr.P(*xp)
    b += text(X + 4, Y - 13, "x′（y に一番近い、x と同じクラス）", "t-s f-ink2", "end")
    X, Y = fr.P(*y)
    b += text(X + 10, Y + 24, "y（x に一番近い、他のクラス）", "t-s f-ink2", "end")
    b += text(fr.X(1.1), fr.Y(0) - 7, "‖x−y‖＝3", "t-s f-ink3", "middle")
    b += text(fr.X(2.72), fr.Y(0.42), "1", "t-s f-ou", "start")
    return svg(380, 200, b, "境界比")


# ───────────────────────────── 第4回 ─────────────────────────────
def phi_circle():
    """原空間では円でしか分けられない2クラスが、φ₁＝x₁²、φ₂＝x₂² の Φ空間では直線で分かれる"""
    W, H = 640, 300
    L = _Frame(-3.6, 3.6, -3.6, 3.6, 300, 300, pad=24)
    R = _Frame(-0.8, 10.2, -0.8, 10.2, 300, 300, pad=28)
    b = L.axes("x₁", "x₂", ticks=False)
    for k in range(16):
        t = 2 * math.pi * k / 16
        b += _mark(L, 3 * math.cos(t), 3 * math.sin(t), 1, 5)
    for k in range(10):
        t = 2 * math.pi * (k + 0.5) / 10
        b += _mark(L, math.cos(t), math.sin(t), 2, 5)
    r5 = math.sqrt(5)
    b += f'<circle cx="{L.X(0):.1f}" cy="{L.Y(0):.1f}" r="{r5 * L.sx:.1f}" class="s-main"/>'
    b += text(L.X(0), L.Y(-3.6) + 16, "原空間：直線では分けられない", "t-s f-ink2", "middle")
    b += text(L.X(-0.12), L.Y(1.38), "半径√5", "t-s f-ou", "end")
    rb = R.axes("φ₁", "φ₂", ticks=False)
    for k in range(16):
        t = 2 * math.pi * k / 16
        rb += _mark(R, (3 * math.cos(t)) ** 2, (3 * math.sin(t)) ** 2, 1, 5)
    for k in range(10):
        t = 2 * math.pi * (k + 0.5) / 10
        rb += _mark(R, math.cos(t) ** 2, math.sin(t) ** 2, 2, 5)
    rb += R.clip_line(1, 1, -5, "s-main")
    rb += R.along(3.2, 1.8, -1, "φ₁＋φ₂＝5", "t-s f-ou", -7)
    rb += R.along(6.5, 2.5, -1, "φ₁＋φ₂＝9", "t-s f-ink3", -10)
    rb += text(R.X(1.9), R.Y(-0.6), "φ₁＋φ₂＝1", "t-s f-ink3")
    rb += text(R.X(5.2), R.Y(9.6), "Φ空間：直線で分けられる", "t-s f-ink2", "middle")
    b += f'<g transform="translate(330,0)">{rb}</g>'
    b += arrow_defs("pc") + '<path d="M298,150 L326,150" class="s-2" marker-end="url(#pc)"/>'
    return svg(W, H, b, "原空間とΦ空間")


# ───────────────────────────── 第5回 ─────────────────────────────
def margin():
    """3点の例：境界 x₁＋x₂＝0、マージンの端 x₁＋x₂＝±2。端の線に乗った2点がサポートベクトル"""
    fr = _Frame(-3, 3, -3, 3, 340, 340)
    b = fr.axes()
    b += fr.clip_line(1, 1, 0, "s-main")
    b += fr.clip_line(1, 1, -2, "s-dash")
    b += fr.clip_line(1, 1, 2, "s-dash")
    pts = [((1, 1), 1, "x₁"), ((-1, -1), 2, "x₂"), ((2, 1), 1, "x₃")]
    for (p, c, s) in pts:
        b += _mark(fr, *p, c, 7)
        X, Y = fr.P(*p)
        b += text(X + 11, Y + 16, s, "t-m f-ink2")
    b += _ring(fr, 1, 1) + _ring(fr, -1, -1)
    b += fr.line(1, 1, 0, 0, "s-3", 'stroke-dasharray="4 3"')
    b += fr.along(-2.0, 2.0, -1, "g＝0", "t-s f-ou", -6)
    b += fr.along(-0.6, 2.6, -1, "g＝1", "t-s f-ink3", -6)
    b += fr.along(-2.6, 0.6, -1, "g＝−1", "t-s f-ink3", -6)
    b += text(fr.X(0.62), fr.Y(0.12), "r＝1/‖w‖", "t-s f-link")
    b += text(fr.X(-2.9), fr.Y(-2.75), "◯＝サポートベクトル", "t-s f-ink2")
    return svg(340, 340, b, "マージンとサポートベクトル")


def lagrange():
    """不等式制約の2つの場合：最小点が領域の中（α＝0）／外（境界上で ∇f と ∇g が逆向き）"""
    W, H = 600, 250
    b = arrow_defs("lg")
    for k, (note1, note2) in enumerate((("f の最小点が領域の中", "→ ∇f＝0、α＝0"), ("f の最小点が領域の外", "→ 境界上で ∇f＝−α∇g（α＞0）"))):
        ox = k * 300
        b += f'<circle cx="{ox + 120:.1f}" cy="150" r="62" class="f-oubg"/>'
        b += f'<circle cx="{ox + 120:.1f}" cy="150" r="62" class="s-2"/>'
        b += text(ox + 120, 186, "g≤0", "t-s f-ink3", "middle")
        ex, ey = (ox + 120, 140) if k == 0 else (ox + 205, 70)
        for s in (16, 32, 48, 64):
            b += f'<ellipse cx="{ex}" cy="{ey}" rx="{s * 1.35:.1f}" ry="{s * 0.7:.1f}" transform="rotate(-25 {ex} {ey})" class="s-dash"/>'
        if k == 0:
            b += f'<circle cx="{ex}" cy="{ey}" r="5" class="f-ou"/>'
            b += text(ex + 8, ey - 8, "最適解", "t-s f-ou")
        else:
            vx, vy = ex - (ox + 120), ey - 150
            n = math.hypot(vx, vy)
            px, py = ox + 120 + 62 * vx / n, 150 + 62 * vy / n
            b += f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px + 34 * vx / n:.1f}" y2="{py + 34 * vy / n:.1f}" class="s-2" marker-end="url(#lg)"/>'
            b += f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px - 34 * vx / n:.1f}" y2="{py - 34 * vy / n:.1f}" class="s-main" marker-end="url(#lgo)"/>'
            b += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" class="f-ou"/>'
            b += text(px + 34 * vx / n + 6, py + 34 * vy / n + 4, "∇g", "t-s f-ink2")
            b += text(px - 34 * vx / n - 6, py - 34 * vy / n + 4, "∇f", "t-s f-ou", "end")
            b += text(px + 9, py + 14, "最適解", "t-s f-ou")
        b += text(ox + 120, 230, note1, "t-m f-ink2", "middle")
        b += text(ox + 120, 246, note2, "t-s f-ink3", "middle")
    return svg(W, H, b, "ラグランジュの未定乗数法の2つの場合")


# ───────────────────────────── 第6回 ─────────────────────────────
def soft_margin():
    """ソフトマージン：g＝x₁−x₂。マージンの内側に入った点は 0＜ξ＜1、境界の反対側まで入った点は ξ＞1"""
    fr = _Frame(-0.5, 4, -0.5, 4, 340, 340)
    b = fr.axes()
    b += fr.clip_line(1, -1, 0, "s-main")
    b += fr.clip_line(1, -1, -1, "s-dash")
    b += fr.clip_line(1, -1, 1, "s-dash")
    for p in ((2.6, 0.5), (3.5, 1.9), (3.6, 0.4), (2.0, -0.1)):
        b += _mark(fr, *p, 1, 6)
    for p in ((0.2, 1.8), (0.5, 2.7), (1.2, 3.0), (-0.2, 1.0)):
        b += _mark(fr, *p, 2, 6)
    a, c = (1.8, 1.4), (1.5, 2.2)       # g＝0.4 → ξ＝0.6 ／ g＝−0.7 → ξ＝1.7（どちらも ω₁）
    b += _mark(fr, *a, 1, 6) + _ring(fr, *a) + _mark(fr, *c, 1, 6) + _ring(fr, *c)
    X, Y = fr.P(*a)
    b += text(X + 24, Y + 15, "A：ξ＝0.6", "t-s f-ou")
    X, Y = fr.P(*c)
    b += text(X - 14, Y - 8, "B：ξ＝1.7", "t-s f-ou", "end")
    b += fr.along(3.3, 3.3, 1, "g＝0", "t-s f-ou", -6)
    b += fr.along(3.5, 2.5, 1, "g＝1", "t-s f-ink3", 13)
    b += fr.along(2.4, 3.4, 1, "g＝−1", "t-s f-ink3", -6)
    return svg(340, 340, b, "ソフトマージンとスラック変数")
