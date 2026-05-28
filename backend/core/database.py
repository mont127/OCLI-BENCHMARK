from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Create the database file path in the parent directory
db_path = os.path.join(os.path.dirname(current_dir), "app.db")

# Create the database engine
engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for our models
Base = declarative_base()