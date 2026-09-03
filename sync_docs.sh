#!/bin/bash
# sync_docs.sh
# 从 GitHub 原项目同步设计稿到本项目的 docs/ 目录
# 用法: ./sync_docs.sh [owner/repo] [branch]

set -e

REPO="${1:-ITJacob/CardGame}"
BRANCH="${2:-main}"
SUBDIR="docs"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$SCRIPT_DIR/docs"
TEMP_DIR="$(mktemp -d)"

echo "========================================"
echo "  设计稿同步工具 (GitHub)"
echo "========================================"
echo ""
echo "📁 源仓库: https://github.com/$REPO ($BRANCH/$SUBDIR)"
echo "📂 同步目标: $TARGET_DIR"
echo ""

cleanup() { rm -rf "$TEMP_DIR"; }
trap cleanup EXIT

# 稀疏克隆，只拉取 docs 目录
echo "🔄 正在从 GitHub 拉取..."
git clone --depth 1 --filter=blob:none --sparse --branch "$BRANCH" "https://github.com/$REPO.git" "$TEMP_DIR" 2>&1 | grep -v "^Cloning" || true
git -C "$TEMP_DIR" sparse-checkout set "$SUBDIR"

if [ ! -d "$TEMP_DIR/$SUBDIR" ]; then
    echo "❌ 仓库中未找到 $SUBDIR 目录"
    exit 1
fi

# 清空并复制（docs 为只读镜像，与源保持一致）
mkdir -p "$TARGET_DIR"
find "$TARGET_DIR" -mindepth 1 -not -name ".gitkeep" -delete
cp -r "$TEMP_DIR/$SUBDIR/." "$TARGET_DIR/"

echo ""
echo "✅ 同步完成!"
echo ""
echo "📋 当前 docs/ 目录内容:"
find "$TARGET_DIR" -type f | head -20
