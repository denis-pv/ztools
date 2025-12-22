@echo off
color 0A

title Обновление проекта без загрузки на github
echo Pub updates

:choice
echo.
echo Выберите способ создания комментария коммита:
echo 1 - Автоматически (дата и время)
echo 2 - Ввести комментарий вручную
echo 3 - Ввести лог изменений	
echo 0 - Выход
echo.
set /p choice="Выберите пункт: "

if "%choice%"=="1" goto auto_commit
if "%choice%"=="2" goto manual_commit
if "%choice%"=="3" goto log
if "%choice%"=="0" exit 0

echo Неверный выбор! Попробуйте снова.
goto choice

:auto_commit
set commit_message="Update: %date% %time%"
goto commit

:manual_commit
echo.
set /p commit_message="Введите комментарий для коммита: "
if "%commit_message%"=="" (
    echo Комментарий не может быть пустым!
    goto manual_commit
)
set commit_message="%commit_message%"

:commit
git add .
git commit -m %commit_message%
rem git push origin main
exit 0

:log 	
echo.
echo Лог изменений (20 кранийх записей):
git log --oneline -n 20
echo.
goto choice

echo.
echo Обновление завершено!
timeout /t 5 /nobreak > nul