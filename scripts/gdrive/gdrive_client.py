"""
Google Drive Client - Ограничен достъп до конкретна папка
Четене и писане на файлове САМО в определена Google Drive папка
"""

import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from config import GDRIVE_FOLDER_ID, SCOPES, CREDENTIALS_FILE


class GDriveClient:
    """Client за работа с Google Drive - ограничен до конкретна папка"""

    def __init__(self):
        """Инициализация на клиента с Service Account credentials"""
        self.folder_id = GDRIVE_FOLDER_ID
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Автентикация с Service Account"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                CREDENTIALS_FILE,
                scopes=SCOPES
            )
            self.service = build('drive', 'v3', credentials=credentials)
            print(f"✓ Успешна автентикация с Google Drive")
            print(f"✓ Достъп ограничен до папка: {self.folder_id}")
        except FileNotFoundError:
            raise Exception(
                f"Credentials файлът не е намерен: {CREDENTIALS_FILE}\n"
                "Моля, следвай инструкциите в SETUP.md за създаване на Service Account."
            )
        except Exception as e:
            raise Exception(f"Грешка при автентикация: {str(e)}")

    def list_files(self, folder_id=None, recursive=False):
        """
        Листва файлове в папката

        Args:
            folder_id: ID на папката (по подразбиране главната папка)
            recursive: Дали да включи подпапки

        Returns:
            List of files
        """
        if folder_id is None:
            folder_id = self.folder_id

        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, modifiedTime, size)",
                orderBy="name"
            ).execute()

            files = results.get('files', [])

            if recursive:
                all_files = files.copy()
                for file in files:
                    if file['mimeType'] == 'application/vnd.google-apps.folder':
                        subfolder_files = self.list_files(file['id'], recursive=True)
                        all_files.extend(subfolder_files)
                return all_files

            return files

        except HttpError as e:
            raise Exception(f"Грешка при листване на файлове: {str(e)}")

    def download_file(self, file_id, destination_path):
        """
        Изтегля файл от Drive

        Args:
            file_id: ID на файла
            destination_path: Локален път за запис
        """
        try:
            request = self.service.files().get_media(fileId=file_id)

            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            with io.FileIO(destination_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"  Download: {int(status.progress() * 100)}%")

            print(f"✓ Изтеглен: {destination_path}")

        except HttpError as e:
            raise Exception(f"Грешка при изтегляне на файл: {str(e)}")

    def upload_file(self, local_path, parent_folder_id=None, update_existing=True):
        """
        Качва файл в Drive папката

        Args:
            local_path: Локален път до файла
            parent_folder_id: ID на родителската папка (по подразбиране главната)
            update_existing: Дали да update-ва съществуващ файл със същото име

        Returns:
            File ID
        """
        if parent_folder_id is None:
            parent_folder_id = self.folder_id

        filename = os.path.basename(local_path)

        try:
            # Проверка дали файлът вече съществува
            existing_file = None
            if update_existing:
                query = f"name='{filename}' and '{parent_folder_id}' in parents and trashed=false"
                results = self.service.files().list(q=query, fields="files(id, name)").execute()
                files = results.get('files', [])
                if files:
                    existing_file = files[0]

            media = MediaFileUpload(local_path, resumable=True)

            if existing_file:
                # Update съществуващ файл
                file = self.service.files().update(
                    fileId=existing_file['id'],
                    media_body=media
                ).execute()
                print(f"✓ Обновен: {filename}")
            else:
                # Създаване на нов файл
                file_metadata = {
                    'name': filename,
                    'parents': [parent_folder_id]
                }
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, name'
                ).execute()
                print(f"✓ Качен: {filename}")

            return file.get('id')

        except HttpError as e:
            raise Exception(f"Грешка при качване на файл: {str(e)}")

    def create_folder(self, folder_name, parent_folder_id=None):
        """
        Създава папка в Drive

        Args:
            folder_name: Име на папката
            parent_folder_id: ID на родителската папка

        Returns:
            Folder ID
        """
        if parent_folder_id is None:
            parent_folder_id = self.folder_id

        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }

            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name'
            ).execute()

            print(f"✓ Създадена папка: {folder_name}")
            return folder.get('id')

        except HttpError as e:
            raise Exception(f"Грешка при създаване на папка: {str(e)}")

    def delete_file(self, file_id):
        """
        Изтрива файл от Drive (премества в кошчето)

        Args:
            file_id: ID на файла
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"✓ Изтрит файл: {file_id}")
        except HttpError as e:
            raise Exception(f"Грешка при изтриване: {str(e)}")

    def get_folder_info(self):
        """Информация за главната папка"""
        try:
            folder = self.service.files().get(
                fileId=self.folder_id,
                fields="id, name, createdTime, modifiedTime"
            ).execute()
            return folder
        except HttpError as e:
            raise Exception(f"Грешка при получаване на информация: {str(e)}")


if __name__ == "__main__":
    # Тестов пример
    try:
        client = GDriveClient()

        # Информация за папката
        info = client.get_folder_info()
        print(f"\nПапка: {info['name']}")
        print(f"ID: {info['id']}")

        # Листване на файлове
        print("\nФайлове в папката:")
        files = client.list_files()
        if files:
            for f in files:
                print(f"  - {f['name']} ({f['mimeType']})")
        else:
            print("  (празна)")

    except Exception as e:
        print(f"Грешка: {str(e)}")
