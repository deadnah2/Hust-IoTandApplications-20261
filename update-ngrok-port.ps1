# Script tự động: Chạy ngrok tcp 1883 và update MQTT port vào các file ESP32 simulator
# Usage: .\update-ngrok-port.ps1
# Script sẽ tự chạy ngrok, lấy port, update files

$files = @(
    "ESP32-Fan\src\main.cpp",
    "ESP32-Sensor\src\main.cpp"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Kiểm tra ngrok đã cài chưa
if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ngrok not found! Please install ngrok first." -ForegroundColor Red
    Write-Host "   Download: https://ngrok.com/download" -ForegroundColor Gray
    exit 1
}

# Kill ngrok cũ nếu đang chạy
$existingNgrok = Get-Process ngrok -ErrorAction SilentlyContinue
if ($existingNgrok) {
    Write-Host "Stopping existing ngrok process..." -ForegroundColor Yellow
    Stop-Process -Name ngrok -Force
    Start-Sleep -Seconds 1
}

# Chạy ngrok trong background
Write-Host "Starting ngrok tcp 1883..." -ForegroundColor Cyan
Start-Process ngrok -ArgumentList "tcp 1883" -WindowStyle Minimized

# Chờ ngrok khởi động
Write-Host "Waiting for ngrok to start..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Lấy port từ ngrok API
$maxRetries = 5
$port = $null

for ($i = 1; $i -le $maxRetries; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method Get -ErrorAction Stop
        $publicUrl = $response.tunnels[0].public_url
        
        # Parse port từ URL: tcp://0.tcp.ap.ngrok.io:14567
        if ($publicUrl -match ':(\d+)$') {
            $port = $matches[1]
            break
        }
    } catch {
        Write-Host "   Retry $i/$maxRetries..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $port) {
    Write-Host "Failed to get port from ngrok API!" -ForegroundColor Red
    Write-Host "Make sure ngrok is running and try again." -ForegroundColor Gray
    exit 1
}

Write-Host "Got ngrok port: $port" -ForegroundColor Green
Write-Host ""

# Update files
Write-Host "Updating MQTT_PORT in ESP32 files..." -ForegroundColor Cyan

foreach ($file in $files) {
    $filePath = Join-Path $scriptDir $file
    
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw
        
        # Replace MQTT_PORT value using regex
        $newContent = $content -replace 'const int MQTT_PORT = \d+;', "const int MQTT_PORT = $port;"
        
        Set-Content $filePath $newContent -NoNewline
        Write-Host "   $file" -ForegroundColor Green
    } else {
        Write-Host "   Not found: $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Done!" -ForegroundColor Yellow
Write-Host "   ngrok URL: tcp://0.tcp.ap.ngrok.io:$port" -ForegroundColor White
Write-Host "   MQTT_PORT: $port" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Gray
Write-Host "   1. Restart Wokwi simulations (Fan, Sensor)" -ForegroundColor Gray
Write-Host "   2. ngrok is running in background (minimized)" -ForegroundColor Gray
Write-Host "   3. To stop ngrok: Stop-Process -Name ngrok" -ForegroundColor Gray
