# Freelance Monitor Bot

Python bot for Windows: monitors freelance job boards via RSS and sends new listings to Telegram.

**Full guide (English + Русский):** [`INSTRUCTION.md`](INSTRUCTION.md)
<img width="486" height="474" alt="4platform" src="https://github.com/user-attachments/assets/ea2eedf7-5cda-44c3-b7ba-d084eb38576a" />
<img width="486" height="474" alt="3platform" src="https://github.com/user-attachments/assets/1a27da63-f694-40d2-9db7-0de4d5144c20" />
<img width="455" height="429" alt="2platform" src="https://github.com/user-attachments/assets/27b57546-1b4b-4b22-a19e-c9f0a15f6389" />
<img width="493" height="463" alt="1platform" src="https://github.com/user-attachments/assets/4c063cd8-3f3a-4dd5-8928-69e90867664d" />
<img width="493" height="444" alt="5platform" src="https://github.com/user-attachments/assets/f60278a9-dfc8-41b5-b462-ecf6afedb229" />

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
