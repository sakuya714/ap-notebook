# -*- coding: utf-8 -*-
"""ビルド前のチェック（全ノート共通）。エラーが1つでもあればビルドを止める。

1. 書き間違い：知らない @記法・@xxx と @end の数の食い違い・存在しない章へのリンク・note.json の不備
2. 公開してはいけない情報：メール・電話・学籍番号・APIキー・Mac のパス・.private-words に書いた言葉
   （このサイトは GitHub で公開する。.private-words は公開しない＝.gitignore 済み）
"""
import os, re, json, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLOCKS = {"map", "stack", "mx", "lad", "html", "flows", "box", "fold", "quiz", "ox", "check", "steps", "stats", "routes", "cover"}
SINGLE = {"part", "ch", "board", "pair", "toc", "formulas", "pairs", "legend", "fig", "fig!", "flow", "end"}
BOX_TONES = {"why", "exam", "warn", "goal"}
NOTE_KEYS = {"title", "type", "labels", "macros"}
TYPES = ("整理型", "理解型")

SECRET_PATTERNS = [
    (r"[\w.+-]+@[\w-]+\.[\w.-]+", "メールアドレス"),
    (r"(?<!\d)0\d{1,4}-\d{1,4}-\d{3,4}(?!\d)", "電話番号"),
    (r"(?<!\d)\d{2}-\d-\d{3}-\d{4}(?!\d)", "学籍番号の形"),
    (r"\b(sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_\w{20,}|AKIA[0-9A-Z]{16}|xox[bpa]-[\w-]{10,})", "APIキー・トークン"),
    (r"/Users/[^\s\"']+", "Mac のファイルの場所"),
]

def private_words():
    p = os.path.join(ROOT, ".private-words")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        return [w.strip() for w in fh if w.strip() and not w.startswith("#")]

def scan_privacy(errors):
    words = private_words()
    targets = []
    for base in ("notes", "theme", "engine"):
        for f in glob.glob(os.path.join(ROOT, base, "**", "*"), recursive=True):
            if os.path.isfile(f) and f.endswith((".txt", ".json", ".py", ".js", ".css", ".html", ".md")) and "/vendor/" not in f:
                targets.append(f)
    targets += [os.path.join(ROOT, f) for f in ("hub.py", "README.md")]
    for f in targets:
        if f.endswith("engine/check.py"):
            continue  # 検出用のパターンそのものが書いてあるため
        with open(f, encoding="utf-8", errors="ignore") as fh:
            for i, line in enumerate(fh, 1):
                for pat, what in SECRET_PATTERNS:
                    m = re.search(pat, line)
                    if m:
                        errors.append(f"{rel(f)}:{i}: 公開NG？（{what}）: {m.group(0)[:40]}")
                for w in words:
                    if w in line:
                        errors.append(f"{rel(f)}:{i}: 公開NG（.private-words の言葉）: {w}")

def rel(f):
    return os.path.relpath(f, ROOT)

def check_note(note_dir, errors, warns):
    name = rel(note_dir)
    try:
        with open(os.path.join(note_dir, "note.json"), encoding="utf-8") as fh:
            cfg = json.load(fh)
    except Exception as e:
        errors.append(f"{name}/note.json: 読めない（{e}）"); return
    if not cfg.get("title"):
        errors.append(f"{name}/note.json: title がない")
    if cfg.get("type") not in TYPES:
        errors.append(f"{name}/note.json: type は 整理型 か 理解型")
    for k in set(cfg) - NOTE_KEYS:
        warns.append(f"{name}/note.json: 知らない項目 \"{k}\"（使える項目：{', '.join(sorted(NOTE_KEYS))}）")
    files = sorted(glob.glob(os.path.join(note_dir, "content", "*.txt")))
    if not files:
        errors.append(f"{name}: content/*.txt がない"); return
    lines = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            lines += [(rel(f), i, l.rstrip("\n")) for i, l in enumerate(fh, 1)]
    chapters, figs = set(), set()
    for f, i, l in lines:
        m = re.match(r"@ch\s+([^|]+)\|", l.strip())
        if m:
            cid = m.group(1).strip()
            if cid in chapters:
                errors.append(f"{f}:{i}: 章の番号 {cid} が2回ある")
            chapters.add(cid)
    if os.path.exists(os.path.join(note_dir, "figs.py")):
        with open(os.path.join(note_dir, "figs.py"), encoding="utf-8") as fh:
            figs = set(re.findall(r"^def ([A-Za-z]\w*)\(", fh.read(), re.M))
    depth, opened, in_code, in_html = 0, [], False, False
    for f, i, l in lines:
        s = l.strip()
        if s.startswith("```"):
            in_code = not in_code; continue
        if in_code:
            continue
        if in_html and s != "@end":
            continue
        m = re.match(r"@(\w+!?)", s)
        if m:
            tag = m.group(1)
            if tag in BLOCKS:
                depth += 1; opened.append((f, i, tag)); in_html = tag == "html"
                if tag == "box":
                    tone = s[4:].strip().split(" ")[0] if s[4:].strip() else ""
                    if tone not in BOX_TONES:
                        errors.append(f"{f}:{i}: @box の種類は {' / '.join(sorted(BOX_TONES))}（「{tone}」になっている）")
            elif tag == "end":
                if depth == 0:
                    errors.append(f"{f}:{i}: 対応する @xxx がない @end")
                else:
                    depth -= 1; opened.pop(); in_html = False
            elif tag not in SINGLE:
                errors.append(f"{f}:{i}: 知らない記法 @{tag}（書き間違い？ 一覧は README）")
            if tag in ("fig", "fig!"):
                fname = s.split(None, 1)[1].split("|")[0].strip() if len(s.split(None, 1)) > 1 else ""
                if fname not in figs:
                    errors.append(f"{f}:{i}: @fig {fname} が figs.py にない")
            if tag == "pair":
                cid = (s[6:].split("|") + [""] * 5)[4].strip()
                if cid and cid not in chapters:
                    errors.append(f"{f}:{i}: @pair の章 {cid} がない")
        for cid in re.findall(r"\{\{([\w.-]+)\}\}", s):
            if cid not in chapters:
                errors.append(f"{f}:{i}: {{{{{cid}}}}} の章がない")
        if opened and opened[-1][2] == "routes" and not s.startswith("@"):
            for st in (s.split("|") + ["", "", ""])[2].split(","):
                cid = st.strip().split(" ")[0]
                if cid and cid not in chapters:
                    errors.append(f"{f}:{i}: 路線図の駅 {cid} の章がない")
        body = re.sub(r"\\\$", "", s)
        if s.count("**") % 2:
            warns.append(f"{f}:{i}: ** の数が奇数（太字の閉じ忘れ？）")
        if not s.startswith("$$") and body.count("$") % 2:
            warns.append(f"{f}:{i}: $ の数が奇数（数式の閉じ忘れ？）")
    for f, i, tag in opened:
        errors.append(f"{f}:{i}: @{tag} が @end で閉じられていない")

def run(note_dirs):
    errors, warns = [], []
    for d in note_dirs:
        check_note(d, errors, warns)
    scan_privacy(errors)
    for w in warns:
        print("  注意:", w)
    for e in errors:
        print("  エラー:", e)
    return errors, warns
