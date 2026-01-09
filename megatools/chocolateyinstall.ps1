$ErrorActionPreference = 'Stop';
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url        = 'https://megatools.megous.com/builds/builds/megatools-1.11.3.20250401-win32.zip'
$url64      = 'https://megatools.megous.com/builds/builds/megatools-1.11.3.20250401-win64.zip'

$Arguments = @{
	PackageName = "megatools"
    Url = $url
    Checksum = "6EA5C83E67B9E2D100F45B0A9AAF5E35610930E069340C0B915170CFBC9F52F0"
    ChecksumType = "sha256"
    Url64 = $url64
    Checksum64 = "AEB69783078FD37CE1C51D4E4760D6584FFBD410B291536B64EDCCF6B424A61B"
    ChecksumType64 = "sha256"
    UnzipLocation = $toolsDir
}

Install-ChocolateyZipPackage @Arguments