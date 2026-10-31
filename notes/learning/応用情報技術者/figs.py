# -*- coding: utf-8 -*-
"""応用情報まとめの図。部品は engine/figkit.py（全ノート共通）"""
from figkit import *  # noqa: F401,F403

def mm1():
    X0, X1, Y0, Y1 = 44, 340, 176, 18
    fx = lambda r: X0 + (X1 - X0) * r
    fy = lambda v: Y0 - (Y0 - Y1) * v / 10
    pts = []
    r = 0.0
    while r <= 0.9091:
        pts.append((fx(r), fy(r / (1 - r))))
        r += 0.005
    b = arrow_defs("mm")
    b += f'<line x1="{X0}" y1="{Y0}" x2="{X1+6}" y2="{Y0}" class="s-ax"/><line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1-6}" class="s-ax"/>'
    for v in (1, 4, 9):
        b += f'<line x1="{X0}" y1="{fy(v):.1f}" x2="{X1}" y2="{fy(v):.1f}" class="s-grid"/>'
        b += text(X0 - 6, fy(v) + 4, f"{v}倍", "t-s f-ink3", "end")
    b += f'<path d="{path(pts)}" class="s-main"/>'
    for rr, v in ((0.5, 1), (0.8, 4), (0.9, 9)):
        b += f'<line x1="{fx(rr):.1f}" y1="{Y0}" x2="{fx(rr):.1f}" y2="{fy(v):.1f}" class="s-dash"/>'
        b += f'<circle cx="{fx(rr):.1f}" cy="{fy(v):.1f}" r="3.5" class="f-ou"/>'
        b += text(fx(rr), Y0 + 14, f"ρ={rr}", "t-s f-ink2", "middle")
    b += text(fx(1.0), Y0 + 14, "1", "t-s f-ink3", "middle")
    b += text(X0 + 6, Y1 + 2, "待ち時間 ÷ サービス時間 ＝ ρ/(1−ρ)", "t-s f-ink2")
    b += text(fx(0.55), fy(6.5), "1に近づくと爆発", "t-s f-ou hand")
    return svg(360, 200, b, "M/M/1 待ち時間のグラフ")

def normal():
    X0, X1, Y0, Y1 = 20, 340, 150, 20
    mu, s = (X0 + X1) / 2, (X1 - X0) / 7.4
    f = lambda z: math.exp(-z * z / 2)
    pts = [(mu + z * s, Y0 - (Y0 - Y1) * f(z)) for z in [i / 20 for i in range(-74, 75)]]
    b = ""
    def band(k, cls):
        sub = [(mu + z * s, Y0 - (Y0 - Y1) * f(z)) for z in [i / 20 for i in range(-20 * k, 20 * k + 1)]]
        return f'<path d="{path(sub)} L{mu+k*s:.1f},{Y0} L{mu-k*s:.1f},{Y0} Z" class="{cls}" />'
    b += band(3, "f-oubg") + band(2, "f-oubg") + band(1, "f-oubg")
    b += f'<path d="{path(pts)}" class="s-main"/><line x1="{X0}" y1="{Y0}" x2="{X1}" y2="{Y0}" class="s-ax"/>'
    for k in (-3, -2, -1, 0, 1, 2, 3):
        x = mu + k * s
        b += f'<line x1="{x:.1f}" y1="{Y0}" x2="{x:.1f}" y2="{Y0+4}" class="s-ax"/>'
        lab = "μ" if k == 0 else (f"{'+' if k>0 else '−'}{abs(k)}σ")
        b += text(x, Y0 + 15, lab, "t-s f-ink3", "middle")
    for k, pct, yy in ((1, "68%", 172), (2, "95%", 186), (3, "99.7%", 200)):
        x1, x2 = mu - k * s, mu + k * s
        b += f'<line x1="{x1:.1f}" y1="{yy-4}" x2="{x2:.1f}" y2="{yy-4}" class="s-2"/>'
        b += text(mu, yy - 7, f"±{k}σ に {pct}", "t-s f-ink2", "middle")
    return svg(360, 206, b, "正規分布 68 95 99.7")

def hufftree():
    nodes = {"r": (180, 18, "100%"), "a": (110, 64, "a 50%"), "n1": (250, 64, "50%"), "b": (190, 110, "b 30%"),
             "n2": (310, 110, "20%"), "c": (270, 156, "c 10%"), "d": (350, 156, "d 10%")}
    edges = [("r", "a", "0"), ("r", "n1", "1"), ("n1", "b", "0"), ("n1", "n2", "1"), ("n2", "c", "0"), ("n2", "d", "1")]
    b = ""
    for p, c, bit in edges:
        x1, y1, _ = nodes[p]; x2, y2, _ = nodes[c]
        b += f'<line x1="{x1}" y1="{y1+8}" x2="{x2}" y2="{y2-10}" class="s-ax"/>'
        b += text((x1 + x2) / 2 + (-9 if bit == "0" else 6), (y1 + y2) / 2 + 2, bit, "t-s f-ou")
    for k, (x, y, s) in nodes.items():
        leaf = k in "abcd"
        b += f'<rect x="{x-24}" y="{y-10}" width="48" height="20" rx="10" class="{"f-sheet3" if leaf else "f-bg"}" stroke="var(--line)"/>'
        b += text(x, y + 4, s, "t-s f-ink" if leaf else "t-s f-ink3", "middle")
    b += text(16, 140, "a=0  b=10", "t-m f-ink2 mono")
    b += text(16, 158, "c=110  d=111", "t-m f-ink2 mono")
    b += text(16, 176, "平均 1.7ビット", "t-m f-ou")
    return svg(380, 180, b, "ハフマン木")

