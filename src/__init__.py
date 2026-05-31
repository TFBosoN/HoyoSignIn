"""
HoyoSignIn - Automatic signin tool for HoYoverse games
"""
__version__ = '2.0.0'

if __name__ == '__main__':
    try:
        from .checkin import CheckInManager
    except ImportError:
        from checkin import CheckInManager

    CheckInManager().run_all()
