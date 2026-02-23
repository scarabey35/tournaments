import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    JSON_SORT_KEYS = False

   
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  #

    
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  
        "pool_recycle": 280,     
    }


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    )

    SQLALCHEMY_ECHO = True  


class ProductionConfig(Config):
    DEBUG = False

   
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }
