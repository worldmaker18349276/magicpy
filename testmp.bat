cd MagicPartModule
rcc -binary resources.qrc -o resources.rcc
cd ..
rd "C:\FreeCAD\Mod\MagicPart" /s /q
xcopy "MagicPartModule" "C:\FreeCAD\Mod\MagicPart" /s /i
start C:\FreeCAD\bin\FreeCAD.exe -M %cd%