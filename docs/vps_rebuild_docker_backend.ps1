# Rebuild Docker Backend - Fix 502 Error
# =======================================
# Rebuild và restart backend bằng Docker (nhanh hơn và ổn định hơn)

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
Write-Host "Rebuild Docker Backend - Fix 502 Error" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Why Docker is faster:" -ForegroundColor Yellow
Write-Host "  - Container already has dependencies" -ForegroundColor Gray
Write-Host "  - Faster restart (no Python module reload)" -ForegroundColor Gray
Write-Host "  - Automatic health checks" -ForegroundColor Gray
Write-Host "  - Better error handling" -ForegroundColor Gray
Write-Host ""

# 1. Stop existing nohup processes
Write-Host "Step 1: Stopping existing nohup backend processes..." -ForegroundColor Yellow
$stopNohup = Run-Plink "pkill -f 'uvicorn main:app.*port 8000' || echo 'No nohup process found'"
Write-Host $stopNohup
Start-Sleep -Seconds 2
Write-Host ""

# 2. Check if Docker is running
Write-Host "Step 2: Checking Docker status..." -ForegroundColor Yellow
$dockerStatus = Run-Plink "docker ps > /dev/null 2>&1 && echo 'Docker is running' || echo 'Docker is not running'"
Write-Host $dockerStatus
Write-Host ""

# 3. Check existing containers
Write-Host "Step 3: Checking existing containers..." -ForegroundColor Yellow
$existingContainers = Run-Plink "docker ps -a | grep econdata-backend || echo 'No econdata-backend container found'"
Write-Host $existingContainers
Write-Host ""

# 4. Navigate to project and stop existing container
Write-Host "Step 4: Stopping existing backend container..." -ForegroundColor Yellow
$stopContainer = Run-Plink "cd /opt/ecodata && docker-compose -f docker-compose.production.yml stop backend 2>&1 || docker stop econdata-backend 2>&1 || echo 'No container to stop'"
Write-Host $stopContainer
Write-Host ""

# 5. Remove old container
Write-Host "Step 5: Removing old container..." -ForegroundColor Yellow
$removeContainer = Run-Plink "cd /opt/ecodata && docker-compose -f docker-compose.production.yml rm -f backend 2>&1 || docker rm -f econdata-backend 2>&1 || echo 'No container to remove'"
Write-Host $removeContainer
Write-Host ""

# 6. Pull latest code (if needed)
Write-Host "Step 6: Pulling latest code..." -ForegroundColor Yellow
$pullCode = Run-Plink "cd /opt/ecodata && git checkout dev && git pull origin dev 2>&1 | tail -5"
Write-Host $pullCode
Write-Host ""

# 7. Build Docker image (with cache for speed)
Write-Host "Step 7: Building Docker image (this may take 2-3 minutes)..." -ForegroundColor Yellow
Write-Host "  Using cache for faster build..." -ForegroundColor Gray
$buildImage = Run-Plink "cd /opt/ecodata && docker-compose -f docker-compose.production.yml build backend 2>&1 | tail -20"
Write-Host $buildImage
Write-Host ""

# 8. Start backend container
Write-Host "Step 8: Starting backend container..." -ForegroundColor Yellow
$startContainer = Run-Plink "cd /opt/ecodata && docker-compose -f docker-compose.production.yml up -d backend 2>&1"
Write-Host $startContainer
Start-Sleep -Seconds 5
Write-Host ""

# 9. Check container status
Write-Host "Step 9: Checking container status..." -ForegroundColor Yellow
$containerStatus = Run-Plink "docker ps | grep econdata-backend || docker-compose -f docker-compose.production.yml ps backend"
Write-Host $containerStatus
Write-Host ""

# 10. Wait for health check
Write-Host "Step 10: Waiting for health check (max 40 seconds)..." -ForegroundColor Yellow
$maxWait = 40
$waited = 0
$healthy = $false
while ($waited -lt $maxWait -and -not $healthy) {
    Start-Sleep -Seconds 5
    $waited += 5
    $healthCheck = Run-Plink "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>&1"
    if ($healthCheck -match "200") {
        $healthy = $true
        Write-Host "  Backend is healthy (HTTP 200) after $waited seconds" -ForegroundColor Green
    } else {
        Write-Host "  Waiting... ($waited/$maxWait seconds) - Status: $healthCheck" -ForegroundColor Gray
    }
}
if (-not $healthy) {
    Write-Host "  Warning: Health check timeout" -ForegroundColor Yellow
}
Write-Host ""

# 11. Check container logs
Write-Host "Step 11: Checking container logs (last 20 lines)..." -ForegroundColor Yellow
$containerLogs = Run-Plink "docker logs econdata-backend --tail 20 2>&1 || docker-compose -f docker-compose.production.yml logs backend --tail 20"
Write-Host $containerLogs
Write-Host ""

# 12. Test from external
Write-Host "Step 12: Testing from external..." -ForegroundColor Yellow
try {
    $externalTest = Invoke-WebRequest -Uri "https://ecodata.khoviet.com/health" -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue
    if ($externalTest.StatusCode -eq 200) {
        Write-Host "  External health check: HTTP 200 (SUCCESS)" -ForegroundColor Green
    } else {
        Write-Host "  External health check: HTTP $($externalTest.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  External health check failed: $_" -ForegroundColor Red
}
Write-Host ""

# 13. Test login endpoint
Write-Host "Step 13: Testing login endpoint..." -ForegroundColor Yellow
try {
    $loginTest = Invoke-WebRequest -Uri "https://ecodata.khoviet.com/auth/login" -Method POST -Body (@{email="test@example.com";password="test"} | ConvertTo-Json) -ContentType "application/json" -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue
    if ($loginTest.StatusCode -eq 401 -or $loginTest.StatusCode -eq 422) {
        Write-Host "  Login endpoint: HTTP $($loginTest.StatusCode) (Endpoint is working)" -ForegroundColor Green
    } else {
        Write-Host "  Login endpoint: HTTP $($loginTest.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Login endpoint test: $_" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Rebuild Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Monitor container:" -ForegroundColor Yellow
Write-Host "  ssh root@$VPS_IP 'docker logs -f econdata-backend'" -ForegroundColor Gray
Write-Host ""
Write-Host "Check container status:" -ForegroundColor Yellow
Write-Host "  ssh root@$VPS_IP 'docker ps | grep econdata-backend'" -ForegroundColor Gray
Write-Host ""
Write-Host "Restart container:" -ForegroundColor Yellow
Write-Host "  ssh root@$VPS_IP 'cd /opt/ecodata && docker-compose -f docker-compose.production.yml restart backend'" -ForegroundColor Gray
Write-Host ""

