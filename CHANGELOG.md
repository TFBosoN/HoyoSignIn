# Changelog

## [2.1.0] - 2026-05-31

### Added
- 🌐 **Per-channel SOCKS5 proxy** — `USE_PROXY_SIGNIN` and `USE_PROXY_TELEGRAM` let you route game sign-in API calls and Telegram notifications through the proxy independently

### Fixed
- `run.bat` was not capturing Python log output (`2>&1` was missing, so `stderr` was dropped from `last_job.log`)
- Cookie validator now accepts `ltoken_v2` in addition to `ltoken`
- Fixed `src/__init__.py` import so the package entry point works correctly

### Changed
- `HttpClient` now accepts a `proxy=` dict directly instead of reading config internally — cleaner separation of concerns
- `AppSettings` and `ProxyConfig` are now cached singletons (parsed once at startup instead of on every request)
- Removed unused `run_check_in()` compatibility stub from `checkin.py`

### Compatibility
- ✅ `USE_PROXY=true` still works as a shortcut that enables proxy for both channels

---

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
- Launcher scripts (`run.bat` / `run.sh`) now add a random startup delay and log all output to `last_job.log`

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
