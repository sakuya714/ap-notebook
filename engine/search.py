# -*- coding: utf-8 -*-
"""全文検索の索引：完成したノートの HTML を「節（章・ボード）ごとの本文」に分ける"""
import unicodedata
from html.parser import HTMLParser

class TextIndexer(HTMLParser):
    """ノート本文を「節（id の付いた section・見出し）ごとのテキスト」に分ける。全文検索用"""
    ANCHOR_TAGS = {"section", "article", "h1", "h2", "h3", "h4"}
    SKIP = {"script", "style", "nav", "noscript", "template", "button"}
    VOID = {"br", "img", "input", "meta", "link", "hr", "area", "base", "col", "embed", "source", "track", "wbr"}

    def __init__(self, labels):
        super().__init__(convert_charrefs=True)
        self.labels = labels          # id → 目次の名前
        self.secs = [["", "", []]]    # [id, label, [text]]
        self.skip = 0
        self.stack = []
        self.want_label = False
    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        self.stack.append(tag)
        if tag in self.SKIP:
            self.skip += 1
        a = dict(attrs)
        if a.get("id") and not self.skip and (tag in self.ANCHOR_TAGS or a["id"] in self.labels):
            self.secs.append([a["id"], self.labels.get(a["id"], ""), []])
            self.want_label = not self.secs[-1][1]
    def handle_endtag(self, tag):
        if tag in self.VOID or tag not in self.stack:
            return
        while self.stack:
            t = self.stack.pop()
            if t in self.SKIP:
                self.skip -= 1
            if t == tag:
                break
    def handle_data(self, data):
        if self.skip:
            return
        t = " ".join(data.split())
        if not t:
            return
        cur = self.secs[-1]
        if self.want_label and len(t) > 1:
            cur[1] = t[:40]; self.want_label = False
        cur[2].append(t)

def text_index(page, outline):
    labels = {}
    for sid, label in outline:
        labels[sid] = label
    ix = TextIndexer(labels)
    ix.feed(page)
    out = []
    for sid, label, texts in ix.secs:
        body = unicodedata.normalize("NFKC", " ".join(texts))
        if body:
            out.append([sid, label or "表紙", body])
    return out

