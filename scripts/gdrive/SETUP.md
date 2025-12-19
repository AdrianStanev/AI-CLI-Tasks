# Google Drive Integration - Ръководство за настройка

Интеграция с **ограничен достъп** само до конкретна Google Drive папка.

## 🔒 Сигурност

- ✅ Достъп **само** до папка: `1RUBSnmMaOrrrvr6vR4H9PffkSrKIHnGg`
- ✅ Service Account НЕ МОЖЕ да достъпи други файлове във твоя Drive
- ✅ Credentials се съхраняват локално и НЕ се commit-ват в Git

---

## Стъпка 1: Създаване на Google Cloud Project

1. Отвори [Google Cloud Console](https://console.cloud.google.com/)
2. Кликни **"Create Project"** или избери съществуващ проект
3. Дай име на проекта, например: `personal-ai-assistant`
4. Кликни **"Create"**

---

## Стъпка 2: Активиране на Google Drive API

1. В Cloud Console, отвори **"APIs & Services" > "Library"**
2. Търси **"Google Drive API"**
3. Кликни върху него и натисни **"Enable"**

---

## Стъпка 3: Създаване на Service Account

1. Отвори **"APIs & Services" > "Credentials"**
2. Кликни **"Create Credentials" > "Service Account"**
3. Попълни:
   - **Service account name**: `ai-assistant-drive`
   - **Service account ID**: (генерира се автоматично)
4. Кликни **"Create and Continue"**
5. **Role**: Избери `Basic > Owner` или остави празно (не е нужно за нашата употреба)
6. Кликни **"Continue"** и после **"Done"**

---

## Стъпка 4: Създаване на Credentials Key

1. В **"Credentials"** страницата, намери създадения Service Account
2. Кликни върху Service Account-а
3. Отиди на таб **"Keys"**
4. Кликни **"Add Key" > "Create new key"**
5. Избери **JSON** формат
6. Кликни **"Create"**
7. JSON файлът ще се изтегли автоматично

---

## Стъпка 5: Настройка на Credentials

1. Преименувай изтегления JSON файл на `credentials.json`
2. Премести го в папката `scripts/gdrive/`:
   ```bash
   mv ~/Downloads/your-project-xxxxx.json scripts/gdrive/credentials.json
   ```

3. **ВАЖНО**: Отвори `credentials.json` и намери **Service Account email** адреса.
   Изглежда така: `ai-assistant-drive@your-project.iam.gserviceaccount.com`

---

## Стъпка 6: Споделяне на Google Drive папката

1. Отвори Google Drive папката: https://drive.google.com/drive/folders/1RUBSnmMaOrrrvr6vR4H9PffkSrKIHnGg
2. Кликни **"Share"** (Споделяне) или десен бутон > Share
3. В полето **"Add people and groups"** въведи **Service Account email-а** от стъпка 5
4. Избери права: **Editor** (за четене и писане)
5. **ВАЖНО**: Изключи "Notify people" (не е нужно да изпращаш имейл на бота)
6. Кликни **"Share"**

🔒 **Сигурност**: Service Account има достъп **САМО** до тази папка! Дори кодът да се опита да достъпи други файлове, няма да може.

---

## Стъпка 7: Инсталиране на Python Dependencies

```bash
cd scripts/gdrive
pip install -r requirements.txt
```

Или с virtual environment (препоръчително):
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## Стъпка 8: Тестване

```bash
# Провери връзката и покажи файловете в папката
python3 sync.py list

# Качи локални файлове в Google Drive
python3 sync.py upload

# Изтегли файлове от Google Drive локално
python3 sync.py download
```

---

## Употреба

### Листване на файлове в Drive
```bash
python3 sync.py list
```

### Качване на локални файлове в Drive
```bash
python3 sync.py upload

# Или с конкретна папка
python3 sync.py upload --path /path/to/folder
```

### Изтегляне от Drive
```bash
python3 sync.py download

# Или в конкретна локална папка
python3 sync.py download --path /path/to/folder
```

---

## Програмна употреба (Python код)

```python
from gdrive_client import GDriveClient

# Инициализация
client = GDriveClient()

# Листване на файлове
files = client.list_files()
for f in files:
    print(f['name'])

# Качване на файл
client.upload_file('README.md')

# Създаване на папка
folder_id = client.create_folder('my-notes')

# Качване във подпапка
client.upload_file('notes.md', parent_folder_id=folder_id)

# Изтегляне
client.download_file(file_id='xxxxx', destination_path='local-file.md')
```

---

## Структура на файловете

```
scripts/gdrive/
├── config.py              # Конфигурация (folder ID, scopes)
├── gdrive_client.py       # Основен клас за работа с Drive
├── sync.py                # CLI инструмент за синхронизация
├── requirements.txt       # Python dependencies
├── SETUP.md              # Това ръководство
├── credentials.json       # Service Account credentials (НЕ commit-вай!)
└── .gitignore            # Игнорира credentials.json
```

---

## Често задавани въпроси

### Може ли кодът да достъпи други файлове във моя Drive?
**НЕ!** Service Account има достъп САМО до споделената папка. Това е гарантирано от Google Drive permissions системата.

### Какво се случва ако изтрия credentials.json?
Ще трябва да създадеш нов Service Account key от Google Cloud Console (стъпки 4-6).

### Мога ли да променя папката?
Да! Промени `GDRIVE_FOLDER_ID` в `config.py` и сподели новата папка със Service Account.

### Как да автоматизирам синхронизацията?
Можеш да добавиш cron job (Linux/Mac) или Task Scheduler (Windows):
```bash
# Всеки час качва промени
0 * * * * cd /path/to/AI-CLI-Tasks/scripts/gdrive && python3 sync.py upload
```

---

## Troubleshooting

### "Credentials файлът не е намерен"
- Уверете се, че `credentials.json` е в `scripts/gdrive/`
- Проверете пътя в `config.py`

### "403 Forbidden"
- Service Account няма достъп до папката
- Провери дали си споделил папката със Service Account email-а (стъпка 6)

### "Module not found"
- Инсталирай dependencies: `pip install -r requirements.txt`

---

## Безопасност

- ✅ `credentials.json` е в `.gitignore` - НЕ се commit-ва
- ✅ Service Account има минимални права
- ✅ Достъп ограничен до една папка
- ⚠️ НЕ споделяй `credentials.json` публично!

---

Готово! Сега имаш сигурна интеграция с Google Drive! 🎉
