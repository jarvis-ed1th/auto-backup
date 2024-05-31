@echo off
setlocal EnableDelayedExpansion

:: Définir le répertoire de destination
set "destination=C:\Users\hourl\Documents\ARCHIVES\00_SAVES\CLOUD_AUTOSAVE"

:: Définir le chemin du fichier contenant les dossiers à sauvegarder
set "foldersFile=%destination%\DirToSave.txt"

:: Définir le chemin du fichier contenant les dossiers à exclure
set "excludeFile=%destination%\DirToExclude.txt"

:: Obtenir la date actuelle au format YYMMDD
for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /value') do (
    set datetime=%%a
)

:: Extraire les parties de la date
set year=!datetime:~2,2!
set month=!datetime:~4,2!
set day=!datetime:~6,2!

:: Afficher la date au format YYMMDD
set date=!year!!month!!day!

:: Créer le dossier de sauvegarde YYMMDD_SAVE
mkdir "%destination%\!date!_SAVE" >> "%destination%\backup_log.txt" 2>&1

:: Lire le fichier contenant les dossiers à exclure
if exist "%excludeFile%" (
    for /f "tokens=*" %%e in (%excludeFile%) do (
        set "excludeList=!excludeList! %%e"
    )
)

:: Lire le fichier contenant les dossiers à sauvegarder
for /f "tokens=*" %%i in (%foldersFile%) do (
    :: Obtenir le nom du dossier source
    set "source=%%i"
    for %%j in ("!source!") do set foldername=%%~nxi

    :: Copier le dossier dans le dossier de sauvegarde YYMMDD_SAVE
    robocopy "!source!" "%destination%\!date!_SAVE\!foldername!" /E /COPY:DAT /XD !excludeList! /R:0 /W:0 >> "%destination%\backup_log.txt" 2>&1

    :: Vérifier si la copie a réussi
    if !errorlevel! geq 8 (
        echo !source! : echec >> "%destination%\backup_log.txt" 2>&1
    ) else (
        echo !source! : done >> "%destination%\backup_log.txt" 2>&1
    )
)

:: Supprimer les dossiers plus anciens dans le répertoire de destination
cd /d "%destination%"
for /f "tokens=*" %%a in ('dir /b /ad /o-d *_SAVE') do (
    set /a count+=1
    if !count! gtr 3 (
        echo %%a deleted >> "%destination%\backup_log.txt" 2>&1
        rd /s /q "%%a"
    )
)