# Fix Nginx Routing Conflict - Final
# ====================================

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
Write-Host "Applying Strict Nginx Config for hotel.khoviet.com" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Kiểm tra chứng chỉ SSL cho hotel.khoviet.com
Write-Host "Step 1: Checking SSL certificates on VPS..." -ForegroundColor Yellow
$certCheck = Run-Plink "test -f /etc/letsencrypt/live/hotel.khoviet.com/fullchain.pem && test -f /etc/letsencrypt/live/hotel.khoviet.com/privkey.pem && echo 'CERT_OK' || echo 'CERT_MISSING'"
if ($certCheck -notmatch "CERT_OK") {
    Write-Host "ERROR: SSL certificates for hotel.khoviet.com are missing on VPS." -ForegroundColor Red
    Write-Host "Hint: Run setup_vps_ssl.ps1 first to issue Let's Encrypt certificate for hotel.khoviet.com." -ForegroundColor Yellow
    exit 1
}
Write-Host "  SSL certificates found." -ForegroundColor Green
Write-Host ""

# 2. Nội dung file Nginx cho hotel.khoviet.com (single-quoted here-string để tránh lỗi escape)
$nginxConfig = @'
server {
    listen 80;
    server_name hotel.khoviet.com;
    return 301 https://hotel.khoviet.com$request_uri;
}

server {
    listen 443 ssl;
    server_name hotel.khoviet.com;

    ssl_certificate /etc/letsencrypt/live/hotel.khoviet.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hotel.khoviet.com/privkey.pem;

    ssl_session_cache shared:le_nginx_SSL:10m;
    ssl_session_timeout 1440m;
    ssl_session_tickets off;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;

    location / {
        proxy_pass http://127.0.0.1:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
'@

# 3. Ghi file config và reload Nginx chỉ cho hotel.khoviet.com
Write-Host "Step 2: Writing Nginx vhost and reloading..." -ForegroundColor Yellow

$remoteCommand = @"
cat > /etc/nginx/sites-available/hotel.khoviet.com << 'EOF'
$nginxConfig
EOF
ln -s -f /etc/nginx/sites-available/hotel.khoviet.com /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
"@

$applyOutput = Run-Plink $remoteCommand
Write-Host $applyOutput

if ($applyOutput -match "test failed" -or $applyOutput -match "nginx: \[emerg\]") {
    Write-Host "ERROR: nginx -t reported an error. Please SSH to VPS and check nginx configuration." -ForegroundColor Red
    exit 1
}

Write-Host "  Nginx vhost for hotel.khoviet.com applied successfully." -ForegroundColor Green
Write-Host ""

# 4. Verify từ VPS: HTTP → HTTPS
Write-Host "Step 3: Verifying HTTP redirect and HTTPS response..." -ForegroundColor Yellow
$checkHttp = Run-Plink "curl -I -H 'Host: hotel.khoviet.com' http://127.0.0.1:80 2>&1 | head -n 5"
Write-Host "---- curl -I http://127.0.0.1:80 (Host: hotel.khoviet.com) ----" -ForegroundColor Gray
Write-Host $checkHttp
Write-Host ""

$checkHttps = Run-Plink "curl -k -I https://hotel.khoviet.com 2>&1 | head -n 10"
Write-Host "---- curl -I https://hotel.khoviet.com ----" -ForegroundColor Gray
Write-Host $checkHttps
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Done." -ForegroundColor Cyan