# ───────────────────────── 01-2 ─────────────────────────
def traversal():
    pos = {1: (180, 20), 2: (110, 72), 3: (250, 72), 4: (70, 124), 5: (150, 124), 6: (290, 124)}
    edges = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6)]
    b = ""
    for a, c in edges:
        b += f'<line x1="{pos[a][0]}" y1="{pos[a][1]}" x2="{pos[c][0]}" y2="{pos[c][1]}" class="s-ax"/>'
    for k, (x, y) in pos.items():
        b += f'<circle cx="{x}" cy="{y}" r="12" class="f-sheet3" stroke="var(--line)"/>' + text(x, y + 4, str(k), "t-m f-ink", "middle")
    rows = [("行きがけ 節→左→右", "1 2 4 5 3 6"), ("通りがけ 左→節→右", "4 2 5 1 3 6"), ("帰りがけ 左→右→節", "4 5 2 6 3 1"), ("幅優先（キュー）", "1 2 3 4 5 6")]
    for i, (n, s) in enumerate(rows):
        y = 160 + i * 17
        b += text(20, y, n, "t-s f-ink2") + text(340, y, s, "t-s f-ou mono", "end")
    return svg(360, 226, b, "2分木の走査")

# ───────────────────────── 02-1 ─────────────────────────
def pipeline():
    st = ["F", "D", "R", "E"]
    rows = ""
    for i in range(5):
        cells = "".join(
            f'<td class="{"on" if i <= j < i+4 else ""}">{st[j-i] if i <= j < i+4 else ""}</td>' for j in range(8))
        rows += f"<tr><th>命令{i+1}</th>{cells}</tr>"
    head = "<tr><th></th>" + "".join(f"<th>{j+1}</th>" for j in range(8)) + "</tr>"
    css = ('<style>.pp{border-collapse:separate;border-spacing:3px;font-family:var(--f-mono);font-size:11px;margin:0 auto}'
           '.pp th{color:var(--ink-3);font-weight:400;padding:0 4px}.pp td{width:26px;height:22px;text-align:center;border-radius:4px;color:var(--bg)}'
           '.pp td.on{background:var(--kihon)}.pp tr:nth-child(2) td.on{background:var(--ou)}</style>')
    return css + f'<table class="pp">{head}{rows}</table>'

def memhier():
    return ('<div class="stack">'
            '<div class="r"><b>レジスタ</b><span>CPUの中</span></div>'
            '<div class="r"><b>キャッシュ（SRAM）</b><span>L1→L2→L3</span></div>'
            '<div class="r"><b>主記憶（DRAM）</b><span>リフレッシュ要</span></div>'
            '<div class="r"><b>SSD（NANDフラッシュ）／HDD</b><span>補助記憶</span></div>'
            '</div><div class="cap" style="display:flex;justify-content:space-between"><span>↑ 速い・小さい・高い</span><span>遅い・大きい・安い ↓</span></div>')

# ───────────────────────── 02-2 ─────────────────────────
def availability():
    box = lambda s: f'<span style="display:inline-block;border:1px solid var(--line);border-radius:6px;padding:2px 8px;background:var(--sheet-3);font-family:var(--f-mono);font-size:12px">{s}</span>'
    line = '<span style="display:inline-block;width:14px;height:1.5px;background:var(--ink-3);vertical-align:middle"></span>'
    ser = f'<div style="display:flex;align-items:center;flex-wrap:wrap;gap:0">{line}{box("0.9")}{line}{box("0.8")}{line}<span style="margin-left:10px;font-family:var(--f-mono);font-size:12px">直列 ＝ 0.9×0.8 ＝ <b class="hl">0.72</b></span></div>'
    par = (f'<div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-top:10px">'
           f'<span style="display:inline-flex;flex-direction:column;gap:4px;border-left:1.5px solid var(--ink-3);border-right:1.5px solid var(--ink-3);padding:0 8px">{box("0.9")}{box("0.8")}</span>'
           f'<span style="font-family:var(--f-mono);font-size:12px">並列 ＝ 1−(1−0.9)(1−0.8) ＝ <b class="hl">0.98</b></span></div>')
    return ser + par

