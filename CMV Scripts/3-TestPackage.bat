@echo off

echo This would remove any local changes in this system
:PROMPT
SET /P AREYOUSURE=Are you sure (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END

echo start pythonsv download
mkdir C:\Source

cd C:\Source
git init
git pull https://gitlab.devtools.intel.com/pgm_gfx_system/pvc-system-test

mklink /J C:\STHI\Fusion\PythonScripts C:\Source\PythonScripts
mklink /J C:\STHI\ConfigFiles C:\Source\STHI\ConfigFiles

if not exist p: (net use p: \\amr\ec\proj\MPV\fm_mpv\Dev\Ops\Products\PVC)

echo This would update FAS with WA for the executiondata collection issue

SET /P AREYOUSURE=Are you sure (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END

copy C:\Source\Tools\FASWorkaround\ExecutionData.py C:\Python36\Lib\site-packages\FAS\ExecutionData.py

:END