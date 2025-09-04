import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    # Prefer DATABASE_URL; otherwise use instance database if present; fallback to project DB
    _db_url_env = os.environ.get('DATABASE_URL')
    _instance_db_path = os.path.join(basedir, 'instance', 'aurora_motors.db')
    _project_db_path = os.path.join(basedir, 'aurora_motors.db')
    if _db_url_env:
        SQLALCHEMY_DATABASE_URI = _db_url_env
    elif os.path.exists(_instance_db_path):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + _instance_db_path
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + _project_db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

    # DigitalOcean Spaces / S3-compatible storage
    SPACES_BUCKET = os.environ.get('SPACES_BUCKET')
    SPACES_REGION = os.environ.get('SPACES_REGION')
    SPACES_ENDPOINT_URL = os.environ.get('SPACES_ENDPOINT_URL')  # e.g. https://nyc3.digitaloceanspaces.com
    SPACES_ACCESS_KEY_ID = os.environ.get('SPACES_ACCESS_KEY_ID')
    SPACES_SECRET_ACCESS_KEY = os.environ.get('SPACES_SECRET_ACCESS_KEY')
    SPACES_CDN_BASE_URL = os.environ.get('SPACES_CDN_BASE_URL')  # optional CDN base
    
    # Pagination
    POSTS_PER_PAGE = int(os.environ.get('POSTS_PER_PAGE') or 10)
    
    # Application
    APP_NAME = os.environ.get('APP_NAME') or 'Aurora Motors'
    APP_URL = os.environ.get('APP_URL') or 'http://localhost:5000'
    
    # Webhooks
    PAY_ADVANTAGE_WEBHOOK_SECRET = os.environ.get('PAY_ADVANTAGE_WEBHOOK_SECRET')
    
    # Xero Configuration
    XERO_CLIENT_ID = os.environ.get('XERO_CLIENT_ID')
    XERO_CLIENT_SECRET = os.environ.get('XERO_CLIENT_SECRET')
    XERO_CALLBACK_URL = os.environ.get('XERO_CALLBACK_URL') or 'http://localhost:5000/xero/callback'
    XERO_SCOPES = [
        'openid',
        'profile',
        'email',
        'accounting.transactions',
        'accounting.contacts',
        'accounting.settings',
        'offline_access'
    ]


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Use DATABASE_URL if provided; otherwise inherit from base (instance SQLite if present)
    _db_url_env = os.environ.get('DATABASE_URL')
    if _db_url_env:
        SQLALCHEMY_DATABASE_URI = _db_url_env.replace('postgres://', 'postgresql://', 1) if _db_url_env.startswith('postgres://') else _db_url_env


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}