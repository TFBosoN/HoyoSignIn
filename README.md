# HoyoSignIn
Daily sign in tool for Mihoyo games.

## Contents

- [About](#about)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
	- [Windows](#windows)
	- [Linux](#linux)
- [Contributing](#contributing)
- [License](#license)

## About
This is a remake of original [Genshin Impact Check-In Helper](https://am-steph.github.io/wayscript-login-helper/) modified to complete daily logins for Hoyo games with notification for Telegram.
Intended for self-hosting.
Can be setup for Windows or Linux.

## Features
- Supports all Hoyo games
- Supports multiple accounts and per game configuration
- Add your own proxy (makes less of a chance to get captcha, probably)
- Optional notifications via Telegram with beautiful status messages

## Prerequisites
- Git
- Python 3.10 (with added `PATH` variable for Windows)

## Installation
Copy the project to your desired location
```bash
git clone https://github.com/TFBosoN/HoyoSighIn
cd HoyoSighIn
pip install -r requirements.txt
```

## Configuration

1. Rename `.env.example` to `.env`
2. Fill environment variables:
	- Hoyolab cookie: Complete guide on how to get `OS_COOKIE` is described at https://am-steph.github.io/wayscript-login-helper/ 
	- Telegram (optional): Fill variables `BOT_API` and `BOT_CHAT` with bot token and chat id accordingly
	- User Agent (optional): If you want to update User Agent to the one you're using replace `USER_AGENT` variable with [this](https://www.google.ru/search?ie=UTF-8&q=what%27s%20my%20user%20agent)
> [!IMPORTANT]
> You need to specify which of the games to do checkin in by providing it in corresponding field.
> 
> For example, fill `OS_COOKIE_HSR` if you want to do only HSR daily checkings.
3. Change the settings in `settings.py`
	- if you wish to add more games in the future with the same daily loging mechanic you can add another game and it's endpoints.
	
## Usage

### Windows

Setup Task Scheduler auto-run method on Windows

1. Open `Task Scheduler`
2. Make a `Basic Task`, give it a name
3. Select `Daily`
4. Choose any prefered `Start` time. (NOTE: checkin servers reset 4PM UTC, choose runtime accordingly)
5. Select `Start program` and choose `run.bat` file in your project folder
6. Click `Finish`

### Linux

Setup crontab auto-run method on Linux

1. Make `run.sh` executable
```bash
chmod +x run.sh
```
2. Open crontab editor
```bash
crontab -e
```
3. Add a new record
```bash
0 3 * * * /path/to/your/hoyosign/directory/run.sh
```
This will run your script every day at 3AM.

## Contributing

Feel free to open pull requests to contribute to the project

## License

This project is licensed under the [GNU GPLv3] - see the LICENSE.md file for details.
