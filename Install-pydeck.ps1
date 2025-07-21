# === Настройки ===
$LogFile = "install_pydeck_log.txt"
$PackageName = "pydeck"
$MaxRetries = 3
$Timeout = 100

# === Функция логирования ===
Function Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp`t$Message" | Out-File -FilePath $LogFile -Append
    Write-Host $Message
}

# === Проверка установки пакета ===
Function Check-PackageInstalled {
    $installed = & "$($env:VIRTUAL_ENV)\Scripts\pip.exe" list | Select-String "^$PackageName\s"
    if ($installed) {
        Write-Host "✅ $PackageName найден"
        return $true
    } else {
        Write-Host "❌ $PackageName не найден"
        return $false
    }
}

# === Обновление pip ===
Function Ensure-PipUpToDate {
    Log "🔄 Обновление pip до последней версии..."
    & "$($env:VIRTUAL_ENV)\Scripts\python.exe" -m pip install --upgrade pip --timeout $Timeout
    Log "✅ pip обновлён"
}

# === Установка пакета с повторными попытками ===
Function Install-Package {
    param([int]$Attempt)
    Log "🚀 Попытка #$Attempt установки $PackageName..."
    try {
        & "$($env:VIRTUAL_ENV)\Scripts\pip.exe" install $PackageName --timeout $Timeout
        if ($LASTEXITCODE -eq 0) {
            Log "✅ $PackageName успешно установлен"
            return $true
        } else {
            Log "❌ Установка завершилась с кодом $LASTEXITCODE"
        }
    } catch {
        Log "⚠️ Ошибка: $_"
    }
    return $false
}

# === Главный блок ===
Log "📦 Старт установки $PackageName"
Ensure-PipUpToDate

if (-not (Check-PackageInstalled)) {
    for ($i = 1; $i -le $MaxRetries; $i++) {
        if (Install-Package -Attempt $i) {
            break
        } else {
            Log "⏳ Ожидание 10 секунд перед повтором..."
            Start-Sleep -Seconds 10
        }
    }
} else {
    Log "✅ $PackageName уже установлен, установка не требуется"
}
Log "Скрипт завершён."