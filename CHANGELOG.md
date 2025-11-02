# Changelog

## [2.0.0] - 2025

### Added
- 🔒 **Secure secret storage** with Pydantic validation
- 👤 **Individual Telegram notifications** for each account
- 📱 **Enhanced Telegram notifications** with HTML formatting
- 🏗️ **Professional architecture** with type hints and modular structure
- 📦 **Updated dependencies** (pydantic, pydantic-settings)
- 📝 **Comprehensive documentation** in README and MIGRATION.md

### Changed
- Code structure refactoring: separated into modules (`config.py`, `http_client.py`, `notify.py`, `sign.py`, `checkin.py`)
- Improved configuration system with support for new format
- Enhanced error handling and logging
- Updated execution method: `python -m src.checkin` instead of direct script execution

### Compatibility
- ✅ Full backward compatibility with old configurations
- ✅ Old format `OS_COOKIE_*` still works
- ✅ Old variables `BOT_API` and `BOT_CHAT` are supported

### Security Improvements
- Configuration validation through Pydantic
- Secure loading of environment variables
- Validation of required fields in cookies

### New Configuration Examples

**New format with individual notifications:**
```env
ACCOUNT_12345_COOKIES=cookie_string
ACCOUNT_12345_TELEGRAM_CHAT_ID=individual_chat_id
ACCOUNT_12345_ENABLED_GAMES=Genshin,HSR
```

**Old format (still works):**
```env
OS_COOKIE_Genshin=cookie1@cookie2
BOT_API=token
BOT_CHAT=chat_id
```
