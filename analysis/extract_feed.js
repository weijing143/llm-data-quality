// 从 数据质量研究动态-2025-2026.html 中抽取内嵌的 JS 数据数组，导出为 JSON
// 用法: node extract_feed.js
const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, '..', '数据质量研究动态-2025-2026.html'), 'utf8');

// 抽取 const NAME = [...]; 形式的数组（HTML 内为单 <script> 块，数组内无 "</script>"）
function extractArray(name) {
  const re = new RegExp('const ' + name + ' = \\[', 'm');
  const m = html.match(re);
  if (!m) return null;
  let i = m.index + m[0].length; // 位于 '[' 之后
  let depth = 1, start = i;
  while (i < html.length && depth > 0) {
    const c = html[i];
    if (c === '[') depth++;
    else if (c === ']') depth--;
    else if (c === "'" || c === '"' || c === '`') {
      // 跳过字符串字面量（含转义）
      const q = c; i++;
      while (i < html.length && html[i] !== q) { if (html[i] === '\\') i++; i++; }
    }
    i++;
  }
  const body = html.slice(start, i - 1);
  // 在 Node 中以 JS 求值（数据为对象字面量，安全：来源是本地受信文件）
  return eval('([' + body + '])');
}

const out = {};
for (const name of ['FEED', 'LABS', 'TOOLS', 'TRENDS', 'DEBATES', 'DELTA', 'SOURCES']) {
  const arr = extractArray(name);
  if (arr) {
    out[name] = arr;
    console.log(name + ': ' + arr.length + ' 条');
  } else {
    console.log(name + ': 未找到');
  }
}

fs.mkdirSync(path.join(__dirname, '..', 'data'), { recursive: true });
fs.writeFileSync(
  path.join(__dirname, '..', 'data', 'research-feed.json'),
  JSON.stringify({ extractedAt: '2026-09-17', source: '数据质量研究动态-2025-2026.html', ...out }, null, 2),
  'utf8'
);

// FEED 另存一份扁平 CSV（body 里的 HTML 标签剥掉，便于表格查看）
if (out.FEED) {
  const strip = s => String(s || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
  const esc = s => '"' + strip(s).replace(/"/g, '""') + '"';
  const rows = [['date', 'lab', 'topic', 'kind', 'kindLabel', 'title', 'summary', 'sources'].join(',')];
  for (const x of out.FEED) {
    const srcs = (x.src || []).map(s => s.u).join(' ; ');
    rows.push([x.date, x.lab, x.topic, x.kind, x.kindLabel, esc(x.title), esc(x.body), esc(srcs)].join(','));
  }
  fs.writeFileSync(path.join(__dirname, '..', 'data', 'research-feed.csv'), '﻿' + rows.join('\n'), 'utf8');
  console.log('CSV 写出: data/research-feed.csv, ' + out.FEED.length + ' 行');
}
console.log('JSON 写出: data/research-feed.json');
