#!/bin/bash
# sync_docs.sh
# 同步原项目设计稿到本项目的 docs/ 目录（docs 为只读镜像，与源保持一致）
# 用法:
#   ./sync_docs.sh --local /path/to/docs   # 从本地目录同步
#   ./sync_docs.sh [owner/repo] [branch]   # 从 GitHub 同步（默认）

set -e

LOCAL_PATH=""
REPO="ITJacob/CardGame"
BRANCH="main"
if [ "$1" = "--local" ]; then
    LOCAL_PATH="${2:?用法: ./sync_docs.sh --local /path/to/docs}"
else
    REPO="${1:-$REPO}"
    BRANCH="${2:-$BRANCH}"
fi

SUBDIR="docs"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$SCRIPT_DIR/docs"
TEMP_DIR="$(mktemp -d)"

cleanup() { rm -rf "$TEMP_DIR"; }
trap cleanup EXIT

echo "========================================"
echo "  设计稿同步工具"
echo "========================================"
echo ""

if [ -n "$LOCAL_PATH" ]; then
    # 本地模式：直接从本地目录复制
    echo "📁 源目录: $LOCAL_PATH (本地)"
    if [ ! -d "$LOCAL_PATH" ]; then
        echo "❌ 本地路径不存在: $LOCAL_PATH"
        exit 1
    fi
    SOURCE_DOCS="$LOCAL_PATH"
else
    # GitHub 模式：稀疏克隆，只拉取 docs 目录
    echo "📁 源仓库: https://github.com/$REPO ($BRANCH/$SUBDIR)"
    echo "🔄 正在从 GitHub 拉取..."
    git clone --depth 1 --filter=blob:none --sparse --branch "$BRANCH" "https://github.com/$REPO.git" "$TEMP_DIR" 2>&1 | grep -v "^Cloning" || true
    git -C "$TEMP_DIR" sparse-checkout set "$SUBDIR"

    if [ ! -d "$TEMP_DIR/$SUBDIR" ]; then
        echo "❌ 仓库中未找到 $SUBDIR 目录"
        exit 1
    fi
    SOURCE_DOCS="$TEMP_DIR/$SUBDIR"
fi

echo "📂 同步目标: $TARGET_DIR"
echo ""

# 清空并复制（docs 为只读镜像，与源保持一致）
mkdir -p "$TARGET_DIR"
find "$TARGET_DIR" -mindepth 1 -not -name ".gitkeep" -delete
cp -r "$SOURCE_DOCS/." "$TARGET_DIR/"

echo ""
echo "✅ 同步完成!"
echo ""
echo "📋 当前 docs/ 目录内容:"
find "$TARGET_DIR" -type f | head -20
