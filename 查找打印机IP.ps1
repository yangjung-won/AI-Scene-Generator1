# 查找打印机实际IP地址的脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "查找 SHARP 打印机IP地址" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 从ARP表获取的设备
Write-Host "发现192.168.1.x网段的设备:" -ForegroundColor Yellow
$devices = @(
    @{IP="192.168.1.187"; MAC="7c-10-c9-44-11-de"},
    @{IP="192.168.1.211"; MAC="f4-f1-9e-1a-55-c8"}
)

foreach ($device in $devices) {
    Write-Host "  测试设备: $($device.IP) (MAC: $($device.MAC))" -ForegroundColor White
    
    # 测试常见打印端口
    $ports = @(515, 9100, 631, 80)
    $foundPorts = @()
    
    foreach ($port in $ports) {
        $test = Test-NetConnection -ComputerName $device.IP -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        if ($test) {
            $foundPorts += $port
        }
    }
    
    if ($foundPorts.Count -gt 0) {
        Write-Host "    ✓ 发现开放端口: $($foundPorts -join ', ')" -ForegroundColor Green
        if ($foundPorts -contains 515 -or $foundPorts -contains 9100) {
            Write-Host "    ⚠ 可能是打印机！" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "建议操作:" -ForegroundColor Cyan
            Write-Host "  1. 更新打印机端口到: $($device.IP)" -ForegroundColor White
            Write-Host "  2. 运行以下命令:" -ForegroundColor White
            Write-Host "     Set-Printer -Name 'SHARP DX-2508NC PCL6' -PortName '$($device.IP)'" -ForegroundColor Green
        }
    } else {
        Write-Host "    ✗ 未发现打印端口" -ForegroundColor Gray
    }
    Write-Host ""
}

# 尝试通过SNMP或HTTP识别设备
Write-Host "尝试识别设备类型..." -ForegroundColor Yellow
foreach ($device in $devices) {
    try {
        # 尝试HTTP连接
        $http = Invoke-WebRequest -Uri "http://$($device.IP)" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($http) {
            Write-Host "  $($device.IP): HTTP响应 - $($http.StatusCode)" -ForegroundColor Green
            if ($http.Content -like "*SHARP*" -or $http.Content -like "*printer*") {
                Write-Host "    ⚠ 可能是SHARP打印机！" -ForegroundColor Yellow
            }
        }
    } catch {
        # HTTP失败，继续
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "如果找到打印机，请更新端口配置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