def raid():
    def disk(name, cells, hot=None):
        cs = "".join(f'<div style="height:20px;border-radius:4px;display:flex;align-items:center;justify-content:center;font-family:var(--f-mono);font-size:11px;'
                     f'background:{"var(--ou)" if c=="P" else "var(--sheet-3)"};color:{"var(--bg)" if c=="P" else "var(--ink)"}">{c}</div>' for c in cells)
        return f'<div style="display:flex;flex-direction:column;gap:3px;width:34px"><div style="font-size:10px;color:var(--ink-3);text-align:center">{name}</div>{cs}</div>'
    def grp(title, sub, disks):
        return (f'<div style="display:flex;flex-direction:column;gap:6px;min-width:0"><div style="font-size:12px;font-weight:700">{title}</div>'
                f'<div style="display:flex;gap:4px">{"".join(disks)}</div><div style="font-size:11px;color:var(--ink-3)">{sub}</div></div>')
    g0 = grp("RAID0", "ストライピング<br>速い・冗長なし", [disk("A", ["1", "3", "5"]), disk("B", ["2", "4", "6"])])
    g1 = grp("RAID1", "ミラーリング<br>容量1/2・1台壊れてもOK", [disk("A", ["1", "2", "3"]), disk("B", ["1", "2", "3"])])
    g5 = grp("RAID5", "パリティ分散<br>1台までOK・容量(n−1)台分", [disk("A", ["1", "3", "P"]), disk("B", ["2", "P", "5"]), disk("C", ["P", "4", "6"])])
    return f'<div style="display:flex;flex-wrap:wrap;gap:18px 26px">{g0}{g1}{g5}</div>'

def bathtub():
    X0, X1, Y0, Y1 = 30, 340, 140, 20
    pts = []
    for i in range(0, 301):
        t = i / 300
        v = 0.75 * math.exp(-t * 14) + 0.12 + 0.8 * max(0, t - 0.68) ** 2 * 9
        pts.append((X0 + (X1 - X0) * t, Y0 - (Y0 - Y1) * min(v, 1)))
    b = f'<line x1="{X0}" y1="{Y0}" x2="{X1}" y2="{Y0}" class="s-ax"/><line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1-4}" class="s-ax"/>'
    b += f'<path d="{path(pts)}" class="s-main"/>'
    for t in (0.22, 0.7):
        x = X0 + (X1 - X0) * t
        b += f'<line x1="{x:.1f}" y1="{Y1}" x2="{x:.1f}" y2="{Y0}" class="s-dash"/>'
    for t, s1, s2 in ((0.11, "初期故障", "↓下がる"), (0.46, "偶発故障", "→一定"), (0.85, "摩耗故障", "↑上がる")):
        x = X0 + (X1 - X0) * t
        b += text(x, Y0 + 15, s1, "t-s f-ink2", "middle") + text(x, Y0 + 28, s2, "t-s f-ink3", "middle")
    b += text(X0 + 4, Y1 - 6, "故障率", "t-s f-ink3")
    b += text(40, 48, "エージング・", "t-s f-ou hand") + text(40, 62, "バーンインで潰す", "t-s f-ou hand")
    b += text(262, 60, "予防保守で先に交換", "t-s f-ou hand")
    return svg(360, 176, b, "バスタブ曲線")

def virt():
    def col(title, layers, note):
        ls = "".join(f'<div style="background:{"var(--ou-bg)" if hi else "var(--sheet-3)"};border-radius:4px;padding:3px 6px;font-size:11px;text-align:center;{"color:var(--ou-2);font-weight:700" if hi else ""}">{s}</div>' for s, hi in layers)
        return f'<div style="flex:1 1 100px;min-width:96px;display:flex;flex-direction:column;gap:3px"><div style="font-size:12px;font-weight:700;text-align:center">{title}</div>{ls}<div style="font-size:11px;color:var(--ink-3);text-align:center">{note}</div></div>'
    a = col("ホスト型", [("アプリ", 0), ("ゲストOS", 0), ("仮想化ソフト", 1), ("ホストOS", 0), ("HW", 0)], "作りやすい・遅い")
    b = col("ハイパバイザ型", [("アプリ", 0), ("ゲストOS", 0), ("ハイパバイザ", 1), ("HW", 0)], "ホストOSなし・速い")
    c = col("コンテナ型", [("アプリ", 0), ("コンテナ", 1), ("コンテナエンジン", 0), ("ホストOS", 0), ("HW", 0)], "ゲストOSなし・軽い")
    return f'<div style="display:flex;gap:10px;flex-wrap:wrap">{a}{b}{c}</div>'

