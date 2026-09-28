# 设置编译环境变量
$version = "0.0.1"
$env:GOOS = "linux"
#$env:GOOS = "windows"
$env:GOARCH = "amd64"
$env:CGO_ENABLED = "0"

# 记录开始时间
$startTime = Get-Date
Write-Host "开始构建: $startTime" -ForegroundColor Green

# 执行编译
go build -tags=go_json -trimpath -ldflags="-s -w -extldflags '-static'" -o "release/main-$version"

# 记录结束时间
$endTime = Get-Date
$duration = $endTime - $startTime

# 输出编译信息
Write-Host "构建完成: $endTime" -ForegroundColor Green
Write-Host "构建耗时: $($duration.TotalSeconds.ToString('F2') ) 秒" -ForegroundColor Yellow

# 显示生成的文件信息
if (Test-Path "release/main")
{
    $fileInfo = Get-Item "release/main"
    $fileSize = [math]::Round($fileInfo.Length / 1MB, 2)
    Write-Host "生成文件: release/main" -ForegroundColor Cyan
    Write-Host "文件大小: $fileSize MB" -ForegroundColor Cyan
}
else
{
    Write-Host "警告: 未找到生成的文件" -ForegroundColor Red
}