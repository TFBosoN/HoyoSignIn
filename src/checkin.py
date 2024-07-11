import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Common Settings
from settings import log, config
from notify import Notify
from sign import Sign


def run_check_in(game_name, CONFIG):
    notify = Notify()
    msg_list = ""
    ret = success_num = fail_num = 0

    OS_COOKIE = ''
    token = ''

    if os.getenv('OS_COOKIE_'+game_name, '') != '':
        OS_COOKIE = os.getenv('OS_COOKIE_'+game_name)
    else:
        log.error(f"{game_name} Cookie not set, skipping.")
        return

    cookie_list = OS_COOKIE.split('@')
    log.info(f'Number of {game_name} account cookies read: {len(cookie_list)}')

    for i in range(len(cookie_list)):
        log.info(f'Preparing {game_name} NO.{i + 1} Account Check-In...')
        try:
            token = cookie_list[i].split('cookie_token=')[1].split(';')[0]
            msg = Sign(cookie_list[i], CONFIG).run()
            msg_list += msg
            success_num = success_num + 1
        except IndexError:
            cookie_values = ["account_id","cookie_token","ltoken","ltuid","mi18nLang","_MHYUUID"]
            for j in cookie_values:
                if not(j in cookie_list[i]):
                    log.error(f'{j} not found')
            fail_num = fail_num + 1
            ret = -1
            log.info(f"\n\n{game_name} Check-In: Try these troubleshooting steps and grab the cookie again:\n -Log out and log back in\n -Ensure you are on the Daily Rewards page and not the HoyoLab Forums page\n -Try incognito mode\n -Try clearing your browser history/cache\n -Try using another browser\n")
        except Exception as e:
            if not token:
                log.error(f"{game_name} Check-In: Cookie token not found, please try to relog on the check-in page.")

            msg = f'{game_name} Check-In NO.{i + 1} Account:\n {e}'
            msg_list += msg
            fail_num = fail_num + 1
            log.error(msg)
            ret = -1

    total_num = success_num + fail_num
    msg_list = str(datetime.today().strftime('%d.%m.%Y')) + '\n' + msg_list
    notify.send(status=f'{game_name} Helper\n{success_num}/{total_num} succeeded', msg=msg_list)

    if ret != 0:
        log.error(f'{game_name} Helper: Program terminated with errors')

if __name__ == '__main__':
    for game, game_config in config.items():
        run_check_in(game, game_config)