# ───────────────────────── 02-3 ─────────────────────────
def taskstate():
    R, U, W = (70, 90), (290, 40), (290, 150)
    b = arrow_defs("ts")
    def node(p, s, sub):
        return (f'<rect x="{p[0]-46}" y="{p[1]-17}" width="92" height="34" rx="17" class="f-sheet3" stroke="var(--line)"/>'
                + text(p[0], p[1] - 1, s, "t-m f-ink", "middle") + text(p[0], p[1] + 12, sub, "t-s f-ink3", "middle"))
    b += f'<path d="M{R[0]+30},{R[1]-17} Q170,10 {U[0]-46},{U[1]-6}" class="s-main" marker-end="url(#tso)"/>'
    b += text(165, 22, "ディスパッチ", "t-s f-ou", "middle")
    b += f'<path d="M{U[0]-46},{U[1]+8} Q175,62 {R[0]+46},{R[1]-4}" class="s-ax" marker-end="url(#ts)"/>'
    b += text(176, 74, "プリエンプション", "t-s f-ink2", "middle")
    b += f'<line x1="{U[0]}" y1="{U[1]+17}" x2="{W[0]}" y2="{W[1]-19}" class="s-ax" marker-end="url(#ts)"/>'
    b += text(U[0] + 8, 98, "入出力要求", "t-s f-ink2") + text(U[0] + 8, 111, "(SVC割込み)", "t-s f-ink3")
    b += f'<path d="M{W[0]-46},{W[1]} Q150,160 {R[0]+10},{R[1]+19}" class="s-ax" marker-end="url(#ts)"/>'
    b += text(160, 166, "入出力完了（入出力割込み）", "t-s f-ink2", "middle")
    b += node(R, "実行可能", "Ready") + node(U, "実行", "Run") + node(W, "待ち", "Wait")
    b += text(250, 196, "待ち → 実行 は直接いけない", "t-s f-warn hand", "middle")
    return svg(360, 204, b, "タスクの状態遷移")

# ───────────────────────── 03-2 ─────────────────────────
def recovery():
    X0, X1 = 70, 330
    CP, FL = 150, 300
    b = f'<line x1="{X0-10}" y1="150" x2="{X1}" y2="150" class="s-ax"/>'
    b += f'<line x1="{CP}" y1="12" x2="{CP}" y2="150" class="s-dash"/>' + text(CP, 164, "チェックポイント", "t-s f-ink2", "middle")
    b += f'<line x1="{FL}" y1="12" x2="{FL}" y2="150" class="s-warn"/>' + text(FL, 164, "障害 ✖", "t-s f-warn", "middle")
    rows = [("T1", 80, 130, True, "何もしない", "f-ink3"), ("T2", 110, 220, True, "ロールフォワード", "f-ou"),
            ("T3", 170, 260, True, "ロールフォワード", "f-ou"), ("T4", 100, FL, False, "ロールバック", "f-k"), ("T5", 200, FL, False, "ロールバック", "f-k")]
    for i, (n, s, e, cm, act, cls) in enumerate(rows):
        y = 26 + i * 25
        b += text(X0 - 26, y + 4, n, "t-s f-ink2")
        b += f'<line x1="{s}" y1="{y}" x2="{e}" y2="{y}" class="{"s-main" if cls=="f-ou" else "s-2"}" stroke-linecap="round"/>'
        if cm:
            b += f'<circle cx="{e}" cy="{y}" r="3.5" class="f-ink"/>' + text(e, y - 6, "commit", "t-s f-ink3", "middle")
        b += text(X1 + 2, y + 4, act, f"t-s {cls}", "start")
    return svg(420, 172, b, "障害回復のタイムライン")

# ───────────────────────── 03-3 ─────────────────────────
def osi():
    rows = [("7 アプリケーション", "HTTP SMTP DNS DHCP", "ゲートウェイ", 0), ("6 プレゼンテーション", "文字コード・圧縮", "↑", 0),
            ("5 セッション", "会話の管理", "↑", 0), ("4 トランスポート", "TCP / UDP（ポート番号）", "↑", 0),
            ("3 ネットワーク", "IP（IPアドレス）・ルーティング", "ルータ・L3SW", 1), ("2 データリンク", "MACアドレス・イーサネット", "ブリッジ・L2SW", 1),
            ("1 物理", "ケーブル・電気信号", "リピータ・ハブ", 1)]
    h = '<div class="stack">'
    for a, b_, c, hi in rows:
        h += f'<div class="r"><b>{a} <small style="font-weight:400;color:var(--ink-3)">{b_}</small></b><span style="color:{"var(--ou-2)" if hi or c=="ゲートウェイ" else "var(--ink-3)"}">{c}</span></div>'
    return h + '</div>'

def handshake():
    C, S = 70, 290
    b = arrow_defs("hs")
    b += f'<line x1="{C}" y1="22" x2="{C}" y2="178" class="s-dash"/><line x1="{S}" y1="22" x2="{S}" y2="178" class="s-dash"/>'
    b += text(C, 14, "クライアント", "t-m f-ink", "middle") + text(S, 14, "サーバ", "t-m f-ink", "middle")
    msgs = [(C, S, 40, 70, "① SYN", "seq=100"), (S, C, 84, 114, "② SYN/ACK", "seq=200, ack=101"), (C, S, 128, 158, "③ ACK", "seq=101, ack=201")]
    for x1, x2, y1, y2, a, s in msgs:
        b += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="s-main" marker-end="url(#hso)"/>'
        b += text((x1 + x2) / 2, (y1 + y2) / 2 - 6, a, "t-m f-ou", "middle")
        b += text((x1 + x2) / 2, (y1 + y2) / 2 + 14, s, "t-s f-ink3 mono", "middle")
    return svg(360, 186, b, "3ウェイハンドシェイク")

