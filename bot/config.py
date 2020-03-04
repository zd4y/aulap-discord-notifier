import os


class Config:
    USERNAME = os.environ.get('AULAP_USERNAME')
    PASSWORD = os.environ.get('AULAP_PASSWORD')
    DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')


try:
    assert Config.USERNAME and Config.PASSWORD and Config.DISCORD_TOKEN
except AssertionError:
    print('Error: Missing username, password, discord token or database uri')
    print('Please set an environment variable for each of these:')
    print('  AULAP_USERNAME')
    print('  AULAP_PASSWORD')
    print('  DISCORD_TOKEN')
    exit()
