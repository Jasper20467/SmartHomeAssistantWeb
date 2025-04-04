class LocalConfig(Config):
    DEBUG = True
    TESTING = False
    DATABASE_URI = 'sqlite:///demo_db.sqlite'
