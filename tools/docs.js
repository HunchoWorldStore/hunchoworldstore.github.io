(() => {
  const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];

  // mobile menu
  const side = $("#side"), scrim = $("#scrim");
  const menu = on => { side.classList.toggle("on", on); scrim.classList.toggle("on", on); };
  $("#menuBtn") && $("#menuBtn").addEventListener("click", () => menu(true));
  scrim.addEventListener("click", () => menu(false));
  const cur = $(".nl.on"); if (cur) cur.scrollIntoView({ block: "center" });

  // tables scroll sideways on phones
  $$(".doc table").forEach(t => { const w = document.createElement("div"); w.className = "tw"; t.before(w); w.append(t); });

  // copy buttons on code
  $$(".doc pre").forEach(p => {
    const b = document.createElement("button"); b.className = "copy"; b.textContent = "Copy";
    b.onclick = () => { navigator.clipboard && navigator.clipboard.writeText(p.innerText.replace(/Copy$/, "").trim()).then(() => { b.textContent = "Copied"; setTimeout(() => b.textContent = "Copy", 1400); }); };
    p.append(b);
  });

  // GitBook-style tabs
  $$(".tabs").forEach(box => {
    const tabs = [...box.children].filter(c => c.classList.contains("tab"));
    const bar = document.createElement("div"); bar.className = "tabbar";
    tabs.forEach((t, i) => {
      const b = document.createElement("button"); b.textContent = t.dataset.title;
      b.onclick = () => { tabs.forEach((x, j) => x.hidden = j !== i); [...bar.children].forEach((x, j) => x.classList.toggle("on", j === i)); };
      bar.append(b); t.hidden = i !== 0; if (i === 0) b.classList.add("on");
    });
    box.prepend(bar);
  });

  // "On this page" highlight
  const tocLinks = $$(".tocin a");
  if (tocLinks.length) {
    const heads = tocLinks.map(a => document.getElementById(decodeURIComponent(a.hash.slice(1)))).filter(Boolean);
    const onScroll = () => {
      let i = 0; heads.forEach((h, j) => { if (h.getBoundingClientRect().top < 120) i = j; });
      tocLinks.forEach((a, j) => a.classList.toggle("on", j === i));
    };
    addEventListener("scroll", onScroll, { passive: true }); onScroll();
  }

  // search
  const box = $("#search"), q = $("#q"), res = $("#sres");
  let idx = null, sel = 0, hits = [];
  const esc = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const load = () => idx ? Promise.resolve(idx) : fetch("/docs/search.json").then(r => r.json()).then(j => idx = j);
  const open = () => { box.hidden = false; menu(false); q.value = ""; render(); setTimeout(() => q.focus(), 30); load().then(render); };
  const close = () => { box.hidden = true; };
  function snippet(text, words) {
    const low = text.toLowerCase(); let at = -1;
    for (const w of words) { at = low.indexOf(w); if (at >= 0) break; }
    if (at < 0) return "";
    let s = text.slice(Math.max(0, at - 50), at + 110);
    s = esc(s);
    words.forEach(w => { if (w.length > 1) s = s.replace(new RegExp("(" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>"); });
    return (at > 50 ? "…" : "") + s + "…";
  }
  function render() {
    const words = q.value.toLowerCase().split(/\s+/).filter(Boolean);
    if (!idx) { res.innerHTML = '<div class="none">Loading…</div>'; return; }
    if (!words.length) {
      hits = idx.filter(p => /download|escrow|permissions|installation/i.test(p.t)).slice(0, 8);
    } else {
      hits = idx.map(p => {
        const t = p.t.toLowerCase(), h = p.h.join(" ").toLowerCase(), x = p.x.toLowerCase(), s = p.s.toLowerCase();
        let score = 0;
        for (const w of words) {
          let ws = 0;
          if (t.includes(w)) ws += t.startsWith(w) ? 12 : 9;
          if (s.includes(w)) ws += 4;
          if (h.includes(w)) ws += 5;
          if (x.includes(w)) ws += 2 + Math.min(3, x.split(w).length - 1) * .5;
          if (!ws) return null;
          score += ws;
        }
        return { p, score };
      }).filter(Boolean).sort((a, b) => b.score - a.score).slice(0, 20).map(r => r.p);
    }
    sel = 0;
    res.innerHTML = hits.length ? hits.map((p, i) =>
      `<a href="${p.u}" class="${i === 0 ? "sel" : ""}"><small>${esc(p.s)}</small>${esc(p.t)}<em>${words.length ? snippet(p.x, words) : ""}</em></a>`).join("")
      : '<div class="none">No results. Try another word, or ask in our Discord.</div>';
  }
  q.addEventListener("input", render);
  q.addEventListener("keydown", e => {
    const items = [...res.querySelectorAll("a")];
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault(); if (!items.length) return;
      sel = (sel + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
      items.forEach((a, i) => a.classList.toggle("sel", i === sel)); items[sel].scrollIntoView({ block: "nearest" });
    } else if (e.key === "Enter" && items[sel]) { location.href = items[sel].href; }
  });
  $$("[data-search]").forEach(b => b.addEventListener("click", open));
  box.addEventListener("click", e => { if (e.target === box || e.target.closest("[data-close]")) close(); });
  addEventListener("keydown", e => {
    if ((e.key === "k" && (e.metaKey || e.ctrlKey)) || (e.key === "/" && !/input|textarea/i.test(document.activeElement.tagName))) { e.preventDefault(); open(); }
    else if (e.key === "Escape") { close(); menu(false); }
  });
})();
