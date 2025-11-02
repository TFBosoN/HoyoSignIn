# Migration Guide from version 1.x to 2.0

This guide will help you upgrade from version 1.x to 2.0 of HoyoSignIn.

## Major Changes

### 1. New Dependencies

The project now uses Pydantic for configuration validation:
- `pydantic==2.9.2`
- `pydantic-settings==2.5.2`

**Action:** Run `pip install -r requirements.txt` to update dependencies.

### 2. New Configuration System

The old configuration system is still supported, but it's recommended to migrate to the new one.

#### Old Format (still works):

```env
OS_COOKIE_Genshin=cookie1@cookie2
OS_COOKIE_HSR=cookie1@cookie2
BOT_API=your_token
BOT_CHAT=your_chat_id
```

#### New Recommended Format:

```env
# General Telegram settings
BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=default_chat_id

# Account 1 with individual settings
ACCOUNT_12345_COOKIES=cookie_string
ACCOUNT_12345_TELEGRAM_CHAT_ID=individual_chat_id
ACCOUNT_12345_ENABLED_GAMES=Genshin,HSR

# Account 2
ACCOUNT_67890_COOKIES=cookie_string
ACCOUNT_67890_TELEGRAM_CHAT_ID=another_chat_id
ACCOUNT_67890_ENABLED_GAMES=HSR,ZZZ
```

### 3. Individual Telegram Notifications

Now each account can have its own Chat ID for notifications.

**Benefits:**
- Separate notifications for each account
- Ability to configure different Telegram chats for different accounts
- If individual Chat ID is not specified, the default one is used

### 4. Enhanced Notifications

Notifications now use HTML formatting for better readability:
- Bold text for headers
- Italic for date
- Monospace font for details
- More structured format

### 5. Code Structure Changes

- New module `src/config.py` - configuration management
- New module `src/http_client.py` - HTTP client
- Updated `src/notify.py` - enhanced notifications
- Updated `src/checkin.py` - new check-in manager

### 6. Execution Method

The script now runs as a module:
- Before: `python ./src/checkin.py`
- After: `python -m src.checkin`

The `run.bat` and `run.sh` files are already updated.

## Step-by-Step Migration

### Step 1: Update Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Update Configuration (optional)

You can continue using the old format, but to get all the benefits of the new version, it's recommended to migrate to the new format.

**Minimal changes to start using new features:**

1. Rename `BOT_API` to `BOT_TOKEN` (optional, old format still works)
2. Rename `BOT_CHAT` to `TELEGRAM_CHAT_ID` (optional, old format still works)
3. Add individual Chat IDs for accounts if needed

### Step 3: Test

Run manually to verify:
```bash
python -m src.checkin
```

### Step 4: Update Automated Execution

If you use Task Scheduler (Windows) or cron (Linux), make sure:
- In Task Scheduler, the path is correctly set: `C:\<Path>\<to>\<project>\run.bat`
- Working directory is set: `C:\<Path>\<to>\<project>`
- In cron, the path to `run.sh` is correct

## Backward Compatibility

Version 2.0 is **fully backward compatible** with the old configuration. You can continue using:
- Old format `OS_COOKIE_*`
- Old variables `BOT_API` and `BOT_CHAT`
- Old cookie structure

Everything will work as before, but you won't get the benefits of new features.

## Troubleshooting

If you encounter issues during migration:
1. Check logs in `last_job.log`
2. Make sure all dependencies are installed
3. Verify cookie format is correct
4. Ensure `.env` file is in the project root
