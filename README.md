# HoyoSignIn
Daily automatic check-in tool for HoYoverse games with Telegram notifications.

## Contents

- [About](#about)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Windows](#windows)
  - [Linux](#linux)
- [Security](#security)
- [What's New in Version 2.0](#whats-new-in-version-20)
- [Contributing](#contributing)
- [License](#license)

## About

This is an enhanced version of the tool for automatic daily check-ins in HoYoverse games (Genshin Impact, Honkai: Star Rail, Honkai Impact 3rd, Tears of Themis, Zenless Zone Zero) with notifications via Telegram.

The project is intended for self-hosting on your PC or Cloud/VPS.

Supports Windows and Linux.

## Features

- ✅ Support for all HoYoverse games (Genshin, HSR, HI3, ToT, ZZZ)
- ✅ Multiple account support
- ✅ **Individual Telegram notifications for each account**
- ✅ **Secure secret storage with validation**
- ✅ **Modern Telegram notifications with HTML formatting**
- ✅ Proxy configuration (reduces chance of getting captcha)
- ✅ Professional code architecture with type hints
- ✅ Backward compatibility with old configurations

## Prerequisites

- Python 3.10 or higher
- Git (for cloning the repository)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/TFBosoN/HoyoSighIn
cd HoyoSighIn
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### 1. Create `.env` file

Copy the configuration example (if `.env.example` exists) or create a new `.env` file in the project root.

### 2. Configure Telegram bot (optional, but recommended)

1. Create a bot via [@BotFather](https://t.me/BotFather) in Telegram
2. Get the bot token
3. Get your Chat ID:
   - Send a message to [@userinfobot](https://t.me/userinfobot) or [@RawDataBot](https://t.me/RawDataBot)
   - Copy your `id` from the response

Add to `.env`:
```env
BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 3. Configure accounts

#### New Format (Recommended) - with individual notifications

For each account, add:

```env
# Account 1
ACCOUNT_12345_COOKIES=account_id=12345;cookie_token=xxx;ltoken=xxx;ltuid=12345;mi18nLang=ru-ru;_MHYUUID=xxx
ACCOUNT_12345_TELEGRAM_CHAT_ID=987654321
ACCOUNT_12345_ENABLED_GAMES=Genshin,HSR,HI3

# Account 2
ACCOUNT_67890_COOKIES=account_id=67890;cookie_token=yyy;ltoken_v2=yyy;ltuid_v2=67890;mi18nLang=en-us;_MHYUUID=yyy
ACCOUNT_67890_TELEGRAM_CHAT_ID=123456789
ACCOUNT_67890_ENABLED_GAMES=HSR,ZZZ
```

**Parameters:**
- `ACCOUNT_<ID>_COOKIES` - required field, cookie string
- `ACCOUNT_<ID>_TELEGRAM_CHAT_ID` - optional, Chat ID for individual notifications (if not specified, `TELEGRAM_CHAT_ID` is used)
- `ACCOUNT_<ID>_ENABLED_GAMES` - optional, comma-separated list of games (default: all games)

#### Old Format (for backward compatibility)

You can use the old format for quick migration:

```env
OS_COOKIE_Genshin=cookie1@cookie2@cookie3
OS_COOKIE_HSR=cookie1@cookie2
```

### 4. How to get cookies

1. Open browser and go to https://act.hoyolab.com
2. Log in to your account
3. Navigate to the daily rewards page for the desired game
4. Open developer tools (F12)
5. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
6. Find **Cookies** → `https://act.hoyolab.com`
7. Copy values from the following fields:
   - `account_id`
   - `cookie_token`
   - `ltoken` or `ltoken_v2`
   - `ltuid` or `ltuid_v2`
   - `mi18nLang`
   - `_MHYUUID`
8. Assemble the string in the format:
   ```
   account_id=xxx;cookie_token=xxx;ltoken=xxx;ltuid=xxx;mi18nLang=ru-ru;_MHYUUID=xxx
   ```

Detailed guide: https://am-steph.github.io/wayscript-login-helper/

### 5. Additional settings (optional)

```env
# User Agent (default is used if not specified)
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0

# Proxy (optional)
USE_PROXY=true
PROXY_DATA=username:password@127.0.0.1:1080
```

## Usage

### Windows

#### Manual execution

Run `run.bat` or execute:
```bash
python -m src.checkin
```

#### Automatic execution via Task Scheduler

1. Open **Task Scheduler**
2. Create a **Basic Task**
3. Give it a name (e.g., "HoyoSignIn Daily")
4. Select trigger **Daily**
5. Choose start time (servers reset at 16:00 UTC)
6. Select action **Start a program**
7. In "Program or script" field, specify: `C:\<Path>\<to>\<project>\run.bat`
8. In "Start in" field, specify: `C:\<Path>\<to>\<project>`
9. Click **Finish**

### Linux

#### Manual execution

Run `run.sh` or execute:
```bash
python3 -m src.checkin
```

#### Automatic execution via cron

1. Make `run.sh` executable:
```bash
chmod +x run.sh
```

2. Open crontab editor:
```bash
crontab -e
```

3. Add entry (example to run every day at 3:00 AM):
```bash
0 3 * * * /path/to/HoyoSignIn/run.sh
```

## Security

⚠️ **IMPORTANT:**
- **NEVER** commit `.env` file to git!
- Keep cookies secure
- Do not share your cookies with others
- Regularly update cookies (they may expire)

The `.env` file is already added to `.gitignore` to protect your data.

## What's New in Version 2.0

- 🔒 **Secure secret storage** with Pydantic validation
- 👤 **Individual notifications** for each account in Telegram
- 📱 **Enhanced Telegram notifications** with HTML formatting
- 🏗️ **Professional architecture** with type hints and modular structure
- 📦 **Updated dependencies** to latest versions
- ♻️ **Backward compatibility** with old configurations

## Contributing

We welcome contributions to the project! Please:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under [GNU GPLv3](LICENSE.md).
