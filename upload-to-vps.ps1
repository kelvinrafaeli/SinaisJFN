# Script PowerShell para enviar arquivos para VPS
# Execute: .\upload-to-vps.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$VpsUser,
    
    [Parameter(Mandatory=$true)]
    [string]$VpsIP,
    
    [Parameter(Mandatory=$false)]
    [string]$VpsPath = "/home/$VpsUser/sinaisjfn"
)

Write-Host "🚀 Enviando arquivos para VPS..." -ForegroundColor Green
Write-Host "Destino: $VpsUser@$VpsIP`:$VpsPath" -ForegroundColor Yellow

# Verificar se tem SCP/SSH disponível
try {
    scp --version | Out-Null
} catch {
    Write-Host "❌ SCP não encontrado! Instale o OpenSSH." -ForegroundColor Red
    Write-Host "Execute: Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0" -ForegroundColor Yellow
    exit 1
}

# Criar pasta na VPS
Write-Host "`n📁 Criando pasta na VPS..." -ForegroundColor Yellow
ssh "$VpsUser@$VpsIP" "mkdir -p $VpsPath"

# Lista de arquivos para enviar
$files = @(
    "main.py",
    "indicator.py",
    "trading.py",
    "telegram_bot.py",
    ".env",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    ".dockerignore",
    "nginx.conf",
    "deploy.sh",
    "static"
)

Write-Host "`n⚠️  IMPORTANTE: Certifique-se de que o arquivo .env está configurado corretamente!" -ForegroundColor Yellow
Write-Host "Pressione ENTER para continuar ou CTRL+C para cancelar..." -ForegroundColor Cyan
Read-Host

# Enviar arquivos
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "📤 Enviando $file..." -ForegroundColor Cyan
        if ((Get-Item $file) -is [System.IO.DirectoryInfo]) {
            scp -r "$file" "${VpsUser}@${VpsIP}:${VpsPath}/"
        } else {
            scp "$file" "${VpsUser}@${VpsIP}:${VpsPath}/"
        }
    } else {
        Write-Host "⚠️  $file não encontrado, pulando..." -ForegroundColor Yellow
    }
}

Write-Host "`n✅ Upload concluído!" -ForegroundColor Green
Write-Host "`n🔧 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Conecte na VPS: ssh $VpsUser@$VpsIP"
Write-Host "2. Entre na pasta: cd $VpsPath"
Write-Host "3. Execute: chmod +x deploy.sh && ./deploy.sh"
Write-Host "`nOu execute manualmente:"
Write-Host "docker-compose up -d --build"
