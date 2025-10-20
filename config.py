"""Configuration module for Flask application."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Flask application."""

    # PostgreSQL configuration
    DB_USER = os.getenv('POSTGRES_USER', 'admin')
    DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'adminpass')
    DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    DB_PORT = os.getenv('POSTGRES_PORT', '5432')
    DB_NAME = os.getenv('POSTGRES_DB', 'database')

    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = (
        f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}'
        f'@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '8080'))

    @classmethod
    def get_database_uri(cls):
        """Get database URI for connection."""
        return cls.SQLALCHEMY_DATABASE_URI

    @classmethod
    def is_debug_mode(cls):
        """Check if debug mode is enabled."""
        return cls.DEBUG
