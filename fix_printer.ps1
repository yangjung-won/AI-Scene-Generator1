# 打印机修复脚本 - SHARP DX-2508NC PCL6
# 问题：网络连接不通（电脑在192.168.3.x，打印机在192.168.1.x）

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "打印机修复工具 - SHARP DX-2508NC PCL6" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查网络连接
Write-Host "[1/5] 检查网络连接..." -ForegroundColor Yellow
$printerIP = "192.168.1.120"
$pingResult = Test-Connection -ComputerName $printerIP -Count 2 -Quiet

if ($pingResult) {
    Write-Host "✓ 可以连接到打印机 $printerIP" -ForegroundColor Green
} else {
    Write-Host "✗ 无法连接到打印机 $printerIP" -ForegroundColor Red
    Write-Host ""
    Write-Host "问题诊断：" -ForegroundColor Yellow
    Write-Host "  - 打印机IP: $printerIP (192.168.1.x网段)" -ForegroundColor White
    $wlanIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like "*WLAN*"}).IPAddress
    $ethernetIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like "*以太网*"}).IPAddress
    Write-Host "  - 当前WiFi IP: $wlanIP (192.168.3.x网段)" -ForegroundColor White
    Write-Host "  - 以太网 IP: $ethernetIP (192.168.1.x网段)" -ForegroundColor White
    Write-Host ""
    Write-Host "解决方案：" -ForegroundColor Yellow
    Write-Host "  1. 切换到以太网连接（推荐）" -ForegroundColor White
    Write-Host "  2. 或者检查路由器，确保两个网段可以互通" -ForegroundColor White
    Write-Host "  3. 或者重新配置打印机IP到当前网络" -ForegroundColor White
    Write-Host ""
}

# 2. 清除打印队列
Write-Host "[2/5] 清除打印队列..." -ForegroundColor Yellow
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
    Write-Host "✗ 清除打印队列时出错: $_" -ForegroundColor Red
}

# 3. 重启打印服务
Write-Host "[3/5] 重启打印服务..." -ForegroundColor Yellow
try {
    # 先停止相关进程
    Get-Process -Name spoolsv -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # 重启服务
    Restart-Service -Name Spooler -Force -ErrorAction Stop
    Start-Sleep -Seconds 2
    Write-Host "✓ 打印服务已重启" -ForegroundColor Green
} catch {
    Write-Host "✗ 无法重启打印服务（可能需要管理员权限）" -ForegroundColor Red
    Write-Host "  请以管理员身份运行此脚本" -ForegroundColor Yellow
}

# 4. 检查打印机状态
Write-Host "[4/5] 检查打印机状态..." -ForegroundColor Yellow
try {
    $printer = Get-Printer -Name "SHARP DX-2508NC PCL6" -ErrorAction Stop
    Write-Host "  打印机名称: $($printer.Name)" -ForegroundColor White
    Write-Host "  状态: $($printer.PrinterStatus)" -ForegroundColor White
    Write-Host "  端口: $($printer.PortName)" -ForegroundColor White
    Write-Host "  驱动: $($printer.DriverName)" -ForegroundColor White
    
    if ($printer.PrinterStatus -eq "Normal") {
        Write-Host "✓ 打印机状态正常" -ForegroundColor Green
    } else {
        Write-Host "✗ 打印机状态异常: $($printer.PrinterStatus)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 无法获取打印机信息: $_" -ForegroundColor Red
}

# 5. 测试打印端口
Write-Host "[5/5] 测试打印端口..." -ForegroundColor Yellow
$port = Get-PrinterPort -Name "*192.168.1.120*" -ErrorAction SilentlyContinue
if ($port) {
    Write-Host "  端口名称: $($port.Name)" -ForegroundColor White
    Write-Host "  打印机地址: $($port.PrinterHostAddress)" -ForegroundColor White
    Write-Host "  端口号: $($port.PortNumber)" -ForegroundColor White
    
    # 测试端口连接
    $portTest = Test-NetConnection -ComputerName $port.PrinterHostAddress -Port $port.PortNumber -WarningAction SilentlyContinue
    if ($portTest.TcpTestSucceeded) {
        Write-Host "✓ 端口连接成功" -ForegroundColor Green
    } else {
        Write-Host "✗ 端口连接失败" -ForegroundColor Red
    }
} else {
    Write-Host "✗ 未找到打印机端口配置" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "修复完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "如果仍然无法打印，请尝试：" -ForegroundColor Yellow
Write-Host "  1. 切换到以太网连接（如果可用）" -ForegroundColor White
Write-Host "  2. 检查打印机是否开机并连接到网络" -ForegroundColor White
Write-Host "  3. 在打印机上打印网络配置页，确认IP地址" -ForegroundColor White
Write-Host "  4. 重新添加打印机" -ForegroundColor White
Write-Host ""


























