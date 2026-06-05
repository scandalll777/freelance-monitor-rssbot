# Freelance Monitor Bot — User Guide

**English** · [Русский](#русский)

---

## English

### What this bot does

Monitors freelance job boards via RSS and sends **new listings** to your Telegram:

- FL.ru, Freelancer.com (optional: RemoteOK, We Work Remotely)
- Checks every **5 minutes** (configurable)
- **No duplicates** — seen jobs are stored in SQLite
- **English UI by default** — choose language on first `/start` (saved in SQLite DB)
- Foreign listings can be auto-translated when Russian is selected

> **VPN required in Russia** for Telegram API. FL.ru RSS works without VPN; Freelancer and other foreign feeds use the same SOCKS proxy as Telegram.

### Quick start (5 steps)

1. Unzip the archive, e.g. `C:\FL-bot\`
2. Run **`install_python.bat`** → download Python 3.10+ from python.org (**Add to PATH**)
3. Run **`install.bat`**
4. Create a bot in @BotFather → put token and Chat ID in **`.env`**
5. Enable **VPN** → run **`start_bot.bat`** → in Telegram choose **language** and complete setup

### First launch in Telegram

1. Bot sends **language picker** — **English** is default (🇬🇧 English / 🇷🇺 Русский)
2. **Step 1:** choose FL.ru categories and enable sources
3. **Step 2:** **New only** (recommended) or **Send current listings**
4. Change language anytime: command **`/language`** or **🌐 Language** in `/menu`

### Files

| File | Purpose |
|------|---------|
| `install_python.bat` | Opens python.org download page |
| `install.bat` | Installs dependencies, creates `.env` |
| `start_bot.bat` | Runs the bot |
| `setup_filters.bat` | Filter window (FL.ru categories) |
| `reset_database.bat` | Clears seen jobs database |
| `.env` | Bot token and Chat ID |
| `config.yaml` | Filters and RSS feeds |

### `.env` example

```env
TELEGRAM_BOT_TOKEN=1234567890:AA...
TELEGRAM_CHAT_ID=987654321
CHECK_INTERVAL_SECONDS=300
INITIAL_SEED=false
TRANSLATE_FOREIGN=true
```

### Telegram commands

| Command | Action |
|---------|--------|
| `/start` | Language + setup wizard (first time) or menu |
| `/menu` | Settings menu |
| `/language` | Change interface language (EN / RU) |
| `/help` | Same as `/menu` |

### VPN / proxy

Telegram API may be blocked. The bot auto-detects SOCKS from VPN (often `127.0.0.1:10808`).

Optional in `.env`:

```env
TELEGRAM_PROXY=socks5://127.0.0.1:10808
```

### Troubleshooting

- **No messages** — enable VPN, check token/Chat ID, send `/start`
- **Python not found** — reinstall with **Add to PATH**
- **Spam of old jobs** — use **Apply + reset DB** in menu or `reset_database.bat`
- **Menu not responding** — keep `start_bot.bat` window open

---

## Русский

### Что делает бот

Мониторит фриланс-площадки по RSS и присылает **новые заказы** в Telegram:

- FL.ru, Freelancer.com (опционально: RemoteOK, We Work Remotely)
- Проверка каждые **5 минут**
- **Без дублей** — база SQLite
- **Интерфейс на английском по умолчанию** — язык выбирается при первом `/start`
- При выборе русского — автоперевод зарубежных объявлений
- Язык сохраняется в базе SQLite — при следующем запуске уже выбран

> **VPN обязателен в России** для Telegram. FL.ru — без VPN; Freelancer и др. — через SOCKS-прокси (бот подхватывает автоматически).

### Быстрый старт (5 шагов)

1. Распакуйте архив, например `C:\FL-bot\`
2. **`install_python.bat`** → скачайте Python 3.10+ (галочка **Add to PATH**)
3. **`install.bat`**
4. Создайте бота в @BotFather → токен и Chat ID в **`.env`**
5. **VPN** → **`start_bot.bat`** → в Telegram выберите **язык** и пройдите настройку

### Первый запуск в Telegram

1. Бот предложит **выбрать язык** (🇬🇧 English / 🇷🇺 Русский), по умолчанию — English
2. **Шаг 1:** разделы FL.ru и источники
3. **Шаг 2:** **Только новые** (рекомендуется) или **Прислать текущие**
4. Сменить язык: команда **`/language`** или **🌐 Язык** в `/menu`

### Файлы

| Файл | Назначение |
|------|------------|
| `install_python.bat` | Открывает python.org |
| `install.bat` | Установка зависимостей |
| `start_bot.bat` | Запуск бота |
| `setup_filters.bat` | Окно фильтров FL.ru |
| `reset_database.bat` | Сброс базы заказов |
| `.env` | Токен и Chat ID |
| `config.yaml` | Фильтры и RSS |

### Пример `.env`

```env
TELEGRAM_BOT_TOKEN=1234567890:AA...
TELEGRAM_CHAT_ID=987654321
CHECK_INTERVAL_SECONDS=300
INITIAL_SEED=false
TRANSLATE_FOREIGN=true
```

### Команды Telegram

| Команда | Действие |
|---------|----------|
| `/start` | Язык + мастер настройки или меню |
| `/menu` | Меню настроек |
| `/language` | Сменить язык интерфейса (EN / RU) |
| `/help` | То же, что `/menu` |

### VPN / прокси

При необходимости в `.env`:

```env
TELEGRAM_PROXY=socks5://127.0.0.1:10808
```

### Частые проблемы

- **Сообщения не приходят** — VPN, токен, Chat ID, `/start`
- **Python не найден** — переустановите с **Add to PATH**
- **Спам старых заказов** — **Применить + сброс базы** или `reset_database.bat`
- **Меню не отвечает** — окно `start_bot.bat` должно быть открыто
