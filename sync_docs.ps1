# sync_docs.ps1
# 从 GitHub 原项目同步设计稿到本项目的 docs/ 目录
# 用法: .\sync_docs.ps1 [-Repo "owner/repo"] [-Branch "main"] [-KeepTemp]

param(
    [string]$Repo = "ITJacob/CardGame",
    [string]$Branch = "main",
    [string]$SubDir = "docs"
)

$ErrorActionPreference = "Stop"
$TargetDir = Join-Path $PSScriptRoot "docs"
$TempDir = Join-Path $env:TEMP ("cardgame-docs-" + [guid]::NewGuid().ToString("N"))

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  设计稿同步工具 (GitHub)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 源仓库: https://github.com/$Repo ($Branch/$SubDir)" -ForegroundColor Green
Write-Host "📂 同步目标: $TargetDir" -ForegroundColor Green
Write-Host ""

try {
    # 稀疏克隆，只拉取 docs 目录
    Write-Host "🔄 正在从 GitHub 拉取..." -ForegroundColor Cyan
    git clone --depth 1 --filter=blob:none --sparse --branch $Branch "https://github.com/$Repo.git" $TempDir
    if ($LASTEXITCODE -ne 0) { throw "git clone 失败，请检查网络与仓库名" }

    Push-Location $TempDir
    git sparse-checkout set $SubDir
    Pop-Location

    $SourceDocs = Join-Path $TempDir $SubDir
    if (-not (Test-Path $SourceDocs)) { throw "仓库中未找到 $SubDir 目录" }

    # 清空并复制（docs 为只读镜像，与源保持一致）
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
    Get-ChildItem -Path $TargetDir -Exclude ".gitkeep" | Remove-Item -Recurse -Force
    Copy-Item -Path "$SourceDocs\*" -Destination $TargetDir -Recurse -Force

    Write-Host ""
    Write-Host "✅ 同步完成!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 当前 docs 目录内容:" -ForegroundColor Cyan
    Get-ChildItem -Path $TargetDir -Recurse -File | Select-Object -First 20 | ForEach-Object {
        Write-Host "   $($_.FullName.Substring($TargetDir.Length + 1))"
    }
}
finally {
    if (Test-Path $TempDir) { Remove-Item -Recurse -Force $TempDir }
}
