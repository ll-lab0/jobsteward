#!/bin/bash
# jobsteward 一键发布到 GitHub Pages
# 用法：先在本目录的 .env 里填好 GITHUB_TOKEN，然后运行：bash deploy.sh
set -e
cd "$(dirname "$0")"

if [ -f .env ]; then
  source .env
fi

if [ -z "$GITHUB_TOKEN" ]; then
  echo "❌ 未找到 GITHUB_TOKEN。请打开 .env，在 GITHUB_TOKEN= 后面填入你的新 ghp_ 令牌后重试。"
  exit 1
fi

echo "📦 暂存改动..."
git add -A

echo "💾 提交..."
git commit -m "deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "（无新改动，跳过提交）"

echo "🚀 推送到 GitHub Pages..."
# 用 .env 里的 token 内嵌到 URL 推送，不依赖 macOS Keychain，也不读取旧凭证
git -c credential.helper= push "https://$GITHUB_TOKEN@github.com/ll-lab0/jobsteward.git" HEAD:main

echo "✅ 发布完成。稍候数秒后访问 https://ll-lab0.github.io/jobsteward/"
