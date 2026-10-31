// 全ページ共通の動き：サイドバー（ノート一覧・全文検索）・テーマ・表示の切替・○×・チェックリスト
(() => {
  const $ = (id) => document.getElementById(id);
  const root = document.documentElement;
  const HUB = window.HUB || { root: "", assets: "", path: "" };
  const store = {
    get: (k, d) => { try { const v = localStorage.getItem(k); return v == null ? d : v; } catch (e) { return d; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* 保存できなくても動かす */ } },
  };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const norm = (s) => s.normalize("NFKC").toLowerCase();
  const href = (p, extra = "") => HUB.root + p.split("/").map(encodeURIComponent).join("/") + "/index.html" + extra;

  const TREE = window.HUB_TREE || [];
  const NOTES = {};
  (function walk(ns) { ns.forEach((n) => (n.type === "dir" ? walk(n.children) : (NOTES[n.path] = n))); })(TREE);

  // ── テーマ ──
  const theme = () => root.getAttribute("data-theme") || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
  function applyTheme(t) {
    root.setAttribute("data-theme", t);
    store.set("hub-theme", t);
    document.querySelectorAll("[data-theme-set]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.themeSet === t)));
  }
  document.querySelectorAll("[data-theme-set]").forEach((b) => (b.onclick = () => applyTheme(b.dataset.themeSet)));
  applyTheme(theme());

  // ── サイドバー（スマホは重ねる・PC は出しっぱなしで本文がずれる）──
  const mobile = () => matchMedia("(max-width:760px)").matches;
  const isOpen = () => root.classList.contains(mobile() ? "open" : "pinned");
  function setDrawer(open) {
    if (mobile()) root.classList.toggle("open", open);
    else { root.classList.toggle("pinned", open); store.set("hub-pinned", open ? "1" : "0"); }
  }
  $("btn-menu").onclick = () => setDrawer(!isOpen());
  $("btn-close").onclick = () => setDrawer(false);
  $("scrim").onclick = () => setDrawer(false);
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && mobile()) setDrawer(false);
    if ((e.metaKey || e.ctrlKey) && e.key === "\\") { e.preventDefault(); setDrawer(!isOpen()); } // Notion と同じ ⌘\
  });
  requestAnimationFrame(() => requestAnimationFrame(() => root.classList.add("ready"))); // 読み込み直後はアニメーションしない

  // ── ノート一覧 ──
  const closed = new Set(JSON.parse(store.get("hub-closed", "[]")));
  const count = (ns) => ns.reduce((a, n) => a + (n.type === "dir" ? count(n.children) : 1), 0);
  function renderTree() {
    const draw = (nodes) => nodes.map((n) => {
      if (n.type === "dir") {
        const open = !closed.has(n.path);
        const body = n.children.length ? draw(n.children) : `<div class="empty-msg">まだノートがありません</div>`;
        return `<div class="grp-n${open ? " open" : ""}"><button type="button" class="grp-h" data-dir="${esc(n.path)}"><i class="car"></i>${esc(n.name)}<span class="n">${count(n.children)}</span></button><div class="grp-b">${body}</div></div>`;
      }
      return `<a class="item${HUB.path === n.path ? " on" : ""}" href="${esc(href(n.path))}" title="${esc(n.title)}"><i class="dt"></i><span class="nm">${esc(n.name)}</span></a>`;
    }).join("");
    $("nav").innerHTML = draw(TREE);
  }
  $("nav").addEventListener("click", (e) => {
    const h = e.target.closest(".grp-h");
    if (!h) return;
    closed.has(h.dataset.dir) ? closed.delete(h.dataset.dir) : closed.add(h.dataset.dir);
    store.set("hub-closed", JSON.stringify([...closed]));
    renderTree();
  });

  // ── 全文検索（索引 search.js は検索欄を触ったときに読む）──
  let index = null, q = "";
  function loadIndex() {
    if (index || $("search-js")) return;
    const sc = document.createElement("script");
    sc.id = "search-js"; sc.src = HUB.assets + "search.js";
    sc.onload = () => {
      index = {};
      Object.entries(window.HUB_SEARCH || {}).forEach(([p, secs]) => (index[p] = secs.map(([id, label, body]) => ({ id, label, body, low: body.toLowerCase() }))));
      if (q) renderResults();
    };
    document.head.appendChild(sc);
  }
  const reEsc = (t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  function snippet(body, toks) {
    const low = body.toLowerCase();
    let at = -1, len = 0;
    toks.forEach((t) => { const i = low.indexOf(t); if (i >= 0 && (at < 0 || i < at)) { at = i; len = t.length; } });
    if (at < 0) return esc(body.slice(0, 60));
    const from = Math.max(0, at - 24), to = Math.min(body.length, at + len + 40);
    let h = esc(body.slice(from, to));
    toks.forEach((t) => { h = h.replace(new RegExp(reEsc(esc(t)), "gi"), (m) => `<mark>${m}</mark>`); });
    return (from > 0 ? "…" : "") + h + (to < body.length ? "…" : "");
  }
  function renderResults() {
    const toks = norm(q).split(/\s+/).filter(Boolean);
    const res = [];
    Object.values(NOTES).forEach((n) => {
      const name = norm(n.path + " " + n.title);
      const secs = (index && index[n.path]) || [];
      if (!toks.every((t) => name.includes(t) || secs.some((x) => x.low.includes(t)))) return;
      let hits = secs.filter((x) => toks.every((t) => x.low.includes(t)));
      if (!hits.length) hits = secs.filter((x) => toks.some((t) => x.low.includes(t)));
      const cnt = secs.reduce((a, x) => a + toks.reduce((b, t) => b + x.low.split(t).length - 1, 0), 0);
      res.push({ n, nameHit: toks.every((t) => name.includes(t)), cnt, hits: hits.slice(0, 4) });
    });
    res.sort((a, b) => (b.nameHit - a.nameHit) || (b.cnt - a.cnt));
    if (!res.length) { $("nav").innerHTML = `<div class="empty-msg">「${esc(q)}」は見つかりません</div>`; return; }
    const qs = "?q=" + encodeURIComponent(q);
    $("nav").innerHTML = `<div class="res-h">${res.length} 冊に見つかった${index ? "" : "（本文を読み込み中…）"}</div>` + res.map((r) =>
      `<div class="res"><a class="item${HUB.path === r.n.path ? " on" : ""}" href="${esc(href(r.n.path, qs))}"><i class="dt"></i><span class="nm">${esc(r.n.name)}</span><span class="cnt">${r.cnt ? r.cnt + "件" : ""}</span></a>` +
      r.hits.map((x) => `<a class="hit" href="${esc(href(r.n.path, qs + "#" + encodeURIComponent(x.id)))}"><span class="hl2">${esc(x.label)}</span><span class="sn">${snippet(x.body, toks)}</span></a>`).join("") + "</div>"
    ).join("");
  }
  $("filter").addEventListener("focus", loadIndex);
  $("filter").addEventListener("input", (e) => { q = e.target.value.trim(); if (!q) return renderTree(); loadIndex(); renderResults(); });
  $("nav").addEventListener("click", (e) => {
    const a = e.target.closest("a.hit, a.item");
    if (!a) return;
    const u = new URL(a.href, location.href);
    if (u.pathname === location.pathname) { // 同じノートの中なら読み直さずに飛ぶ
      e.preventDefault();
      history.replaceState(null, "", u.search + u.hash);
      highlight(u.searchParams.get("q"), decodeURIComponent(u.hash.slice(1)));
    }
    if (mobile()) setDrawer(false);
  });
  renderTree();

  // 検索結果から来たら、その語をノートの中でハイライトしてスクロールする
  let marks = [];
  function highlight(query, id) {
    marks.forEach((m) => { const p = m.parentNode; if (p) { p.replaceChild(document.createTextNode(m.textContent), m); p.normalize(); } });
    marks = [];
    if (!query) return;
    const toks = norm(query).split(/\s+/).filter(Boolean);
    const scope = (id && document.getElementById(id)) || document.querySelector("main");
    const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT, {
      acceptNode: (n) => (n.parentElement && !n.parentElement.closest("script,style,svg,mjx-container") ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT),
    });
    const hits = [];
    let n;
    while ((n = walker.nextNode()) && hits.length < 60) {
      const low = n.nodeValue.normalize("NFKC").toLowerCase();
      if (low.length !== n.nodeValue.length) continue; // 正規化で長さが変わる所は位置がずれるので飛ばす
      toks.forEach((t) => { const i = low.indexOf(t); if (i >= 0) hits.push([n, i, t.length]); });
    }
    hits.reverse().forEach(([node, i, len]) => {
      const r = document.createRange();
      try { r.setStart(node, i); r.setEnd(node, i + len); const m = document.createElement("mark"); m.className = "q"; r.surroundContents(m); marks.unshift(m); } catch (e) { /* 要素をまたぐ所は諦める */ }
    });
    const first = marks[0];
    if (first) {
      const det = first.closest("details"); if (det) det.open = true;
      first.scrollIntoView({ block: "center" });
    } else if (id && document.getElementById(id)) document.getElementById(id).scrollIntoView({ block: "start" });
  }
  const params = new URLSearchParams(location.search);
  if (params.get("q")) {
    $("filter").value = params.get("q");
    window.addEventListener("load", () => setTimeout(() => highlight(params.get("q"), decodeURIComponent(location.hash.slice(1))), 60));
  }

  // ── 表示の切替（全部／金だけ／公式だけ）──
  const fbtn = document.querySelectorAll(".filters button");
  function setMode(m) {
    document.body.classList.remove("mode-accent", "mode-fx");
    if (m !== "all") document.body.classList.add("mode-" + m);
    fbtn.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.mode === m)));
    store.set("hub-mode:" + HUB.path, m);
  }
  if (fbtn.length) {
    fbtn.forEach((b) => (b.onclick = () => setMode(b.dataset.mode)));
    const saved = store.get("hub-mode:" + HUB.path, "all");
    setMode([...fbtn].some((b) => b.dataset.mode === saved) ? saved : "all");
  }

  // ── ○× ──
  document.querySelectorAll(".oxq").forEach((li) => li.querySelectorAll("button").forEach((b) => (b.onclick = () => {
    li.classList.add("done");
    li.classList.toggle("ok", b.dataset.v === li.dataset.a);
    li.classList.toggle("ng", b.dataset.v !== li.dataset.a);
  })));

  // ── これが言えたら次へ（チェックはこの端末に覚えておく）──
  document.querySelectorAll(".check input").forEach((cb) => {
    const k = "hub-check:" + HUB.path + ":" + cb.nextElementSibling.textContent.trim();
    cb.checked = store.get(k, "0") === "1";
    cb.onchange = () => store.set(k, cb.checked ? "1" : "0");
  });
})();
