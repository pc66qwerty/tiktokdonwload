@echo off
echo Instalando PyInstaller...
pip install pyinstaller

echo Compilando bot.py a .exe...
pyinstaller --onefile --name "DessstikBot" --icon NONE --add-data ".env;." bot.py

echo.
echo Listo! El ejecutable esta en: dist\DessstkBot.exe
echo Copia tambien el archivo .env a la misma carpeta que el .exe
pause
