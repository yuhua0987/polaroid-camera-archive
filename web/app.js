/* SPDX-License-Identifier: MIT */
"use strict";
const D = JSON.parse(document.getElementById("data").textContent);
const all = D.models;
const byid = new Map(all.map(m => [m.id, m]));
const $ = id => document.getElementById(id);
const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[c]));
const priority = ["SX-70 折叠机", "600 系列", "Go 系列", "现代 i-Type"];
all.sort((a, b) => {
  const pa = priority.indexOf(a.family), pb = priority.indexOf(b.family);
  return (pa < 0 ? 9 : pa) - (pb < 0 ? 9 : pb) || a.id.localeCompare(b.id);
});
const groups = [...new Set([...priority, ...all.map(m => m.family)])];
let family = "", page = 1, active = null, index = 0;
const pageSize = 36;
const bundled = p => p.distribution === "bundled" && Boolean(p.path && p.thumb);
const pending = m => ["正面", "侧面", "背面"].filter(name => !(m.views_recorded || []).includes(name));
const localCount = m => m.photos.filter(bundled).length;
const sourceCounts = new Map();
for (const m of all) for (const p of m.photos) {
  const entry = sourceCounts.get(p.source_host) || {name:p.source_website, count:0};
  entry.count++;
  sourceCounts.set(p.source_host, entry);
}
$("source").innerHTML = '<option value="">全部来源网站</option>' + [...sourceCounts].sort((a,b) => b[1].count-a[1].count || a[0].localeCompare(b[0])).map(([host, entry]) => `<option value="${esc(host)}">${esc(entry.name)} (${entry.count})</option>`).join("");

function hero(m, respectFilters = false) {
  const matching = m.photos.filter(p => !respectFilters || photoMatch(p));
  const local = matching.filter(bundled);
  const available = local.length ? local : matching;
  return available.find(p => /^(正面|斜前方)/.test(p.label)) || available[0] || null;
}

// External previews are requested by the visitor's browser; no image proxy or copies.
function imageMarkup(p, alt, full = false) {
  const src = bundled(p) ? (full ? p.path : p.thumb) : (p.original_url || p.url);
  return `<img ${full ? '' : 'loading="lazy"'} decoding="async" referrerpolicy="no-referrer" src="${esc(src)}" alt="${esc(alt)}" data-source="${esc(p.source_website)}" ${bundled(p) ? '' : 'data-remote="true"'}>`;
}
document.addEventListener("error", e => {
  const img = e.target;
  if (!(img instanceof HTMLImageElement)) return;
  img.outerHTML = `<div class="image-unavailable" role="img" aria-label="图片暂不可用"><span>图片暂不可用</span><small>${esc(img.dataset.source || '')}</small><small>可在详情中打开来源网页</small></div>`;
}, true);

function views(m) {
  return (m.views_recorded || []).join(" · ") || "视角未标注";
}

function placeholder(m, small = false) {
  return `<div class="placeholder ${small ? "compact" : ""}"><b aria-hidden="true">${m.photos.length ? "↗" : "+"}</b><span>${m.photos.length ? "图片见来源页" : "照片待补"}</span></div>`;
}

$("stats").innerHTML = `<div class="stat"><b>${D.stats.models}</b><span>型号与命名版本</span></div><div class="stat"><b>${D.stats.families}</b><span>历史系列分组</span></div><div class="stat"><b>${D.stats.bundled_images}</b><span>张开放许可图片</span></div>`;
$("scope").textContent = `目录保存 ${D.stats.photo_references} 条图片参考，涉及 ${D.stats.referenced_images} 张去重图像。其中 ${D.stats.bundled_images} 张开放许可图片可离线查看，其余图片由浏览器从原网站加载预览，附来源链接；原站限制或失效时可打开来源网页。目录覆盖全历史主要系列，包含地区铭牌和特别用途版本，并非官方完整型号总数。`;
$("featured").innerHTML = ["P114", "P203", "P254"].map(id => {
  const m = byid.get(id), p = hero(m);
  return `<button class="feature" data-model="${id}" data-index="${Math.max(0, m.photos.indexOf(p))}">${p ? imageMarkup(p, m.name) : placeholder(m, true)}<b>${esc(m.name)}</b><span>${esc(m.family)} · ${p && bundled(p) ? "开放图片" : "外站图片"}</span><span>来源：${esc(p?.source_website || "待补")}</span></button>`;
}).join("");

