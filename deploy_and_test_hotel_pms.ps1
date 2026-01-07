<# 
    Deploy + Nginx Fix + Test for Hotel PMS
    =======================================
    - Tự động đăng nhập VPS bằng PuTTY Plink (giống deploy_hotel_pms.ps1)
    - Triển khai Docker stack Hotel PMS (backend 8002, Postgres 5434, frontend 8003)
    - Áp dụng cấu hình Nginx cho hotel.khoviet.com (không đụng ECONAI/ECODATA)
    - Test HTTP/HTTPS từ cả VPS (curl) và máy local (Invoke-WebRequest)
#>

param(
    [string]$VPS_IP = "212.85.24.158",
    [string]$VPS_USER = "root",
    [string]$VPS_PASSWORD = "EcoData2025VPS@Secure-Pass123",
    [string]$PLINK_PATH = "C:\Program Files\PuTTY\plink.exe"
)

$hostkey = "ssh-ed25519 255 SHA256:WCIu/MntsW6iVVem37UoYsMM8APL+/MQYe6vtbTmt2g"

function Run-Plink {
    param([string]$Command)
    $fullCmd = "`"$PLINK_PATH`" -hostkey `"$hostkey`" -ssh -pw `"$VPS_PASSWORD`" -batch ${VPS_USER}@${VPS_IP} `"$Command`""
    cmd /c $fullCmd 2>&1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Hotel PMS - Deploy + Nginx Fix + Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "VPS: $VPS_USER@$VPS_IP" -ForegroundColor Yellow
Write-Host "Project: /opt/hotel (Docker: backend 8002, frontend 8003, Postgres 5434)" -ForegroundColor Yellow
Write-Host ""

# 1. Deploy/update Docker stack (reuse existing deploy script)
Write-Host "Step 1: Deploying Hotel PMS Docker stack on VPS..." -ForegroundColor Yellow

$deployScript = Join-Path $PSScriptRoot "deploy_hotel_pms.ps1"
if (-not (Test-Path $deployScript)) {
    Write-Host "ERROR: deploy_hotel_pms.ps1 not found in $PSScriptRoot" -ForegroundColor Red
    exit 1
}

$deployArgs = @{
    VPS_IP      = $VPS_IP
    VPS_USER    = $VPS_USER
    VPS_PASSWORD = $VPS_PASSWORD
    PLINK_PATH  = $PLINK_PATH
}

& $deployScript @deployArgs
Write-Host ""

# 2. Áp dụng cấu hình Nginx riêng cho hotel.khoviet.com (không ảnh hưởng ECONAI/ECODATA)
Write-Host "Step 2: Applying dedicated Nginx vhost for hotel.khoviet.com..." -ForegroundColor Yellow

$nginxScript = Join-Path $PSScriptRoot "fix_nginx_conflict.ps1"
if (-not (Test-Path $nginxScript)) {
    Write-Host "ERROR: fix_nginx_conflict.ps1 not found in $PSScriptRoot" -ForegroundColor Red
    exit 1
}

& $nginxScript @deployArgs
Write-Host ""

# 3. Kiểm tra stack Docker trên VPS (đảm bảo không đụng ECONAI/ECODATA)
Write-Host "Step 3: Verifying Docker containers for Hotel PMS..." -ForegroundColor Yellow
$dockerStatus = Run-Plink "cd /opt/hotel && docker-compose -f docker-compose.production.yml ps 2>&1"
Write-Host $dockerStatus
Write-Host ""

# 4. Health check backend Hotel PMS trên VPS (port 8002)
Write-Host "Step 4: Backend health check on VPS (http://localhost:8002/health)..." -ForegroundColor Yellow
$maxWait = 60
$waited = 0
$healthy = $false
while ($waited -lt $maxWait -and -not $healthy) {
    Start-Sleep -Seconds 5
    $waited += 5
    $healthCheck = Run-Plink "curl -s -o /dev/null -w '%{http_code}' http://localhost:8002/health 2>&1"
    if ($healthCheck -match "200") {
        $healthy = $true
        Write-Host "  Backend is healthy (HTTP 200) after $waited seconds." -ForegroundColor Green
    } else {
        Write-Host "  Waiting... ($waited/$maxWait seconds) - Status: $healthCheck" -ForegroundColor Gray
    }
}
if (-not $healthy) {
    Write-Host "WARNING: Backend health check did not return 200 within $maxWait seconds." -ForegroundColor Yellow
}
Write-Host ""

# 5. Test HTTP→HTTPS redirect và nội dung trên VPS
Write-Host "Step 5: Testing Nginx routing for hotel.khoviet.com on VPS..." -ForegroundColor Yellow

Write-Host "  5.1 HTTP (port 80) with Host header -> expect 301 to https://hotel.khoviet.com/ ..." -ForegroundColor Gray
$httpCheck = Run-Plink "curl -I -H 'Host: hotel.khoviet.com' http://127.0.0.1:80 2>&1 | head -n 5"
Write-Host $httpCheck
Write-Host ""

Write-Host "  5.2 HTTPS (port 443) -> expect 200/304 and Hotel PMS HTML..." -ForegroundColor Gray
$httpsHeaders = Run-Plink "curl -k -I https://hotel.khoviet.com 2>&1 | head -n 10"
Write-Host $httpsHeaders
Write-Host ""

Write-Host "  5.3 Content sniff (grep 'Hotel PMS' to distinguish from ECODATA/ECONAI)..." -ForegroundColor Gray
$httpsBodyCheck = Run-Plink "curl -k -s https://hotel.khoviet.com | head -n 80 | grep -i 'Hotel PMS' && echo 'BODY_MATCH_HOTEL' || echo 'BODY_NO_MATCH'"
Write-Host $httpsBodyCheck
Write-Host ""

# 6. External test từ máy Windows (Invoke-WebRequest)
Write-Host "Step 6: External HTTPS test from this machine..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://hotel.khoviet.com/" -UseBasicParsing -TimeoutSec 15 -ErrorAction Stop
    Write-Host ("  Status: HTTP {0}" -f $response.StatusCode) -ForegroundColor Green
    if ($response.Content -match "Hotel PMS") {
        Write-Host "  Content contains 'Hotel PMS' (likely correct frontend)." -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Content does not clearly contain 'Hotel PMS'. Please verify UI manually in browser." -ForegroundColor Yellow
    }
} catch {
    Write-Host "  External HTTPS request failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploy + Nginx Fix + Test completed for hotel.khoviet.com" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""


