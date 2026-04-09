# github-backup

Скачивает репозитории, отмеченные звёздами на GitHub (README или zip-архивы).
При повторном запуске файлы обновляются только если репозиторий менялся после последней загрузки — уже актуальные архивы пропускаются.

- **`git_backup.py`** — основной скрипт
- **`git_back.sh`** — быстрый запуск полного цикла (активирует окружение и запускает скрипт)

## Установка

```bash
python -m venv env
env\Scripts\activate        # Windows
# source env/bin/activate   # Linux / macOS
pip install -r requirements.txt
```

## Настройка

Скопируйте `.env.example` в `.env` и заполните своими данными:

```bash
cp .env.example .env
```

```
privateToken = ghp_ваш_токен_здесь
userName = ваш_логин
```

### Получение токена

1. Перейдите на [github.com/settings/tokens](https://github.com/settings/tokens)
2. Нажмите **Generate new token → Tokens (classic)**
3. Укажите название, выберите срок действия
4. Отметьте право **`read:user`** — достаточно для доступа к списку звёзд
5. Для скачивания **приватных** репозиториев дополнительно отметьте **`repo`**
6. Нажмите **Generate token** и скопируйте значение в `.env`

> `.env` добавлен в `.gitignore` — токен не попадёт в репозиторий.

## git_backup.py — звёздные репозитории

### 1. Обновить список

Загружает актуальный список из GitHub и сохраняет в `stars.txt`:

```bash
python git_backup.py update-list
```

### 2. Скачать README каждого репозитория

Сохраняет файлы в `storage/` в формате `owner_repo_branch.md`.
Уже существующий файл пропускается, если репозиторий не обновлялся:

```bash
python git_backup.py readme
```

### 3. Скачать zip-архивы исходного кода

Сохраняет архивы в `storage/` в формате `owner_repo_branch.zip`.
Уже существующий архив пропускается, если репозиторий не обновлялся:

```bash
python git_backup.py zip
```

### Типичный сценарий

```bash
python git_backup.py update-list   # обновить список звёзд
python git_backup.py zip           # скачать / обновить архивы
```

## git_back.sh — быстрый запуск

Активирует виртуальное окружение и последовательно выполняет полный цикл бэкапа:

```bash
bash git_back.sh
```

Эквивалентно:

```bash
python git_backup.py update-list
python git_backup.py readme
python git_backup.py zip
```
