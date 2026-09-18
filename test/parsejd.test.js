#!/usr/bin/env node
/**
 * parseJD 回归测试
 * ------------------------------------------------------------------
 * 作用：每次改动 index.html 里的 parseJD（JD 自动识别：公司/职位/薪资）
 *       之前先跑一遍，确认没有改坏常见格式。
 *
 * 运行：node test/parsejd.test.js
 *
 * 原理：单一真相源纪律 —— 测试不另写一份解析逻辑，而是直接从
 *       ../index.html 抽取真实线上的 cleanStr / stripMd / cleanPos /
 *       parseJD 四个函数，eval 后跑用例。这样 index.html 改了，
 *       测试永远测的是线上真实代码。
 *
 * 维护：如果某次是有意优化识别（比如 case H 的职位误抓），
 *       相应更新下方的 expect 字段，并在 commit message 里说明。
 */

const fs = require('fs');
const path = require('path');

const htmlPath = path.resolve(__dirname, '../index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

// ---- 从 index.html 抽取函数（大括号配对，支持嵌套）----
function extractFn(src, name) {
  const re = new RegExp('function\\s+' + name + '\\s*\\([^)]*\\)\\s*\\{', 'g');
  const m = re.exec(src);
  if (!m) throw new Error('函数未找到: ' + name);
  let i = m.index + m[0].length, depth = 1;
  while (i < src.length && depth > 0) {
    const ch = src[i];
    if (ch === '{') depth++;
    else if (ch === '}') depth--;
    i++;
  }
  return src.slice(m.index, i);
}

eval(extractFn(html, 'cleanStr'));
eval(extractFn(html, 'stripMd'));
eval(extractFn(html, 'cleanPos'));
eval(extractFn(html, 'fixOcrSpacing'));
eval(extractFn(html, 'parseJD'));

// ---- 覆盖各类 JD 形态的用例（公司名识别是本次重点）----
const cases = [
  {
    name: 'A 月之暗面（AI 转述残留首行）',
    jd: '以下是完整版（已补全公司名称）：\n---\n**月之暗面（Moonshot AI）正在招聘**\n# AI Operations Builder\n35-55K',
    expect: { company: '月之暗面（Moonshot AI）', position: 'AI Operations Builder', salary: '35-55K' }
  },
  {
    name: 'B 含「社会招聘」分区标题',
    jd: '某某网络科技\n## 社会招聘\n# 前端工程师\n薪资20-30K\n职位描述：负责...',
    expect: { company: '某某网络科技', position: '前端工程师', salary: '20-30K' }
  },
  {
    name: 'C 正文有「招聘人数：5人」',
    jd: '星辰智能科技\n# 产品经理\n招聘人数：5人\n职位描述：...',
    expect: { company: '星辰智能科技', position: '产品经理', salary: '' }
  },
  {
    name: 'D 职责含「负责招聘渠道」（修复点）',
    jd: '云图信息\n# HRBP\n岗位职责：负责招聘渠道维护与雇主品牌建设',
    expect: { company: '云图信息', position: 'HRBP', salary: '' }
  },
  {
    name: 'D2 bullet 含「负责招聘」（修复点）',
    jd: '# HRBP\n1. 负责招聘团队与雇主品牌\n公司：云图信息',
    expect: { company: '云图信息', position: 'HRBP', salary: '' }
  },
  {
    name: 'E 「XX诚聘」无招聘二字',
    jd: '蓝海数据\n诚聘\n# 数据分析师\n薪资25-35K',
    expect: { company: '蓝海数据', position: '数据分析师', salary: '25-35K' }
  },
  {
    name: 'F 纯首行公司名',
    jd: '腾讯科技\n# 后端工程师\n20-40K',
    expect: { company: '腾讯科技', position: '后端工程师', salary: '20-40K' }
  },
  {
    name: 'G 键值对 公司：字节',
    jd: '公司：字节跳动\n职位：产品经理\n薪资30-50K',
    expect: { company: '字节跳动', position: '产品经理', salary: '30-50K' }
  },
  {
    name: 'H 51job式 社招+正文招聘',
    jd: '## 社会招聘\n某独角兽公司\n我们正在招聘一名增长运营，负责...',
    expect: { company: '某独角兽公司', position: '我们正在招聘一名增长运营', salary: '' }
  },
  {
    name: 'I 正文招聘早于公司行',
    jd: '职位描述：我们正在招聘增长运营。\n小米科技\n# 产品经理',
    expect: { company: '小米科技', position: '产品经理', salary: '' }
  },
  {
    name: 'J 英文JD无招聘',
    jd: 'Acme AI Inc.\nWe are hiring a Product Manager.\n$40-60K',
    expect: { company: 'Acme AI Inc.', position: '', salary: '40-60K' }
  }
];

// ---- 执行 + 断言 ----
let pass = 0, fail = 0;
console.log('parseJD 回归测试 — 用例数 ' + cases.length);
console.log('源码: ' + htmlPath + '\n');

for (const c of cases) {
  const r = parseJD(c.jd);
  const fields = ['company', 'position', 'salary'];
  let ok = true;
  const diffs = [];
  for (const f of fields) {
    if (r[f] !== c.expect[f]) {
      ok = false;
      diffs.push('  ' + f + ': 期望 ' + JSON.stringify(c.expect[f]) + ' / 实际 ' + JSON.stringify(r[f]));
    }
  }
  if (ok) {
    pass++;
    console.log('  ✅ ' + c.name);
  } else {
    fail++;
    console.log('  ❌ ' + c.name);
    diffs.forEach(d => console.log(d));
  }
}

console.log('\n结果: ' + pass + ' 通过 / ' + fail + ' 失败');

// ---- OCR 间距场景：模拟 Tesseract 中文逐字加空格的输出 ----
// 这是 v72 修复的 bug：OCR 把「正在招聘」识别成「正 在 招 聘」，导致正则
// 匹配不到、公司/职位全失效。fixOcrSpacing 须折叠 CJK 间空格且保留换行。
const ocrCases = [
  {
    name: 'K OCR逐字空格·多行排版JD（直白美学/FDE前置交付工程师）',
    jd: '直 白 美 学 正 在 招 聘\nFDE 前 置 交 付 工 程 师\n北 京 /25-35K/ 经 验 不 限 /本 科\n职 位 详 情\n我 们 是 一 家 正 在 成 长 中 的 新 消 费 医 美 平台',
    expect: { company: '直白美学', position: 'FDE 前置交付工程师', salary: '25-35K' }
  },
  {
    name: 'L OCR逐字空格·月之暗面（验证换行不被连成一行）',
    jd: '以 下 是 完 整 版\n**月 之 暗 面（Moonshot AI）正 在 招 聘**\n# AI Operations Builder\n35-55K',
    expect: { company: '月之暗面（Moonshot AI）', position: 'AI Operations Builder', salary: '35-55K' }
  }
];

console.log('\nparseJD + fixOcrSpacing（OCR 间距）— 用例数 ' + ocrCases.length);
for (const c of ocrCases) {
  const r = parseJD(fixOcrSpacing(c.jd));
  const fields = ['company', 'position', 'salary'];
  let ok = true;
  const diffs = [];
  for (const f of fields) {
    if (r[f] !== c.expect[f]) {
      ok = false;
      diffs.push('  ' + f + ': 期望 ' + JSON.stringify(c.expect[f]) + ' / 实际 ' + JSON.stringify(r[f]));
    }
  }
  if (ok) { pass++; console.log('  ✅ ' + c.name); }
  else { fail++; console.log('  ❌ ' + c.name); diffs.forEach(d => console.log(d)); }
}

console.log('\n结果(含OCR): ' + pass + ' 通过 / ' + fail + ' 失败');
process.exit(fail === 0 ? 0 : 1);