# ───────────────────────── 03-4 ─────────────────────────
def subnet():
    bits = "11000000.10101000.00000001.10|000010"
    net, host = "11000000 10101000 00000001 10", "000010"
    cell = lambda c, on: f'<span style="display:inline-block;width:11px;text-align:center;font-family:var(--f-mono);font-size:11px;border-radius:2px;{"background:var(--ou-bg);color:var(--ou-2)" if on else "background:var(--sheet-3);color:var(--ink-2)"}">{c}</span>'
    n = "".join(cell(c, 1) if c != " " else '<span style="display:inline-block;width:5px"></span>' for c in net)
    hh = "".join(cell(c, 0) for c in host)
    return (f'<div style="white-space:nowrap;overflow-x:auto">{n}<span style="display:inline-block;width:6px"></span>{hh}</div>'
            '<div style="display:flex;justify-content:space-between;font-size:11px;color:var(--ink-3);margin-top:4px"><span style="color:var(--ou-2)">ネットワーク部 26ビット（/26）</span><span>ホスト部 6ビット</span></div>'
            '<div style="font-family:var(--f-mono);font-size:12px;margin-top:8px;line-height:1.7">192.168.1.130/26<br>NW ＝ AND → 192.168.1.<b class="hl">128</b>　BC ＝ ホスト全部1 → .<b class="hl">191</b><br>ホスト数 ＝ 2⁶−2 ＝ <b class="hl">62</b>（.129〜.190）</div>')

# ───────────────────────── 03-5 ─────────────────────────
def keys():
    def lane(title, steps, color):
        s = ""
        for i, (who, act, key) in enumerate(steps):
            if i:
                s += '<div style="color:var(--ink-3);padding:0 4px;display:flex;align-items:center">→</div>'
            s += (f'<div style="flex:1 1 120px;min-width:110px;background:var(--sheet-3);border-radius:8px;padding:6px 8px">'
                  f'<div style="font-size:11px;color:var(--ink-3)">{who}</div><div style="font-size:12.5px;font-weight:700">{act}</div>'
                  f'<div style="font-size:12px;color:{color};font-weight:700">{key}</div></div>')
        return f'<div style="font-family:var(--f-hand);font-size:13px;margin:4px 0">{title}</div><div style="display:flex;flex-wrap:wrap;gap:4px 0">{s}</div>'
    a = lane("暗号化（盗聴対策）", [("送信者", "暗号化", "受信者の公開鍵"), ("受信者", "復号", "受信者の秘密鍵")], "var(--link)")
    b = lane("デジタル署名（改ざん・なりすまし・否認対策）", [("送信者", "ハッシュ値を署名", "送信者の秘密鍵"), ("受信者", "署名を検証", "送信者の公開鍵")], "var(--ou-2)")
    c = lane("証明書の検証", [("認証局", "証明書に署名", "CAの秘密鍵"), ("利用者", "証明書を検証", "CAの公開鍵")], "var(--ou-2)")
    return a + '<div style="height:8px"></div>' + b + '<div style="height:8px"></div>' + c

def dmz():
    b = arrow_defs("dz")
    def bx(x, y, w, s, sub="", cls="f-sheet3"):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="36" rx="8" class="{cls}" stroke="var(--line)"/>' + text(x + w / 2, y + 15, s, "t-s f-ink", "middle")
                + (text(x + w / 2, y + 29, sub, "t-s f-ink3", "middle") if sub else ""))
    b += bx(4, 70, 96, "インターネット")
    b += bx(122, 70, 44, "FW", "", "f-oubg")
    b += '<line x1="100" y1="88" x2="122" y2="88" class="s-ax"/>'
    b += '<path d="M166,80 L190,40" class="s-ax"/><path d="M166,96 L190,136" class="s-ax"/>'
    b += bx(190, 18, 166, "DMZ", "Webサーバ・メールサーバ")
    b += bx(190, 118, 166, "内部ネットワーク", "DBサーバ・社員PC")
    b += text(273, 74, "公開サーバはここ", "t-s f-ou hand", "middle")
    b += text(273, 106, "外から直接は入れない", "t-s f-ink3 hand", "middle")
    return svg(360, 160, b, "DMZの構成")

# ───────────────────────── 04-1 ─────────────────────────
def vmodel():
    L = ["業務要件定義", "システム要件定義", "システム方式設計", "ソフトウェア要件定義", "ソフトウェア方式設計", "ソフトウェア詳細設計"]
    R = ["運用テスト", "システム適格性確認テスト", "システム結合テスト", "ソフトウェア適格性確認テスト", "ソフトウェア結合テスト", "単体テスト"]
    rows = ""
    for i in range(6):
        pad = i * 4
        col = "var(--ink-3)" if i == 0 else "var(--ou-2)"
        rows += (f'<div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(14px,{40-pad*2}px) minmax(0,1fr);align-items:center;gap:6px;padding:0 {pad}%;font-size:12px">'
                 f'<span style="text-align:right;color:var(--ink-2)">{L[i]}</span>'
                 f'<span style="border-top:1.5px dashed var(--line);height:0"></span>'
                 f'<span style="color:{col}">{R[i]}</span></div>')
    rows += '<div style="text-align:center;font-size:12px;color:var(--ink);font-weight:700;margin-top:4px">＼ プログラミング ／</div>'
    head = ('<div style="display:grid;grid-template-columns:1fr 1fr;font-size:11px;color:var(--ink-3);margin-bottom:4px">'
            '<span style="text-align:right;padding-right:26px">決める（作り込み）↓</span><span style="padding-left:26px">↑ 確かめる（検証）</span></div>')
    return head + f'<div style="display:flex;flex-direction:column;gap:5px">{rows}</div>'

