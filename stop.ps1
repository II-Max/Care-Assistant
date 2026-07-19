<#
.SYNOPSIS
Dừng tiến trình đang chiếm port 8001 (AI Service).

.DESCRIPTION
Tìm và tắt (kill) tiến trình (thường là python.exe / uvicorn) đang lắng nghe trên cổng 8001 để giải phóng cổng, chuẩn bị cho việc khởi động lại.
#>

$ErrorActionPreference = "SilentlyContinue"

Write-Host "Đang tìm tiến trình chiếm port 8001..." -ForegroundColor Cyan

# Tìm PID của tiến trình LISTENING trên port 8001
$listeningLine = (netstat -ano | Select-String ":8001" | Select-String "LISTENING")

if ($listeningLine) {
    # Lấy PID ở cuối chuỗi
    $pid_to_kill = $listeningLine.Line.Split(" ", [StringSplitOptions]::RemoveEmptyEntries)[-1]
    
    if ($pid_to_kill) {
        Write-Host "Phát hiện PID: $pid_to_kill đang chiếm port 8001. Tiến hành đóng..." -ForegroundColor Yellow
        taskkill /PID $pid_to_kill /F
        
        if ($?) {
            Write-Host "✅ Đã đóng thành công tiến trình $pid_to_kill. Port 8001 đã được giải phóng." -ForegroundColor Green
        } else {
            Write-Host "❌ Không thể đóng tiến trình. Bạn có thể cần chạy PowerShell với quyền Administrator." -ForegroundColor Red
        }
    }
} else {
    Write-Host "✅ Không có tiến trình nào đang chạy trên port 8001. Port đã trống." -ForegroundColor Green
}
