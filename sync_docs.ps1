# sync_docs.ps1
# 从原项目同步设计稿到本项目的 docs/ 目录
# 用法: .\sync_docs.ps1 [原项目路径]

$SourceProject = if ($args[0]) { $args[0] } else { "..\your-old-project" }
$TargetDir = ".\docs"
$SourceDocs = Join-Path $SourceProject "docs"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  设计稿同步工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查源项目
if (-not (Test-Path $SourceProject)) {
    Write-Host "❌ 错误: 找不到原项目目录: $SourceProject" -ForegroundColor Red
    Write-Host "   请修改脚本中的 \$SourceProject 变量，或传入路径参数" -ForegroundColor Yellow
    Write-Host "   用法: .\sync_docs.ps1 C:\path\to\your-old-project" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $SourceDocs)) {
    Write-Host "⚠️  警告: 原项目中未找到 docs 目录: $SourceDocs" -ForegroundColor Yellow
    exit 1
}

# 创建目标目录
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

Write-Host "📁 源项目: $SourceProject" -ForegroundColor Green
Write-Host "📂 同步目标: $TargetDir" -ForegroundColor Green
Write-Host ""

# 同步文件
Write-Host "🔄 正在同步文件..." -ForegroundColor Cyan
$sourceFiles = Get-ChildItem -Path $SourceDocs -Recurse -File
foreach ($file in $sourceFiles) {
    $relativePath = $file.FullName.Substring((Resolve-Path $SourceDocs).Path.Length + 1)
    $destPath = Join-Path $TargetDir $relativePath
    $destDir = Split-Path -Parent $destPath
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    Copy-Item -Path $file.FullName -Destination $destPath -Force
}

Write-Host ""
Write-Host "✅ 同步完成!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 当前 docs 目录内容:" -ForegroundColor Cyan
Get-ChildItem -Path $TargetDir -Recurse -File | Select-Object -First 20 | ForEach-Object {
    Write-Host "   $($_.FullName.Substring((Resolve-Path .).Path.Length + 1))"
}
