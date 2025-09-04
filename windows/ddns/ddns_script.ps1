# Set your parameters
$zoneID  = "aa74dad45c4d4c169ec254ce87bf3300"
$recordID = "7a30e934fd12ca799f328b323be6d303"
$token    = "vctyl8uRT7hKucDdK0sSuo5VMBisCoplaPpegpTM"
$dnsName  = "evanwu1314.ddns-ip.net"

# Get current public IP
$currentIP = (Invoke-RestMethod -Uri "https://api.ipify.org?format=json").ip

# Update the DNS record in Cloudflare
$updateResult = Invoke-RestMethod -Method PUT `
  -Uri "https://api.cloudflare.com/client/v4/zones/$zoneID/dns_records/$recordID" `
  -Headers @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
  } `
  -Body (@{
    type    = "A"
    name    = $dnsName
    content = $currentIP
    ttl     = 1
    proxied = $false
  } | ConvertTo-Json -Depth 10)

# Display the result
if ($updateResult.success) {
  Write-Host " IP update successful: $currentIP" -ForegroundColor Green
} else {
  Write-Host " Update failed!" -ForegroundColor Red
  $updateResult
}
