<#
.SYNOPSIS
Khởi động hệ thống AI Customer Care Assistant (Bệnh viện Tim Hà Nội).

.DESCRIPTION
Script này sẽ cài đặt các dependencies (nếu cần) và khởi động FastAPI AI Service (port 8001).
#>

$ErrorActionPreference = "Stop"
$ProjectPath = $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " 🏥 AI Customer Care Assistant - Bệnh viện Tim Hà Nội " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Kiểm tra file .env
if (-not (Test-Path "$ProjectPath\.env")) {
    Write-Host "⚠️ Không tìm thấy file .env!" -ForegroundColor Yellow
    Write-Host "Vui lòng copy từ .env.example sang .env và cấu hình NVIDIA_API_KEY." -ForegroundColor Yellow
    exit 1
}

# 1. Cài đặt Python Dependencies
Write-Host "`n[1/2] Đang kiểm tra và cài đặt dependencies..." -ForegroundColor Green
try {
    # Cài đặt AI Service requirements
    pip install -r "$ProjectPath\ai-service\requirements.txt" --quiet
    Write-Host "✅ Dependencies đã sẵn sàng." -ForegroundColor Green
}
catch {
    Write-Host "❌ Lỗi khi cài đặt dependencies: $_" -ForegroundColor Red
    exit 1
}

# 2. Khởi động ứng dụng hợp nhất
Write-Host "`n[2/2] Khởi động website và AI API trên port 8001..." -ForegroundColor Green
Write-Host "👉 Website: http://localhost:8001" -ForegroundColor White
Write-Host "👉 API Docs: http://localhost:8001/docs" -ForegroundColor White

Set-Location "$ProjectPath\ai-service"
$env:PYTHONIOENCODING="utf-8"
python main.py
