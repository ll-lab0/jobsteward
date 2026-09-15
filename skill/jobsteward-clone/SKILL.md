---
name: jobsteward-clone
description: This skill should be used when a user wants to deploy, clone, or self-host the 求职管家 (JobSteward) — a single-file HTML job-hunting tracker with a data dashboard (总览/状态分布/周期趋势), JD auto-fill, and cross-device GitHub Gist sync. It bundles the self-contained index.html and provides GitHub Pages / static-host deploy steps plus Gist sync setup, so the user runs their own instance with data stored in their own private Gist (author cannot access). Trigger phrases include '部署求职跟踪工具', '克隆 jobsteward', '搭一个求职管理工具', '一键创建求职追踪器', '做个求职投递看板'.
agent_created: true
---

# JobSteward Clone

## Overview

求职管家（JobSteward）是一个**纯前端、零依赖的单文件 HTML** 求职管理工具：把投递全流程（岗位、状态、周期、JD、备注）管清楚，带数据看板与 JD 自动填充，可选连接 GitHub 私有 Gist 跨设备同步。本 Skill 让另一个用户/AI **一键克隆出属于自己的实例**——数据存在用户自己的 Gist，作者（李玲）看不到、平台不锁。

## When To Use

- 用户说"部署/克隆/搭一个求职跟踪工具""做同款 jobsteward""求职投递看板"。
- 用户想要一个**自己掌控数据**的求职管理工具，不愿把数据交给第三方 SaaS。
- 作为"去平台化单文件应用"的复刻范例。

## How To Use

### 1. 取得应用本体

应用是单个自包含文件 `assets/index.html`（CSS/JS/SVG 全内联，约 128KB，双击即用）。最新版也在 GitHub 仓库 `https://github.com/ll-lab0/jobsteward` 的 `index.html`。两者等价，优先用仓库最新版。

### 2. 部署（三选一）

- **A. GitHub Pages（匿名公开，推荐）**：Fork/新建仓库 → 上传 `index.html` → Settings → Pages → Source 选 `main`/根目录 → 生成 `https://<你>.github.io/<仓库>/`，永久免费、无需登录即可打开。
- **B. 任意静态托管**：Vercel / Netlify / EdgeOne / 对象存储，上传 `index.html` 即可。
- **C. 本地双击**：直接双击 `index.html` 用浏览器打开，数据存本机，不联网也照用。

### 3. 跨设备同步（GitHub 私有 Gist，可选）

1. 打开 https://github.com/settings/tokens
2. **Generate new token (classic)**，Note 随意
3. 权限**只勾 `gist`**
4. 复制 `ghp_...` 令牌
5. 工具内点顶部「云同步」→ 粘贴令牌 → 保存并连接
6. 首次连接自动在用户账户下创建**私有 Gist**；另一台设备贴同一令牌即连同一份备份
7. **同步状态与失败重试**：连接后顶部状态条实时显示「同步中 / 已同步 / 失败原因」；失败会分类提示（令牌无效、网络异常、GitHub 配额受限）并明确「本地数据已保留，未上传」，弹窗内提供「重试同步」按钮，不会静默丢数据。

> 数据通过用户自己的私有 Gist 同步，作者无法访问。令牌仅存用户本机浏览器，不上传任何第三方服务器。

### 4. 关键设计点（复刻/改造时必读）

- **无后端**：全部逻辑在单文件内，无服务器、无追踪、无第三方脚本。
- **数据归属用户**：同步走用户自己的 Gist，克隆出的每个实例数据互不可见。
- **合并策略**：首连按记录 `更新时间` 合并、删除优先；**打开/刷新页面即自动双向同步**（上传本机改动并拉取其他设备），改字段后 800ms 防抖推送，页面常开时每 25 秒后台拉取；推送前先拉云端合并，单方不覆盖另一方。
- **移动端弹窗**：iOS Safari 用 inner-scroll（滚动收进 `#scrollRoot`，window 永不滚动）避免弹窗跳首屏；微信 WebView 无此问题。

## Resources

- `assets/index.html` — 应用本体（单文件，可部署/克隆）
- `references/deploy.md` — 部署与 Gist 同步的详细步骤与排错

## 应用市场上架说明

本 Skill 即"做同款"的打包形态：上架 WorkBuddy 应用市场后，用户安装即获得上述部署能力（换 ID 即用）。数据仍走各自 Gist，不落作者云表——这是相比"平台托管克隆"方案的核心安全优势。上架前的提交/审核流程以 WorkBuddy 应用市场实际规范为准。
