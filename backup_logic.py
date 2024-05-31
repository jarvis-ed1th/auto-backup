import os
from datetime import datetime, timedelta


def backup(path, src, destination, excluded_folders, backup_name):
    # Obtenir le code de date actuel
    date_code = datetime.now().strftime("%Y-%m-%d")
    # Nom du dossier de sauvegarde
    backup_folder = os.path.join(destination, f"{date_code}-{backup_name}")

    # Vérifier si le dossier de sauvegarde existe déjà
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    # Chemin du fichier batch
    batch_file_path = os.path.join(path, 'backup.bat')
    file_to_save = os.path.join(path, 'save.txt')
    file_to_exclude = os.path.join(path, 'exclude.txt')

    with open(file_to_save, 'w') as save_file:
        for folder in src:
            save_file.write(f'{folder}\n'.replace('/', '\\'))

    with open(file_to_exclude, 'w') as exclude_file:
        for folder in excluded_folders:
            exclude_file.write(f'{folder}\n'.replace('/', '\\'))

    # Écrire le contenu dans le fichier batch
    with open(batch_file_path, 'w') as batch_file:
        batch_file.write('@echo off\n')
        batch_file.write('setlocal EnableDelayedExpansion\n')
        batch_file.write(f'set "destination={destination}"\n')

        batch_file.write(f'''
for /f "tokens=*" %%e in ({file_to_exclude}) do (
    set "excludeList=!excludeList! %%e"
)


for /f "tokens=*" %%i in ({file_to_save}) do (
    set "source=%%i"
    for %%j in ("!source!") do set foldername=%%~nxi
''')
        batch_file.write(
            fr'robocopy "!source!" "{backup_folder}\!folderName!" /E /COPY:DAT /XD !excludeList! /R:0 /W:0\n)')

    # Exécuter le fichier batch
    os.system(batch_file_path)


def check_auto_backup(backup_frequency, backup_folder):
    # Vérifier le type de sauvegarde automatique
    if backup_frequency == "daily":
        days_to_subtract = 1
    elif backup_frequency == "weekly":
        days_to_subtract = 7
    elif backup_frequency == "monthly":
        days_to_subtract = 30
    else:
        return False

    # Calculer la date limite pour la sauvegarde automatique
    cutoff_date = datetime.now() - timedelta(days=days_to_subtract)
    cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")

    # Vérifier s'il existe un dossier avec une date trop récente
    for folder in os.listdir(backup_folder):
        if folder.endswith(f"-auto-backup"):
            folder_date = folder[:10]  # Récupérer la partie de la date dans le nom du dossier
            if folder_date > cutoff_date_str:
                return False
    return True


def auto_backup(path, frequency, history, src, destination, exclusion):
    if check_auto_backup(frequency, destination):
        backup(path, src, destination, exclusion, "auto-backup")
    keep_recent_backups(os.path.join(path, 'delete.bat'), destination, history)


def force_backup(path, src, destination, exclusion):
    backup(path, src, destination, exclusion, "backup")


def keep_recent_backups(path, destination, history):
    # Obtenir la liste des dossiers de sauvegarde automatique
    backup_folders = [folder for folder in os.listdir(destination) if folder.endswith("-auto-backup")]

    # Trier les dossiers par date de création (du plus récent au plus ancien)
    backup_folders.sort(key=lambda folder: datetime.strptime(folder[:10], "%Y-%m-%d"), reverse=True)

    # Conserver uniquement les x plus récents
    folders_to_keep = backup_folders[:history]

    # Supprimer les dossiers non retenus
    for folder in backup_folders:
        if folder not in folders_to_keep:
            batch_automation(path, os.path.join(destination, folder))


def batch_automation(path, directory):
    # Créer le contenu du fichier batch
    batch_content = f'@echo off\nrd /s /q "{directory}"\nif exist "{directory}"'

    # Chemin du fichier batch
    batch_file_path = path

    # Écrire le contenu dans le fichier batch
    with open(batch_file_path, 'w') as batch_file:
        batch_file.write(batch_content)

    # Exécuter le fichier batch
    os.system(batch_file_path)

    # Supprimer le fichier batch
    os.remove(batch_file_path)
