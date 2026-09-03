#!/bin/bash
# sync_docs.sh
# 从原项目同步设计稿到本项目的 docs/ 目录
# 用法: ./sync_docs.sh [原项目路径]

set -e

SOURCE_PROJECT="${1:-../your-old-project}"  # 默认上级目录的原项目
TARGET_DIR="./docs"
SOURCE_DOCS="$SOURCE_PROJECT/docs"

echo "========================================"
echo "  设计稿同步工具"
echo "========================================"
echo ""

# 检查源项目是否存在
if [ ! -d "$SOURCE_PROJECT" ]; then
    echo "❌ 错误: 找不到原项目目录: $SOURCE_PROJECT"
    echo "   请修改脚本中的 SOURCE_PROJECT 变量，或传入路径参数"
    echo "   用法: ./sync_docs.sh /path/to/your-old-project"
    exit 1
fi

# 检查源项目的 docs 目录
if [ ! -d "$SOURCE_DOCS" ]; then
    echo "⚠️  警告: 原项目中未找到 docs/ 目录: $SOURCE_DOCS"
    echo "   请确认原项目的文档存放位置"
    exit 1
fi

# 创建目标目录
mkdir -p "$TARGET_DIR"

echo "📁 源项目: $SOURCE_PROJECT"
echo "📂 同步目标: $TARGET_DIR"
echo ""

# 使用 rsync 或 cp 进行同步
if command -v rsync &> /dev/null; then
    echo "🔄 使用 rsync 同步..."
    rsync -av --delete "$SOURCE_DOCS/" "$TARGET_DIR/"
else
    echo "🔄 使用 cp 同步..."
    rm -rf "$TARGET_DIR"/*
    cp -r "$SOURCE_DOCS"/* "$TARGET_DIR/"
fi

echo ""
echo "✅ 同步完成!"
echo ""
echo "📋 当前 docs/ 目录内容:"
find "$TARGET_DIR" -type f | head -20