function nav() {
  $("families").innerHTML = '<h2>相机系列 / SERIES</h2>' + ["", ...groups].map(g => `<button class="family ${g === family ? "active" : ""}" data-family="${esc(g)}" aria-pressed="${g === family}">${esc(g || "全部型号")}<span>${g ? all.filter(m => m.family === g).length : all.length}</span></button>`).join("") + '<div class="side-note">每张图都保留作者与许可。<br>来源参考不等于开放图片。<br>完整视角缺口见型号清单。</div>';
}

function angleMatch(p, angle) {
  return !angle || ({front:/^(正面|斜前方)/, side:/^侧面/, back:/^(背面|斜后方|后背)/, fold:/收合/, other:/未标注|待核对/}[angle].test(p.label));
}

function photoMatch(p) {
  const access = $("access").value;
  const source = $("source").value;
  return (!source || p.source_host === source) && angleMatch(p, $("angle").value) && (access === "all" || (access === "bundled" ? bundled(p) : !bundled(p)));
}

function filtered() {
  const q = $("search").value.trim().toLowerCase(), mode = $("mode").value;
  const needsPhotoMatch = Boolean($("angle").value) || Boolean($("source").value) || $("access").value !== "all";
  return all.filter(m => (!family || family === m.family)
    && (!q || `${m.id} ${m.name} ${m.family}`.toLowerCase().includes(q))
    && (mode !== "missing" || !m.photos.length)
    && (mode !== "gaps" || pending(m).length > 0)
    && (!needsPhotoMatch || m.photos.some(photoMatch)));
}

function render() {
  nav();
  const ms = filtered(), mode = $("mode").value;
  const rows = mode === "photos" ? ms.flatMap(m => m.photos.map((p, i) => ({m, p, i})).filter(x => photoMatch(x.p))) : ms;
  const pages = Math.max(1, Math.ceil(rows.length / pageSize));
  page = Math.min(page, pages);
  const subset = rows.slice((page - 1) * pageSize, page * pageSize);
  $("resultcount").textContent = mode === "photos" ? `${rows.length} 条图片参考 · ${rows.filter(x => bundled(x.p)).length} 张开放图片` : `${ms.length} 个型号 · ${ms.filter(m => localCount(m)).length} 个含开放图片`;
  if (!rows.length) {
    $("results").innerHTML = '<div class="empty">没有符合条件的条目。试试其他关键词、视角或图片范围。</div>';
  } else if (mode === "missing" || mode === "gaps") {
    $("results").innerHTML = '<div class="table-scroll"><table class="listtable"><thead><tr><th>编号</th><th>型号</th><th>系列 / 已标注方向</th><th>待补或待核对</th></tr></thead><tbody>' + subset.map(m => `<tr data-model="${m.id}" tabindex="0" role="button"><td>${m.id}</td><td>${esc(m.name)}</td><td>${esc(m.family)}<br><small>${esc(views(m))}</small></td><td class="missing">${esc(mode === "missing" ? "全部照片" : pending(m).join(" / "))}</td></tr>`).join("") + '</tbody></table></div>';
  } else {
    $("results").innerHTML = '<div class="grid">' + subset.map(row => {
      const m = mode === "photos" ? row.m : row;
      const p = mode === "photos" ? row.p : hero(m, true) || m.photos.find(photoMatch) || null;
      const i = mode === "photos" ? row.i : Math.max(0, m.photos.indexOf(p));
      const hasImage = Boolean(p);
      const caption = mode === "photos" ? p.label : `${m.photos.length} 条参考 · ${localCount(m)} 张开放图片`;
      return `<button class="card" data-model="${m.id}" data-index="${i}"><div class="cover">${hasImage ? imageMarkup(p, m.name + " · " + p.label) : placeholder(m)}<span class="count">${esc(mode === "photos" ? p && bundled(p) ? "开放图片" : "外站图片" : m.photos.length + " 条参考")}</span></div><div class="cardbody"><div class="modelid">${m.id} / ${esc(m.family)}</div><h3>${esc(m.name)}</h3><div class="subtitle">${esc(caption)}</div>${p ? `<div class="source-caption">来源：${esc(p.source_website)}</div>` : ""}</div></button>`;
    }).join("") + '</div>';
  }
  $("pagination").innerHTML = rows.length > pageSize ? `<button id="prev" ${page <= 1 ? "disabled" : ""}>上一页</button><span>${page} / ${pages}</span><button id="next" ${page >= pages ? "disabled" : ""}>下一页</button>` : "";
  for (const [id, delta] of [["prev", -1], ["next", 1]]) {
    if ($(id)) $(id).onclick = () => { page += delta; render(); $("search").scrollIntoView({block:"start"}); };
  }
}

