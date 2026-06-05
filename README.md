# Freelance Monitor Bot

Python bot for Windows: monitors freelance job boards via RSS and sends new listings to Telegram.

**Full guide (English + Русский):** [`INSTRUCTION.md`](INSTRUCTION.md)

## Features

- Checks every 5 minutes (configurable in `.env`)
- FL.ru, Freelancer.com, optional RemoteOK & We Work Remotely
- **English UI by default** — language picker on first `/start`, change anytime with `/language`
- First-run wizard: filters + “new only” mode
- SQLite deduplication, anti-spam limits
- SOCKS proxy for Telegram and foreign RSS (auto-detected from VPN)

## Quick start

1. Install Python 3.10+ from https://www.python.org/downloads/ (**Add to PATH**)
2. Unzip project → run `install.bat`
3. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`
4. Enable VPN if needed → `start_bot.bat`
5. In Telegram: choose language → complete setup wizard

## Build ZIP for release

```bat
make_archive.bat
```

Creates `FreelanceMonitor-bot.zip` without `.env`, database, or `.venv`.

## Security

Do not publish: `.env`, `config.yaml`, `data/`, `.venv/`

---

## Русский

Бот мониторит FL.ru, Freelancer.com и др. → уведомления в Telegram.

**Инструкция:** [`INSTRUCTION.md`](INSTRUCTION.md) (English + Русский)

- Интерфейс по умолчанию на **английском**, язык при первом `/start` или команда **`/language`**
- VPN нужен для Telegram (и для зарубежных RSS в РФ)
- Архив: `make_archive.bat`
