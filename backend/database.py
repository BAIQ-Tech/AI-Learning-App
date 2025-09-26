import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Determine database URL based on environment
if os.getenv('DATABASE_URL'):
    # Production - use PostgreSQL
    SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL').replace(
        'postgres://', 'postgresql://', 1
    )
    logger.info("Using PostgreSQL database")
else:
    # Development - use SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    logger.info("Using SQLite database")

# Create engine with optimized settings
if "postgresql" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

# Add connection event listeners for PostgreSQL
if "postgresql" in SQLALCHEMY_DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_postgresql_connection_params(dbapi_connection, connection_record):
        """Set PostgreSQL connection parameters"""
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SET timezone TO 'UTC'")
            cursor.execute("SET statement_timeout = '30s'")