function show(id, position = 0) {
  active = byid.get(id);
  if (!active) return;
  index = Math.min(Math.max(0, position), Math.max(0, active.photos.length - 1));
  $("detailfamily").textContent = `${active.family} / ${active.id}`;
  $("detailtitle").textContent = active.name;
  $("detailnote").textContent = (active.note || "型号按来源命名整理。") + " 正/侧/背待补或待核对：" + (pending(active).join(" / ") || "三视图已标注") + "。";
  showPhoto();
  if (!$("detail").open) $("detail").showModal();
}

function showPhoto() {
  const m = active, p = m.photos[index];
  const sourceImage = p && (p.original_url || p.url);
  $("thumbs").innerHTML = m.photos.map((item, i) => `<button class="thumb ${i === index ? "sel" : ""}" data-photo="${i}" aria-label="第${i + 1}条 · ${esc(item.label)}" title="${esc(item.label)}">${imageMarkup(item, item.label + " · " + item.source_website)}</button>`).join("");
  if (!p) {
    $("stage").innerHTML = '<div class="empty">尚未找到可核实的对应型号照片。</div>';
    $("meta").innerHTML = '<h3>型号资料</h3>' + m.sources.map((u, i) => `<p><a href="${esc(u)}" target="_blank" rel="noopener noreferrer">资料来源 ${i + 1} ↗</a></p>`).join("");
    return;
  }
  const arrows = m.photos.length > 1 ? '<button class="navpic prevpic" id="prevpic" aria-label="上一张">‹</button><button class="navpic nextpic" id="nextpic" aria-label="下一张">›</button>' : "";
  $("stage").innerHTML = imageMarkup(p, m.name + " · " + p.label, true) + arrows;
  $("meta").innerHTML = `<div class="eyebrow">${index + 1} / ${m.photos.length} REFERENCES</div><h3>${esc(p.label)}</h3><dl><dt>收录方式</dt><dd>${bundled(p) ? "开放许可图片 · 可离线查看" : "外站图片预览 · 图片归原作者所有"}</dd><dt>来源网站</dt><dd><a href="${esc(p.source)}" target="_blank" rel="noopener noreferrer">${esc(p.source_website)}</a><br><small>${esc(p.source_host)}</small></dd><dt>收集时图像尺寸</dt><dd>${p.width} × ${p.height} px</dd><dt>作者 / 图片来源</dt><dd>${esc(p.credit)}</dd><dt>许可信息</dt><dd>${p.license_url ? `<a href="${esc(p.license_url)}" target="_blank" rel="noopener noreferrer">${esc(p.license)}</a>` : esc(p.license)}</dd></dl><div class="photolinks">${bundled(p) ? `<a href="${esc(p.path)}" target="_blank" rel="noopener">打开图片 ↗</a>` : ""}<a href="${esc(p.source)}" target="_blank" rel="noopener noreferrer">来源网页 ↗</a><a href="${esc(sourceImage)}" target="_blank" rel="noopener noreferrer">来源原图 ↗</a></div>${bundled(p) ? '<p class="origin">图像保留下载响应；缩略图经过缩放，透明区域使用白底。逐图署名与原许可随仓库保存。</p>' : ""}`;
  if ($("prevpic")) $("prevpic").onclick = () => step(-1);
  if ($("nextpic")) $("nextpic").onclick = () => step(1);
}

function step(delta) {
  if (!active?.photos.length) return;
  index = (index + delta + active.photos.length) % active.photos.length;
  showPhoto();
}

document.addEventListener("click", e => {
  const f = e.target.closest("[data-family]");
  if (f) { family = f.dataset.family; page = 1; render(); }
  const model = e.target.closest("[data-model]");
  if (model) show(model.dataset.model, Number(model.dataset.index || 0));
  const photo = e.target.closest("[data-photo]");
  if (photo) { index = Number(photo.dataset.photo); showPhoto(); }
});
document.addEventListener("keydown", e => {
  const row = e.target.closest("tr[data-model]");
  if (row && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); show(row.dataset.model); }
  if (!$("detail").open) return;
  if (e.key === "ArrowRight") step(1);
  if (e.key === "ArrowLeft") step(-1);
});
$("close").onclick = () => $("detail").close();
$("detail").addEventListener("click", e => {
  if (e.target !== $("detail")) return;
  const rect = $("detail").getBoundingClientRect();
  if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) $("detail").close();
});
for (const id of ["search", "mode", "angle", "access", "source"]) $(id).addEventListener(id === "search" ? "input" : "change", () => { page = 1; render(); });
render();
const hash = location.hash.slice(1);
if (byid.has(hash)) show(hash);
