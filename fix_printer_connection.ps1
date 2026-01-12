# 打印机连接修复脚本 - 需要管理员权限运行
# 使用方法: 右键点击 -> 以管理员身份运行

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SHARP DX-2508NC PCL6 连接修复工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "警告: 需要管理员权限才能执行某些操作" -ForegroundColor Yellow
    Write-Host "建议: 右键点击此脚本，选择'以管理员身份运行'" -ForegroundColor Yellow
    Write-Host ""
}

# 1. 扫描网络查找打印机
Write-Host "[步骤1] 扫描网络查找打印机..." -ForegroundColor Yellow
$printerIP = "192.168.1.120"
$found = $false

# 测试打印机IP
$ping = Test-Connection -ComputerName $printerIP -Count 2 -Quiet -ErrorAction SilentlyContinue
if ($ping) {
    Write-Host "✓ 找到打印机: $printerIP" -ForegroundColor Green
    $found = $true
} else {
    Write-Host "✗ 无法连接到 $printerIP" -ForegroundColor Red
    Write-Host "  正在扫描192.168.1.x网段..." -ForegroundColor Yellow
    
    # 扫描常见IP范围
    $scanRange = 1..20
    $activeIPs = @()
    foreach ($i in $scanRange) {
        $testIP = "192.168.1.$i"
        $result = Test-Connection -ComputerName $testIP -Count 1 -Quiet -ErrorAction SilentlyContinue
        if ($result) {
            $activeIPs += $testIP
            Write-Host "  发现设备: $testIP" -ForegroundColor Green
        }
    }
    
    if ($activeIPs.Count -eq 0) {
        Write-Host "✗ 未发现任何活动设备" -ForegroundColor Red
    }
}

Write-Host ""

# 2. 检查网络接口
Write-Host "[步骤2] 检查网络接口..." -ForegroundColor Yellow
$ethernet = Get-NetAdapter | Where-Object {$_.InterfaceDescription -like "*Realtek*" -or $_.InterfaceDescription -like "*Ethernet*"} | Where-Object {$_.Status -eq 'Up'}
$wlan = Get-NetAdapter | Where-Object {$_.Name -like "*WLAN*"} | Where-Object {$_.Status -eq 'Up'}

if ($ethernet) {
    $ethIP = Get-NetIPAddress -InterfaceIndex $ethernet.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object {$_.IPAddress -like "192.168.1.*"}
    if ($ethIP) {
        Write-Host "✓ 以太网接口: $($ethernet.Name) - IP: $($ethIP.IPAddress)" -ForegroundColor Green
    } else {
        Write-Host "✗ 以太网接口未配置192.168.1.x IP" -ForegroundColor Red
    }
}

if ($wlan) {
    $wlanIP = Get-NetIPAddress -InterfaceIndex $wlan.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object {$_.IPAddress -like "192.168.3.*"}
    if ($wlanIP) {
        Write-Host "  WiFi接口: $($wlan.Name) - IP: $($wlanIP.IPAddress)" -ForegroundColor White
    }
}

Write-Host ""

# 3. 添加路由（如果需要）
if ($ethernet -and $isAdmin) {
    Write-Host "[步骤3] 配置网络路由..." -ForegroundColor Yellow
    try {
        $gateway = (Get-NetIPConfiguration -InterfaceIndex $ethernet.ifIndex).IPv4DefaultGateway.NextHop
        if (-not $gateway) {
            $gateway = "192.168.1.1"
        }
        
        # 检查路由是否存在
        $route = Get-NetRoute -DestinationPrefix "192.168.1.0/24" -ErrorAction SilentlyContinue
        if (-not $route) {
            New-NetRoute -DestinationPrefix "192.168.1.0/24" -InterfaceIndex $ethernet.ifIndex -NextHop $gateway -ErrorAction Stop
            Write-Host "✓ 已添加路由: 192.168.1.0/24 -> $gateway" -ForegroundColor Green
        } else {
            Write-Host "✓ 路由已存在" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ 添加路由失败: $_" -ForegroundColor Red
        Write-Host "  尝试使用route命令..." -ForegroundColor Yellow
        try {
            route add 192.168.1.0 mask 255.255.255.0 $gateway if $ethernet.ifIndex 2>$null
        } catch {}
    }
} elseif (-not $isAdmin) {
    Write-Host "  跳过路由配置（需要管理员权限）" -ForegroundColor Yellow
}

Write-Host ""

# 4. 清除打印队列
Write-Host "[步骤4] 清除打印队列..." -ForegroundColor Yellow
try {
    $jobs = Get-PrintJob -PrinterName "SHARP DX-2508NC PCL6" -ErrorAction SilentlyContinue
    if ($jobs) {
        foreach ($job in $jobs) {
            Remove-PrintJob -PrinterName "SHARP DX-2508NC PCL6" -ID $job.Id -ErrorAction SilentlyContinue
        }
        Write-Host "✓ 已清除 $($jobs.Count) 个打印任务" -ForegroundColor Green
    } else {
        Write-Host "✓ 打印队列为空" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ 清除失败: $_" -ForegroundColor Red
}

Write-Host ""

# 5. 重启打印服务
Write-Host "[步骤5] 重启打印服务..." -ForegroundColor Yellow
try {
    if ($isAdmin) {
        Restart-Service -Name Spooler -Force -ErrorAction Stop
        Start-Sleep -Seconds 2
        Write-Host "✓ 打印服务已重启" -ForegroundColor Green
    } else {
        Write-Host "  跳过（需要管理员权限）" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ 重启失败: $_" -ForegroundColor Red
}

Write-Host ""

# 6. 最终测试
Write-Host "[步骤6] 测试连接..." -ForegroundColor Yellow
$finalTest = Test-Connection -ComputerName $printerIP -Count 2 -Quiet -ErrorAction SilentlyContinue
if ($finalTest) {
    Write-Host "✓ 可以连接到打印机!" -ForegroundColor Green
    Write-Host ""
    Write-Host "建议下一步操作:" -ForegroundColor Yellow
    Write-Host "  1. 尝试打印测试页" -ForegroundColor White
    Write-Host "  2. 如果仍无法打印，检查打印机物理状态" -ForegroundColor White
} else {
    Write-Host "✗ 仍然无法连接到打印机" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因:" -ForegroundColor Yellow
    Write-Host "  1. 打印机未开机" -ForegroundColor White
    Write-Host "  2. 打印机IP地址已更改" -ForegroundColor White
    Write-Host "  3. 打印机和电脑不在同一物理网络" -ForegroundColor White
    Write-Host "  4. 防火墙阻止了连接" -ForegroundColor White
    Write-Host ""
    Write-Host "建议操作:" -ForegroundColor Yellow
    Write-Host "  1. 检查打印机是否开机" -ForegroundColor White
    Write-Host "  2. 在打印机上打印网络配置页，确认IP地址" -ForegroundColor White
    Write-Host "  3. 确认打印机和电脑连接到同一个路由器/交换机" -ForegroundColor White
    Write-Host "  4. 尝试重新添加打印机" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "修复完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

