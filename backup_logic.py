import os
import subprocess
from datetime import datetime, timedelta


def backup(destination_folder, source_folders, excluded_folders, backup_name, history, progress_window, callback):
    # Création du chemin d'accès du dossier avec la date de la sauvegarde
    backup_date = datetime.now().strftime('%Y-%m-%d')
    backup_destination = os.path.join(destination_folder, f"{backup_date}-{backup_name}")

    # Création du répertoire de sauvegarde s'il n'existe pas
    os.makedirs(backup_destination, exist_ok=True)

    # Construction de la liste des répertoires à exclure
    exclude_str = " ".join([f'"{excluded_folder}"' for excluded_folder in excluded_folders]).replace("/", "\\")

    # Exécution de la commande robocopy pour chaque source
    for folder in source_folders:
        folder_name = os.path.basename(folder)
        target = os.path.join(backup_destination, folder_name)
        os.makedirs(target, exist_ok=True)

        command = (f'robocopy "{folder.replace("/", "\\")}" "{target.replace("/", "\\")}" '
                   f'/E /COPY:DAT /XD {exclude_str} /R:0 /W:0')
        subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)

    # Call de la fonction qui termine la sauvegarde
    callback(progress_window, backup_name, destination_folder, history)


def check_auto_backup(backup_frequency, destination_folder):
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
    for folder in os.listdir(destination_folder):
        if folder.endswith(f"-auto-backup"):
            folder_date = folder[:10]  # Récupérer la partie de la date dans le nom du dossier
            if folder_date > cutoff_date_str:
                return False
    return True


def keep_recent_backups(destination_folder, backup_history):
    # Obtenir la liste des dossiers de sauvegarde automatique
    backup_folders = [folder for folder in os.listdir(destination_folder) if folder.endswith("-auto-backup")]

    # Trier les dossiers par date de création (du plus récent au plus ancien)
    backup_folders.sort(key=lambda folder: datetime.strptime(folder[:10], "%Y-%m-%d"), reverse=True)

    # Conserver uniquement les x plus récents
    folders_to_keep = backup_folders[:backup_history]

    # Supprimer les dossiers non retenus
    for folder in backup_folders:
        if folder not in folders_to_keep:
            delete_old_folders(os.path.join(destination_folder, folder))


def delete_old_folders(folder_to_delete):
    # Contenu de la commande et exécution
    batch_content = f'rd /s /q "{folder_to_delete.replace('/', '\\')}"'
    subprocess.run(batch_content, shell=True)
