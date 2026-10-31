// MathJax の設定（数式を使うページだけ読み込む）。ノートごとのマクロは note.json の "macros" から入る
window.MathJax = {
  loader: { load: ["[tex]/boldsymbol"] },
  tex: {
    packages: { "[+]": ["boldsymbol"] },
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    macros: window.NOTE_MACROS || {},
  },
  svg: { fontCache: "global" },
  options: { skipHtmlTags: ["script", "noscript", "style", "textarea", "pre", "code", "svg"] },
};
