#!/usr/bin/env python3
"""
Google Drive Sync - Синхронизация между локална папка и Google Drive
"""

import os
import sys
import argparse
from pathlib import Path
from gdrive_client import GDriveClient
from config import LOCAL_SYNC_PATH, IGNORE_PATTERNS


def should_ignore(path, ignore_patterns):
    """Проверява дали файл/папка трябва да се игнорира"""
    path_str = str(path)
    for pattern in ignore_patterns:
        if pattern in path_str or path_str.endswith(pattern.replace('*', '')):
            return True
    return False


def upload_local_to_drive(client, local_root=LOCAL_SYNC_PATH):
    """
    Качва всички локални файлове в Google Drive

    Args:
        client: GDriveClient instance
        local_root: Локална папка за синхронизация
    """
    print(f"\n📤 Качване на файлове от '{local_root}' в Google Drive...\n")

    uploaded_count = 0
    skipped_count = 0

    for root, dirs, files in os.walk(local_root):
        # Премахваме игнорирани директории от търсенето
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), IGNORE_PATTERNS)]

        # Определяме родителската папка в Drive
        rel_path = os.path.relpath(root, local_root)
        if rel_path == '.':
            parent_id = client.folder_id
        else:
            # TODO: Създаване на подпапки в Drive
            parent_id = client.folder_id

        # Качване на файлове
        for filename in files:
            local_file = os.path.join(root, filename)

            if should_ignore(local_file, IGNORE_PATTERNS):
                skipped_count += 1
                continue

            try:
                client.upload_file(local_file, parent_id)
                uploaded_count += 1
            except Exception as e:
                print(f"✗ Грешка при качване на {filename}: {str(e)}")

    print(f"\n✓ Качени: {uploaded_count} файла")
    print(f"⊘ Игнорирани: {skipped_count} файла")


def download_drive_to_local(client, local_root=LOCAL_SYNC_PATH):
    """
    Изтегля всички файлове от Google Drive локално

    Args:
        client: GDriveClient instance
        local_root: Локална папка за запис
    """
    print(f"\n📥 Изтегляне на файлове от Google Drive в '{local_root}'...\n")

    try:
        files = client.list_files(recursive=True)

        downloaded_count = 0

        for file in files:
            # Пропускаме папки
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                continue

            # Google Docs, Sheets, etc. пропускаме засега
            if file['mimeType'].startswith('application/vnd.google-apps'):
                print(f"⊘ Пропуснат Google Doc: {file['name']}")
                continue

            local_path = os.path.join(local_root, file['name'])

            try:
                client.download_file(file['id'], local_path)
                downloaded_count += 1
            except Exception as e:
                print(f"✗ Грешка при изтегляне на {file['name']}: {str(e)}")

        print(f"\n✓ Изтеглени: {downloaded_count} файла")

    except Exception as e:
        print(f"✗ Грешка: {str(e)}")


def list_drive_files(client):
    """Показва всички файлове в Drive папката"""
    print(f"\n📂 Файлове в Google Drive папка:\n")

    try:
        info = client.get_folder_info()
        print(f"Папка: {info['name']}")
        print(f"ID: {info['id']}\n")

        files = client.list_files(recursive=True)

        if not files:
            print("(Папката е празна)\n")
            return

        folders = [f for f in files if f['mimeType'] == 'application/vnd.google-apps.folder']
        regular_files = [f for f in files if f['mimeType'] != 'application/vnd.google-apps.folder']

        if folders:
            print("📁 Папки:")
            for folder in folders:
                print(f"  └─ {folder['name']}/")
            print()

        if regular_files:
            print("📄 Файлове:")
            for file in regular_files:
                size = file.get('size', 'N/A')
                if size != 'N/A':
                    size_kb = int(size) / 1024
                    size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
                else:
                    size_str = "N/A"
                print(f"  └─ {file['name']} ({size_str})")
            print()

    except Exception as e:
        print(f"✗ Грешка: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Google Drive Sync - Синхронизация с ограничен достъп до конкретна папка'
    )
    parser.add_argument(
        'action',
        choices=['upload', 'download', 'list'],
        help='upload: качва локални файлове | download: изтегля от Drive | list: показва файлове'
    )
    parser.add_argument(
        '--path',
        default=LOCAL_SYNC_PATH,
        help='Локална папка за синхронизация'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🔒 Google Drive Sync - Ограничен достъп")
    print("=" * 60)

    try:
        client = GDriveClient()

        if args.action == 'upload':
            upload_local_to_drive(client, args.path)
        elif args.action == 'download':
            download_drive_to_local(client, args.path)
        elif args.action == 'list':
            list_drive_files(client)

        print("\n✓ Готово!\n")

    except Exception as e:
        print(f"\n✗ Грешка: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
