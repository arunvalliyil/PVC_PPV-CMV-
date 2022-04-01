

echo start pythonsv download
mkdir C:\PythonSV
mkdir C:\PythonSV\pontevecchio
mkdir C:\PythonSV\sapphirerapids

cd C:\PythonSV\pontevecchio
git init
git pull https://gitlab.devtools.intel.com/pythonsv-projects/pontevecchio/pontevecchio

cd C:\PythonSV\sapphirerapids
git init
git pull https://gitlab.devtools.intel.com/pythonsv-projects/sapphirerapids/sapphirerapids
