# JobSteward 部署与同步详细指南

## 一、部署方式

### A. GitHub Pages（匿名公开，推荐）

1. 登录 GitHub，新建仓库（如 `jobsteward`）或 Fork `https://github.com/ll-lab0/jobsteward`。
2. 把 `index.html` 放到仓库根目录（main 分支）。
3. 仓库 → Settings → Pages → Source 选 `Deploy from a branch` → Branch 选 `main` / `(root)` → Save。
4. 等待约 1 分钟，访问 `https://<你的用户名>.github.io/<仓库名>/`。
5. 验证：匿名（退出登录）浏览器打开应能正常渲染、可录入。

> 国内访问偶慢属正常，可下载 `index.html` 本地双击使用，功能完全一致。

### B. 任意静态托管

Vercel / Netlify / EdgeOne / 对象存储（OSS/COS + CDN）均只需上传单个 `index.html`，按平台指引设为静态站点根即可。无需构建、无需后端。

### C. 本地双击

直接双击 `index.html` 用浏览器打开。数据存浏览器 localStorage，不联网也照用；但跨设备同步需走方式 A/B + Gist。

## 二、跨设备同步（GitHub 私有 Gist）

### 步骤

1. 打开 https://github.com/settings/tokens
2. 点 **Generate new token (classic)**，Note 随意（如 `jobsteward-sync`）。
3. 权限**只勾 `gist`** 一项，其余全部不勾（最小权限）。
4. 生成后复制 `ghp_xxxxxxxxxxxx` 令牌（只显示一次）。
5. 工具内点顶部「云同步」→ 粘贴令牌 → 点保存并连接。
6. 首次连接自动在你的账户下创建**私有 Gist**（名为 `jobsteward-data`，内容加密无关、仅你可见）。
7. 第二台设备：打开同一工具 → 云同步 → 粘贴**同一令牌** → 连接即同步同一份数据。

### 排错

- **令牌无效/401**：令牌复制不完整，或权限未勾 `gist`，或 token 已过期/撤销。重新生成 classic token（只勾 gist）再连。
- **连接后数据为空**：首次连接是空库属正常；在任一设备录入并等待 800ms 自动推送后，另一台刷新即同步。
- **两设备互相覆盖**：不会。每次改动防抖推送前先拉云端按 `updated` 合并；删除优先。
- **手机端清了浏览器数据**：令牌有 10 年 cookie 回退兜底；若仍丢失，重新粘贴令牌连同一 Gist 即可恢复。

## 三、隐私与安全边界

- 无后端、无追踪、无第三方脚本；所有字段经 HTML 转义，导入仅 `JSON.parse` 不 `eval`。
- 同步令牌仅本机存储，不上传作者服务器；数据经你的私有 Gist，作者（李玲）无法访问内容。
- 不要把令牌提交到公开仓库或发给他人——他人持令牌可读写你的 Gist。

## 四、与"平台托管克隆"方案的区别（卖点）

- 平台托管克隆（如资料库"做同款"）：登录墙 + 数据落作者云表，用户数据不归己。
- 本方案：GitHub Pages 匿名公开 + 数据走用户自己的 Gist，每人数据互不可见、作者不可见、无平台锁定。
