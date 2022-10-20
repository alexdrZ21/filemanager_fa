import manager
from usr import usr_stor

if __name__ == '__main__':
    manag = manager.multiple_user(
        usr_stor('users.json'),
        size=100
    ).settings()

    manag.authentication()
    manag.start()
