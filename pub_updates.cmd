@echo off
color 0A

title Обновление проекта
echo Pub updates

git add .
git commit -m "Update: %date% %time%"
git push origin main

echo.
echo Обновление завершено!
timeout /t 3 /nobreak > nul