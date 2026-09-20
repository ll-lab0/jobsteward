#!/usr/bin/env python3
# 直接调 GitHub Contents API 推送 index.html 到 ll-lab0/jobsteward
# 完全绕过本地 git，不受 .git/index.lock 影响。
# token 从 .env 读取，不打印、不进日志。

import base64
import json
import urllib.request
import urllib.error

# ---- 读 GITHUB_TOKEN：优先 .env，其次桌面可见的 填GITHUB令牌.txt ----
token = ''
for env_file in ('.env', '/Users/liling/Desktop/填GITHUB令牌.txt'):
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('GITHUB_TOKEN='):
                    token = line[len('GITHUB_TOKEN='):].strip().strip('"').strip("'")
                    if token:
                        break
    except FileNotFoundError:
        continue
    if token:
        break

if not token:
    print("❌ 没读到令牌。请打开桌面上的「填GITHUB令牌.txt」，"
          "把新的 ghp_ 令牌粘到 GITHUB_TOKEN= 后面并保存，然后再运行本脚本。")
    raise SystemExit(1)

REPO = 'll-lab0/jobsteward'
BRANCH = 'main'
FILE = 'index.html'
API = f'https://api.github.com/repos/{REPO}/contents/{FILE}'

headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'jobsteward-deploy',
    'Content-Type': 'application/json',
}

# ---- 读本地 index.html ----
with open(FILE, 'rb') as f:
    content_b64 = base64.b64encode(f.read()).decode('ascii')

# ---- 获取当前 sha（更新需要）----
sha = None
req = urllib.request.Request(API, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        sha = json.loads(resp.read())['sha']
    print('📄 已读取仓库现有文件，准备更新 (sha 前6位: %s)' % sha[:6])
except urllib.error.HTTPError as e:
    if e.code == 404:
        print('📄 仓库暂无该文件，将新建')
    else:
        print('❌ 读取仓库文件失败 %s' % e.code)
        print(e.read().decode('utf-8', 'ignore')[:300])
        raise SystemExit(1)

# ---- 推送 ----
body = {
    'message': 'fix(github-sync): 令牌失效后弹窗显示重新输入入口',
    'content': content_b64,
    'branch': BRANCH,
}
if sha:
    body['sha'] = sha

data = json.dumps(body).encode('utf-8')
req = urllib.request.Request(API, data=data, headers=headers, method='PUT')
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        r = json.loads(resp.read())
        print('✅ 发布成功！commit: %s' % r.get('commit', {}).get('sha', '')[:10])
        print('🌐 页面数秒后更新：https://ll-lab0.github.io/jobsteward/')
except urllib.error.HTTPError as e:
    print('❌ 发布失败 %s' % e.code)
    print(e.read().decode('utf-8', 'ignore')[:500])
    raise SystemExit(1)
