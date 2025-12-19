"""
Google Drive Integration Configuration
Конфигурация за достъп само до конкретна папка
"""

# ID на папката в Google Drive (от URL-а)
GDRIVE_FOLDER_ID = "1RUBSnmMaOrrrvr6vR4H9PffkSrKIHnGg"

# Scopes - ограничени разрешения
# 'drive.file' - достъп само до файлове създадени от приложението
# За пълен достъп до споделената папка използваме 'drive'
SCOPES = ['https://www.googleapis.com/auth/drive']

# Път до Service Account credentials файл
# ВАЖНО: Този файл НЕ трябва да се commit-ва в Git!
CREDENTIALS_FILE = 'scripts/gdrive/credentials.json'

# Локална папка за синхронизация
LOCAL_SYNC_PATH = '.'

# Файлове и папки за игнориране при синхронизация
IGNORE_PATTERNS = [
    '.git',
    '.gitignore',
    '__pycache__',
    '*.pyc',
    'scripts/gdrive/credentials.json',
    'scripts/gdrive/token.json'
]
