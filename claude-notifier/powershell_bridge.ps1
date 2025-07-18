# PowerShell bridge to send status to tray app
param($Status)

try {
    $client = New-Object System.Net.Sockets.TcpClient
    $client.Connect("127.0.0.1", 12345)
    $stream = $client.GetStream()
    $writer = New-Object System.IO.StreamWriter($stream)
    $writer.Write($Status)
    $writer.Flush()
    $client.Close()
    Write-Host "Status sent: $Status"
} catch {
    Write-Host "Failed to send status: $_"
}