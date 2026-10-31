# -*- coding: utf-8 -*-
"""Notebook Hub：notes/ のノートを、全ノート共通の見た目（theme/）で1つのサイト（docs/）にする。

  python3 hub.py build                     notes/ → docs/ を作り直す（docs/index.html を開けば見られる）
  python3 hub.py new  university/統計-期末 整理型   ノートのひな形を作る（型は 整理型 か 理解型）
  python3 hub.py mkdir university/2年後期    フォルダを作る
  python3 hub.py check                     書き間違い・公開してはいけない情報がないか調べる（build でも毎回やる）
  python3 hub.py serve                     作り直して http://127.0.0.1:8765 で開く
"""
import sys, os, json, re, http.server
sys.dont_write_bytecode = True  # ノートの figs.py を読み込むときに __pycache__ を作らない

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import builder  # noqa: E402  engine/builder.py

SAMPLE = """@cover
eyebrow: 科目名 ／ 範囲
lead: このノートで何ができるようになるかを1〜2文で。
@end

@part p1 | パート名 | ひとこと | 短い名前
@ch 01 | 章タイトル | この章を1行で
@map
flow: 入口::最初に知ること > 中身::核になる考え > +出口::大事なところ
この章で取る点を1行で。
@end
## 見出し
( グループ
- 用語 — ふつうの説明（グレー）
+* 用語 — 大事なところ（金）・★よく出る
)
"""

def safe_rel(rel):
    parts = [p for p in rel.strip("/").split("/") if p]
    if not parts or any(p in (".", "..") or p.startswith((".", "_")) or re.search(r'[\\:*?"<>|]', p) for p in parts):
        raise SystemExit("パスが不正です: " + rel)
    return os.path.join(builder.NOTES, *parts)

def new_note(rel, kind):
    if kind not in builder.TYPES:
        raise SystemExit("型を 整理型 か 理解型 で指定してください（例：python3 hub.py new university/統計-期末 理解型）")
    d = safe_rel(rel)
    if os.path.exists(d):
        raise SystemExit("もうあります: " + rel)
    os.makedirs(os.path.join(d, "content"))
    with open(os.path.join(d, "note.json"), "w", encoding="utf-8") as fh:
        json.dump({"title": os.path.basename(d), "type": kind}, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(d, "content", "c1.txt"), "w", encoding="utf-8") as fh:
        fh.write(SAMPLE)
    return d

def new_folder(rel):
    d = safe_rel(rel)
    os.makedirs(d)
    open(os.path.join(d, ".keep"), "w").close()  # 空フォルダも git に残す
    return d

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=builder.DOCS, **kw)
    def log_message(self, *a):
        pass

def serve(port=8765):
    builder.build()
    # 複数のファイルを同時に配れるようにする（1本ずつだと MathJax などの読み込み中に固まる）
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler) as s:
        print(f"http://127.0.0.1:{port}/  （止めるときは Ctrl+C）")
        s.serve_forever()

if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "build"
    if cmd == "build":
        builder.build()
    elif cmd == "check":
        sys.exit(0 if builder.run_check() else 1)
    elif cmd == "new" and len(args) >= 2:
        print("作成:", os.path.relpath(new_note(args[1], args[2] if len(args) > 2 else ""), ROOT)); builder.build()
    elif cmd == "mkdir" and len(args) >= 2:
        print("作成:", os.path.relpath(new_folder(args[1]), ROOT)); builder.build()
    elif cmd == "serve":
        serve()
    else:
        print(__doc__)
