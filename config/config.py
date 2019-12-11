_all__ = [
    'DevelopmentConfig',
    'ProductionConfig',
    'get_config'
]


class Config:
    HOST = '127.0.0.1'
    PORT = 3030
    API_HOST = 'http://localhost'
    API_VERSION = 'v1'
    API_BASE_PATH = 'api/{}'.format(API_VERSION)
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'ThisIsNotASecret'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    SECRET_KEY = 'ThisIsNotASecret'


def get_config(env):
    switch = {
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }
    return switch[env]
