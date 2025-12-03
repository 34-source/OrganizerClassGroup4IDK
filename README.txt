This python code will organize a folder based on the type of files found within. Like files (e.g. text documents, videos, pictures) will be sorted into subfolders. Logs will be kept of each sort, and an undo option will be included in the menu.

To download and install, run:

$repoUrl = "https://raw.githubusercontent.com/34-source/OrganizerClassGroup4IDK/refs/heads/main/Organizer.py?token=GHSAT0AAAAAADQPVJFFWPVVJWNFGANTWAOQ2JPH2AQ"
$downloadPath = "$env:USERPROFILE\Desktop\organizer.py"
Invoke-WebRequest $repoUrl -OutFile $downloadPath
Write-Host "Organizer downloaded to: $downloadPath"

And then,

python "$env:USERPROFILE\Desktop\organizer.py"
