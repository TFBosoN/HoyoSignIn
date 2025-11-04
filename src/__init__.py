"""
HoyoSignIn - Automatic signin tool for HoYoverse games
"""
__version__ = '2.0.0'

import checkin as checkin

if __name__ == '__main__':
    manager = checkin.CheckInManager()
    manager.run_all()