[Setup]
AppName=YouTube Downloader Pro
AppVersion=1.0
DefaultDirName={autopf}\YoutubeDownloader
DefaultGroupName=Youtube Downloader
UninstallDisplayIcon={app}\YoutubeDownloader.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=YoutubeDownloaderSetup
SetupIconFile=app_icon.ico

[Files]
Source: "dist\YoutubeDownloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\YouTube Downloader"; Filename: "{app}\YoutubeDownloader.exe"; IconFilename: "{app}\app_icon.ico"
Name: "{autodesktop}\YouTube Downloader"; Filename: "{app}\YoutubeDownloader.exe"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
