To download and install, run:

$repoUrl = "https://raw.githubusercontent.com/34-source/OrganizerClassGroup4IDK/refs/heads/main/Organizer.py?token=GHSAT0AAAAAADQPVJFFWPVVJWNFGANTWAOQ2JPH2AQ"
$downloadPath = "$env:USERPROFILE\Desktop\organizer.py"
Invoke-WebRequest $repoUrl -OutFile $downloadPath
Write-Host "Organizer downloaded to: $downloadPath"

And then,

python "$env:USERPROFILE\Desktop\organizer.py"
