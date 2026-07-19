<#
.SYNOPSIS
Khởi động hệ thống AI Customer Care Assistant (Bệnh viện Tim Hà Nội).

Phase 3: Booking, Handoff, Database, Departments.

.DESCRIPTION
Script cài đặt dependencies và khởi động FastAPI AI Service (port 8001).
Service phục vụ cả REST API lẫn frontend static files.
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
Write-Host "👉 Website:         http://localhost:8001" -ForegroundColor White
Write-Host "👉 Chat AI:         http://localhost:8001/ai-chat" -ForegroundColor White
Write-Host "👉 Đặt lịch:        http://localhost:8001/booking" -ForegroundColor White
Write-Host "👉 Tra cứu lịch:    http://localhost:8001/booking-history" -ForegroundColor White
Write-Host "👉 Dashboard NV:    http://localhost:8001/staff-dashboard" -ForegroundColor White
Write-Host "👉 API Docs:        http://localhost:8001/docs" -ForegroundColor White

Set-Location "$ProjectPath\ai-service"
$env:PYTHONIOENCODING="utf-8"
python main.py