# ───────────────────────── 05-1 ─────────────────────────
def cpm():
    N = {1: (28, 105), 2: (130, 38), 3: (130, 172), 4: (250, 38), 5: (250, 172), 6: (338, 105)}
    T = {1: "0/0", 2: "1/2", 3: "5/5", 4: "9/10", 5: "9/9", 6: "14/14"}
    E = [(1, 2, "A1", 0, 0), (1, 3, "B5", 1, 0), (2, 3, "C3", 0, 0), (2, 4, "D3", 0, 0), (3, 5, "E4", 1, 0), (5, 4, "F", 0, 1), (4, 6, "H4", 0, 0), (5, 6, "G5", 1, 0)]
    b = arrow_defs("cp")
    r = 14
    for a, c, lab, crit, dummy in E:
        (x1, y1), (x2, y2) = N[a], N[c]
        d = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / d, (y2 - y1) / d
        sx, sy, ex, ey = x1 + ux * r, y1 + uy * r, x2 - ux * (r + 2), y2 - uy * (r + 2)
        cls = "s-main" if crit else ("s-dash" if dummy else "s-ax")
        mk = "cpo" if crit else "cp"
        b += f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" class="{cls}" marker-end="url(#{mk})"/>'
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if abs(ux) < 0.2:
            b += text(mx + (8 if dummy else -8), my + 4, lab + ("（ダミー）" if dummy else ""), "t-s " + ("f-ou" if crit else "f-ink2"), "start" if dummy else "end")
        else:
            b += text(mx, my - 6, lab, "t-s " + ("f-ou" if crit else "f-ink2"), "middle")
    for k, (x, y) in N.items():
        crit = k in (1, 3, 5, 6)
        b += f'<circle cx="{x}" cy="{y}" r="{r}" class="f-sheet3" stroke="{"var(--ou)" if crit else "var(--line)"}" stroke-width="1.5"/>'
        b += text(x, y + 4, str(k), "t-m f-ink", "middle")
        b += text(x, y + (30 if y > 100 else -20), T[k], "t-s f-ink3 mono", "middle")
    b += text(190, 224, "最早/最遅が一致する点を結ぶ＝クリティカルパス", "t-s f-ou hand", "middle")
    return svg(366, 232, b, "アローダイアグラムとクリティカルパス")

def evm():
    X0, X1, Y0, Y1 = 40, 330, 170, 16
    fx = lambda t: X0 + (X1 - X0) * t
    fy = lambda v: Y0 - (Y0 - Y1) * v / 100
    b = f'<line x1="{X0}" y1="{Y0}" x2="{X1+8}" y2="{Y0}" class="s-ax"/><line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1-6}" class="s-ax"/>'
    b += f'<line x1="{X0}" y1="{fy(100):.1f}" x2="{X1}" y2="{fy(100):.1f}" class="s-grid"/>' + text(X0 - 4, fy(100) + 4, "BAC", "t-s f-ink3", "end")
    b += f'<line x1="{fx(0)}" y1="{fy(0)}" x2="{fx(1)}" y2="{fy(100):.1f}" class="s-2"/>' + text(fx(1) - 4, fy(100) - 6, "PV（計画）", "t-s f-k", "end")
    b += f'<line x1="{fx(0)}" y1="{fy(0)}" x2="{fx(.5)}" y2="{fy(60):.1f}" class="s-warn"/>'
    b += f'<line x1="{fx(0)}" y1="{fy(0)}" x2="{fx(.5)}" y2="{fy(40):.1f}" class="s-main"/>'
    b += f'<line x1="{fx(.5)}" y1="{Y1}" x2="{fx(.5)}" y2="{Y0}" class="s-dash"/>' + text(fx(.5), Y0 + 14, "いま", "t-s f-ink2", "middle")
    for v, s, cls in ((60, "AC 60（実際に払った）", "f-warn"), (50, "PV 50", "f-k"), (40, "EV 40（できた分）", "f-ou")):
        b += f'<circle cx="{fx(.5):.1f}" cy="{fy(v):.1f}" r="3.5" class="{cls}"/>' + text(fx(.5) + 8, fy(v) + 4, s, f"t-s {cls}")
    b += text(fx(.5) - 8, fy(70) + 4, "SV＝EV−PV＝−10 遅れ", "t-s f-ink2", "end")
    b += text(fx(.5) - 8, fy(82) + 4, "CV＝EV−AC＝−20 超過", "t-s f-ink2", "end")
    return svg(360, 186, b, "EVM")

# ───────────────────────── 06-1 ─────────────────────────
def plc():
    X0, X1, Y0, Y1 = 20, 340, 120, 14
    b = f'<line x1="{X0}" y1="{Y0}" x2="{X1}" y2="{Y0}" class="s-ax"/>'
    sales = [(X0 + (X1 - X0) * t, Y0 - (Y0 - Y1) * (math.exp(-((t - 0.62) / 0.24) ** 2))) for t in [i / 200 for i in range(201)]]
    prof = [(X0 + (X1 - X0) * t, Y0 - (Y0 - Y1) * (0.75 * math.exp(-((t - 0.58) / 0.2) ** 2) - 0.12)) for t in [i / 200 for i in range(201)]]
    b += f'<path d="{path(sales)}" class="s-main"/><path d="{path(prof)}" class="s-2"/>'
    b += text(X0 + (X1 - X0) * .62, Y1 - 2, "売上", "t-s f-ou", "middle") + text(X0 + (X1 - X0) * .44, Y1 + 40, "利益", "t-s f-k", "middle")
    seps = [0.25, 0.5, 0.78]
    for t in seps:
        x = X0 + (X1 - X0) * t
        b += f'<line x1="{x:.1f}" y1="{Y1}" x2="{x:.1f}" y2="{Y0+40}" class="s-dash"/>'
    labs = [(0.125, "導入期", "問題児"), (0.375, "成長期", "花形"), (0.64, "成熟期", "金のなる木"), (0.89, "衰退期", "負け犬")]
    for t, a, p in labs:
        x = X0 + (X1 - X0) * t
        b += text(x, Y0 + 16, a, "t-s f-ink", "middle") + text(x, Y0 + 31, p, "t-s f-ink3", "middle")
    return svg(360, 160, b, "プロダクトライフサイクル")

# ───────────────────────── 06-2 ─────────────────────────
def eoq():
    X0, X1, Y0, Y1 = 44, 340, 160, 14
    qmax, ymax = 600, 3000
    fx = lambda q: X0 + (X1 - X0) * q / qmax
    fy = lambda v: Y0 - (Y0 - Y1) * min(v, ymax) / ymax
    order = [(fx(q), fy(120000 / q)) for q in range(40, 601, 4)]
    hold = [(fx(q), fy(3 * q)) for q in range(0, 601, 10)]
    tot = [(fx(q), fy(120000 / q + 3 * q)) for q in range(60, 601, 4)]
    b = f'<line x1="{X0}" y1="{Y0}" x2="{X1+6}" y2="{Y0}" class="s-ax"/><line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1-4}" class="s-ax"/>'
    b += f'<path d="{path(order)}" class="s-2"/><path d="{path(hold)}" class="s-3"/><path d="{path(tot)}" class="s-main"/>'
    b += f'<line x1="{fx(200):.1f}" y1="{fy(1200):.1f}" x2="{fx(200):.1f}" y2="{Y0}" class="s-dash"/><circle cx="{fx(200):.1f}" cy="{fy(1200):.1f}" r="3.5" class="f-ou"/>'
    b += f'<circle cx="{fx(200):.1f}" cy="{fy(600):.1f}" r="3" class="f-ink"/>'
    b += text(fx(200), Y0 + 14, "EOQ", "t-s f-ou", "middle")
    b += text(fx(560), fy(1950), "総費用", "t-s f-ou", "end") + text(fx(560), fy(1500), "保管費用", "t-s f-link", "end") + text(fx(70), fy(2700), "発注費用", "t-s f-k")
    b += text(fx(215), fy(600) + 16, "発注費＝保管費のとき最小", "t-s f-ink2 hand")
    b += text(X1, Y0 + 14, "1回の発注量", "t-s f-ink3", "end")
    return svg(360, 180, b, "経済的発注量")

def oc():
    X0, X1, Y0, Y1 = 40, 340, 150, 16
    n, c = 50, 2
    def L(p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(c + 1))
    pmax = 0.16
    fx = lambda p: X0 + (X1 - X0) * p / pmax
    fy = lambda v: Y0 - (Y0 - Y1) * v
    pts = [(fx(p), fy(L(p))) for p in [i / 1000 for i in range(0, 161)]]
    p1, p2 = 0.02, 0.10
    L1, L2 = L(p1), L(p2)
    b = f'<line x1="{X0}" y1="{Y0}" x2="{X1+6}" y2="{Y0}" class="s-ax"/><line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1-4}" class="s-ax"/>'
    b += f'<line x1="{X0}" y1="{fy(1):.1f}" x2="{X1}" y2="{fy(1):.1f}" class="s-grid"/>' + text(X0 - 4, fy(1) + 4, "1.0", "t-s f-ink3", "end")
    b += f'<path d="{path(pts)}" class="s-main"/>'
    for p, Lv in ((p1, L1), (p2, L2)):
        b += f'<line x1="{fx(p):.1f}" y1="{fy(Lv):.1f}" x2="{fx(p):.1f}" y2="{Y0}" class="s-dash"/><line x1="{X0}" y1="{fy(Lv):.1f}" x2="{fx(p):.1f}" y2="{fy(Lv):.1f}" class="s-dash"/>'
    b += f'<line x1="{fx(p1)+6:.1f}" y1="{fy(1):.1f}" x2="{fx(p1)+6:.1f}" y2="{fy(L1):.1f}" class="s-warn"/>'
    b += text(fx(p1) + 12, fy((1 + L1) / 2) + 4, "生産者危険 α（良品ロットが不合格）", "t-s f-warn")
    b += f'<line x1="{fx(p2)+6:.1f}" y1="{fy(L2):.1f}" x2="{fx(p2)+6:.1f}" y2="{Y0}" class="s-3"/>'
    b += text(fx(p2) + 12, fy(L2 / 2) - 8, "消費者危険 β", "t-s f-link") + text(fx(p2) + 12, fy(L2 / 2) + 6, "（不良ロットが合格）", "t-s f-link")
    b += text(fx(p1), Y0 + 14, "p1(AQL)", "t-s f-ink2", "middle") + text(fx(p2), Y0 + 14, "p2", "t-s f-ink2", "middle")
    b += text(X1, Y0 + 14, "ロットの不良率", "t-s f-ink3", "end") + text(X0 + 4, Y1 - 4, "合格率", "t-s f-ink3")
    return svg(360, 170, b, "OC曲線")

def breakeven():
    X0, X1, Y0, Y1 = 46, 330, 160, 14
    smax = 1000
    fx = lambda s: X0 + (X1 - X0) * s / smax
    fy = lambda v: Y0 - (Y0 - Y1) * v / smax
    b = f'<line x1="{X0}" y1="{Y0}" x2="{X1+6}" y2="{Y0}" class="s-ax"/><line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1-4}" class="s-ax"/>'
    b += f'<line x1="{fx(0)}" y1="{fy(500):.1f}" x2="{fx(1000):.1f}" y2="{fy(500):.1f}" class="s-dash"/>' + text(fx(990), fy(500) - 4, "固定費 500", "t-s f-ink3", "end")
    b += f'<line x1="{fx(0)}" y1="{fy(0)}" x2="{fx(1000):.1f}" y2="{fy(1000):.1f}" class="s-main"/>' + text(fx(905), fy(1000) + 2, "売上高", "t-s f-ou", "end")
    b += f'<line x1="{fx(0)}" y1="{fy(500):.1f}" x2="{fx(1000):.1f}" y2="{fy(700):.1f}" class="s-2"/>' + text(fx(1000), fy(700) + 16, "総費用＝500＋0.2×売上", "t-s f-k", "end")
    b += f'<circle cx="{fx(625):.1f}" cy="{fy(625):.1f}" r="4" class="f-ou"/><line x1="{fx(625):.1f}" y1="{fy(625):.1f}" x2="{fx(625):.1f}" y2="{Y0}" class="s-dash"/>'
    b += text(fx(625), Y0 + 14, "625", "t-s f-ou mono", "middle")
    b += text(fx(625) - 8, fy(625) - 8, "損益分岐点", "t-s f-ou hand", "end")
    b += text(fx(250), fy(430), "損失", "t-s f-warn", "middle") + text(fx(880), fy(770), "利益", "t-s f-ou", "middle")
    return svg(360, 178, b, "損益分岐点")

# ───────────────────────── 06-3 ─────────────────────────
def contracts():
    b = arrow_defs("ct")
    def bx(x, y, s, cls="f-sheet3"):
        return f'<rect x="{x-34}" y="{y-13}" width="68" height="26" rx="7" class="{cls}" stroke="var(--line)"/>' + text(x, y + 4, s, "t-s f-ink", "middle")
    def panel(ox, t1, t2, title, cmd_from_client):
        s = text(ox + 85, 14, title, "t-m f-ink hand", "middle")
        A, B, W = (ox + 40, 46), (ox + 130, 46), (ox + 85, 130)
        s += f'<line x1="{A[0]+34}" y1="{A[1]}" x2="{B[0]-34}" y2="{B[1]}" class="s-ax"/>' + text(ox + 85, 40, "契約", "t-s f-ink3", "middle")
        s += f'<line x1="{A[0]}" y1="{A[1]+13}" x2="{W[0]-14}" y2="{W[1]-13}" class="s-ax" marker-end="url(#ct)"/>'
        lab = "雇用" if cmd_from_client else "雇用＋指揮命令"
        s += text(A[0] - 6, 96, lab, "t-s f-ink2", "middle")
        if cmd_from_client:
            s += f'<line x1="{B[0]}" y1="{B[1]+13}" x2="{W[0]+14}" y2="{W[1]-13}" class="s-main" marker-end="url(#cto)"/>' + text(B[0] + 8, 96, "指揮命令", "t-s f-ou", "middle")
        else:
            s += f'<line x1="{B[0]}" y1="{B[1]+13}" x2="{W[0]+14}" y2="{W[1]-13}" class="s-dash"/>' + text(B[0] + 10, 96, "✕指示NG", "t-s f-warn", "middle")
        s += bx(A[0], A[1], t1) + bx(B[0], B[1], t2, "f-oubg" if cmd_from_client else "f-sheet3") + bx(W[0], W[1], "労働者")
        return s
    b += panel(0, "派遣元", "派遣先", "労働者派遣", True)
    b += panel(180, "請負元", "発注者", "請負", False)
    return svg(360, 150, b, "派遣と請負の指揮命令")

